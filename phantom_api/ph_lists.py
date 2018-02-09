import json
from phantom_api import ph_base
from phantom_api import ph_consts

#List Based Methods
import copy

class ph_list(object):
    """Facilitates the creation and manipulation of lists

    Args:
        name (string): name of list
    
    Keyword Args:
        id (int): set after save is called, or can be set manually.
        content (list): list of phantom list content i.e. ([[col 1, col2, col3], [col1, col2, col3]])

    """
    
    def __init__(
        self,
        name,
        id=None,
        content=None
    ):
        self.name = name
        self.content = content
        self.id = None

    def _list_exists(self):
        found = True
        response = self.get_list(self.name)

        if not response:
            found = False

        return found

    def save(self, overwrite=True):
        """Saves list to phantom

        Keyword Args:
            overwrite (bool): Defaults to True. If true will overrite existing list data.
        
        Raises:
            Exception: [description]
            Exception: [description]
        
        Returns:
            [type]: [description]
        """

        list_exists = self._list_exists()
        if not overwrite and list_exists:
            raise Exception('Cannot create list - ' + self.name + ' - because it already exists.')
        else:
            if list_exists:
                response = ph_base._send_request(
                    '/rest/decided_list/' + self.name,
                    'post',
                    payload=json.dumps(self.format_list_json()),
                    content_type='application/json'
                )
            else:
                if not list_exists:
                    response = ph_base._send_request(
                        '/rest/decided_list',
                        'post',
                        payload=json.dumps(self.format_list_json()),
                        content_type='application/json'
                    )

        if ph_consts.LIST_SUCCESS_KEY not in response:
            raise Exception(
                'Error saving list with name - ' + self.name + '. ' 
                + response[ph_consts.LIST_FAILED_MESSAGE_KEY]
            )
        elif ph_consts.LIST_NEW_ID in response:
            self.id = response[ph_consts.LIST_NEW_ID]
        
        return True

    def update_list(self, append_data=None, delete_rows=None, update_rows=None):
        """Update an existing list

        Keyword Args:
            append_data (list): Data to append ``[[col1, col2, col3], [col1, col2, col3]]``
            delete_rows (list): List of rows to delete
            update_rows (dict): Dict where keys are row numbers and values are column data in list format.
        
        Raises:
            Exception: Exception if you try to append data,  but the columns in your data don't match the number of columns in the list
            Exception: Exception if you try to delete row that doesn't exist
            Exception: Exception if you try to update a row that doesn't exist or there is a mismatch in column count.
            Exception: Exception if updating the list fails.
        
        Returns:
            bool: True if successfully saved.
        """

        if self.content:
            if append_data and len(self.content[0]) != len(append_data[0]):
                raise Exception(
                    'The data you are trying to add to the list - ' + self.name + ' - does not '
                    + 'have the same number of columns as the list. Append Data Columns - '
                    + str(len(append_data[0])) + ' vs List Data Columns - '
                    + str(len(self.content[0]))
                )
            if delete_rows and any([row_num > len(self.content)-1 for row_num in delete_rows]):
                raise Exception(
                    'You are trying to delete a row_number that does not exists in the list - '
                    + self.name + '.'
                )
            if(
                update_rows and(
                    any(
                        [int(row_num) > len(self.content)-1 for row_num in update_rows.keys()]
                    ) 
                    or any(
                        [len(row_data) != len(self.content[0]) for row_data in update_rows.values()]
                    )
                )
            ):
                raise Exception(
                    'The data in the rows you are trying to update do no have the same number '
                    + 'of columns as the list - ' + self.name + ' - that you are trying to '
                    + 'update. List Data Columns - ' + str(len(self.content[0]))
                )

        update_json = {}
        if append_data:
            update_json['append_rows'] = append_data
        if delete_rows:
            update_json['delete_rows'] = delete_rows
        if update_rows:
            update_json['update_rows'] = update_rows

        response = ph_base._send_request(
            '/rest/decided_list/' + self.name,
            'POST', payload=json.dumps(update_json),
            content_type='application/json'
        )

        if(ph_consts.LIST_SUCCESS_KEY not in response):
            raise Exception(
                'Error updating list with name - ' + self.name + '. '
                + response[ph_consts.LIST_FAILED_MESSAGE_KEY]
            )

        return True

    def refresh(self):
        """Get current data from phantom.
        
        Returns:
            bool: returns True if successully refreshed data
        """

        self.content = ph_list.get_list(self.name, id=self.id).content
        
        return True

    def search_list(self, column_num, search_val, find_all=True):
        """Searches a list for data
        
        Args:
            column_num (int): Column number that you want searched - since there are no column names
            search_val (string: What to search for
            find_all (bool): Defaults to True. Stop at first match if False, or return all results.
        
        Raises:
            Exception: Exception if search column_num does not exist in list.
        
        Returns:
            list: returns list of found rows
        """

        if len(self.content[0]) < column_num:
            raise Exception(
                'Searching in column number - ' + column_num + ' but the list - ' 
                + self.name + ' has only ' + len(self.content[0]) 
                + ' columns.'
            )
        found_rows = []
        for row_num, record in enumerate(self.content):
            if search_val == record[column_num]:
                found_rows.append(row_num)
                if not find_all:
                    break

        return found_rows

    def format_list_json(self):
        list_json = {
            'name': self.name,
            'content': self.content
        }

        return list_json

    @classmethod
    def get_list(cls, list_name, id=None):
        """Get list data.
        
        Args:
            list_name (string): Name of phantom list to get
            id (int): Defaults to None. Id of phantom list.
        
        Raises:
            Exception: Exception if list is not found.
        
        Returns:
            ph_list: Returns found list.
        """

        retrieved_list = None

        response = ph_base._send_request(
            '/rest/decided_list/' + (list_name if list_name else str(id)) + '?_output_format=JSON',
            'get'
        )

        if 'failed' in response:
            if 'item not found' not in response['message']:
                raise Exception(
                    'Error reading from list - ' + list_name 
                    + '. Error: ' + response['message']
                )
        else:
            retrieved_list = ph_list(response['name'], content=response['content'], id=response['id'])

        return retrieved_list

    @classmethod
    def get_list_csv(cls, list_name, row_separator='%0A', field_separator=','):
        """Get list csv
        
        Args:
            list_name (string): name of list

        Keyword Args:
            row_separator (string): separator for rows - defaults to %0A
            field_separator (string): separator for fields defaults to ,
        
        Raises:
            Exception: [description]
        """

        retreived_csv = None
        
        response = ph_base._send_request(
            '/rest/decided_list/' + list_name + '/formatted_content?_output_format=csv&_rs=' 
            + row_separator + '&_fs=' + field_separator,
            'get'
        )

        if 'failed' in response:
            if 'item not found' not in response['message']:
                raise Exception(
                    'Error reading from list - ' + list_name 
                    + '. Error: ' + response['message']
                )
        else:
            retrieved_csv = response

        return retrieved_csv