from datetime import datetime
import json
from phantom_api import ph_base
from phantom_api import ph_consts

class ph_user(object):
    """Facilitates creation and manipulation of users in phantom.

    Keyword Args:
        username (string): name of user
        first_name (string): first name of user
        last_name (string): last name of user
        email (string): email of user
        title (string): title of user
        location (string): location of user
        time_zone (string): timezone of user
        is_ad_user (bool): determines if users is ad or local acount
        password (string): password of user
        roles (list): list of role ids to which the user will belong
        two_fa (bool): 2fa in place?
        two_fa_username (string): 2fa username
        user_id (int): id of user, set with ``save()``
        allowed_ips (list): list of allowed_ips for access
        automation_user (bool): is automation user?
    """

    def __init__(
        self,
        username=None,
        first_name=None,
        last_name=None,
        email=None,
        title=None,
        location=None,
        time_zone=None,
        is_ad_user=False,
        password=None,
        roles=[],
        two_fa=False,
        two_fa_username=None,
        user_id=None,
        allowed_ips=[],
        automation_user=False
    ):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.title = title
        self.location = location
        self.time_zone = time_zone
        self.is_ad_user = is_ad_user
        self.password = password
        self.roles = roles
        self.two_fa = two_fa
        self.two_fa_username = two_fa_username
        self.user_id = user_id
        self.allowed_ips = allowed_ips
        self.automation_user= automation_user

    def render_dictionary(self):
        """Returns dictionary representation of object that can easily be converted to json with ``json.loads``

        Returns:
            dict: dictionary representation of object
        """

        user_json = {}

        if self.username:
            user_json['username'] = self.username
        if self.first_name:
            user_json['first_name'] = self.first_name
        if self.last_name:
            user_json['last_name'] = self.last_name
        if self.email:
            user_json['email'] = self.email
        if self.title:
            user_json['title'] = self.title
        if self.location:
            user_json['location'] = self.location
        if self.time_zone:
            user_json['time_zone'] = self.time_zone
        if self.is_ad_user:
            user_json['is_ad_user'] = self.is_ad_user
        if self.password:
            user_json['password'] = self.password
        if self.roles:
            user_json['roles'] = self.roles
        if self.two_fa:
            user_json['2fa'] = self.two_fa
        if self.two_fa_username:
            user_json['two_fa_username'] = self.two_fa_username
        if self.allowed_ips:
            user_json['allowed_ips'] = self.allowed_ips
        if self.automation_user:
            user_json['type'] = 'automation'
        
        return user_json

    def save(self):
        """Saves user
        
        Sets user_id after successful save

        Raises:
            Exception: Exception if error saving user
        
        Returns:
            int: id of newly saved user
        """

        response = ph_base._send_request(
            '/rest/ph_user',
            'post',
            payload=json.dumps(self.render_dictionary()),
            content_type='application/json'
        )

        if ph_consts.USER_SUCCESS_KEY not in response:
            raise Exception(str(response)) #response[ph_consts.USER_FAILED_MESSAGE_KEY])
        
        self.user_id = response[ph_consts.USER_NEW_ID]

        return self.user_id

    def update(self, remove_roles=[], add_roles=[]):
        """Update an existing user

        Remove or add roles

        Keyword Args:
            remove_roles (list): list of role ids to remove
            add_roles (list): list of role ids to add
        
        Returns:
            dict: returns update user response json

        Example:
            Saving a user, then updating::
                
                user = ph_user(
                username='testerman',
                    first_name='test',
                    last_name='man',
                    email='test.test@test.com',
                    password='test password'
                )

                user.save()

                user.update(add_roles=[4,1])

        Notes:
            This should be used if you have already run save, or manually set the user_id attribute.
        """

        return ph_user.update_user(self.user_id, remove_roles, add_roles)

    @classmethod
    def update_user(cls, user_id, remove_roles=[], add_roles=[]):
        """Update an existing user

        Remove or add roles

        Args:
            user_id (int): id of the user

        Keyword Args:
            remove_roles (list): list of role ids to remove
            add_roles (list): list of role ids to add

        Returns:
            dict: returns update user response json

        Example:
            Update a user with user id of 15::

                ph_user.update_user(user_id=15, remove_roles=[4])

        Notes:
            This should be used if you have not run ``save()`` but already know the user id
        """

        update_json = {
            'add_roles': add_roles,
            'remove_roles': remove_roles
        }

        response = ph_base._send_request(
            '/rest/ph_user/' + str(user_id),
            'post',
            payload=json.dumps(update_json),
            content_type='application/json'
        )

        return response

class ph_role(object):
    """Facilitates the creation of roles

    Args:
        name (string): name of role
        description (string): descriptoin of role

    Keyword Args:
        permissions (list): list of dictionaries describing permissions (see phantom api doc for formatting)
        users (list): list of user ids for users to be in role
        role_id (int): id of role. set after ``save()`` is called.

    """

    def __init__(
        self,
        name,
        description,
        permissions=[],
        users=[],
        role_id=None
    ):
        self.name = name
        self.description = description
        self.permissions = permissions
        self.users = users
        self.role_id = role_id

    def render_dictionary(self):
        """Renders a dictionary representation of the object which can easily be converted to json with ``json.loads()``
        
        Returns:
            dict: dictionary representation of the object
        """

        role_json = {}

        if self.name:
            role_json['name'] = self.name
        if self.description:
            role_json['description'] = self.description
        if self.permissions:
            if(
                ph_base._exists_in_data_set('permission object', ph_consts.ROLE_PERMISSIONS, [permission['name'] for permission in self.permissions])
            ):
                role_json['permissions'] = self.permissions
        
        return role_json

    def save(self):
        """Saves the new role

        Sets role_id upon successful save
        
        Raises:
            Exception: Exception if fails to save role
        
        Example:
            Creating a new role an saving it::
            
                role = ph_role(
                    'Test Role',
                    'Testing role creation',
                    permissions=[
                        {
                            'name': 'containers',
                            'view': True,
                            'edit': False,
                            'delete': True
                        }
                    ]
                )

                role.save()

        Returns:
            int: id of new role. 
        """

        response = ph_base._send_request(
            '/rest/role',
            'post',
            payload=json.dumps(self.render_dictionary()),
            content_type='application/json'
        )

        if ph_consts.ROLE_SUCCESS_KEY not in response:
            raise Exception(response[ph_consts.ROLE_FAILED_MESSAGE_KEY])
        
        self.role_id = response[ph_consts.ROLE_NEW_ID]

        return self.role_id

    def update(self, add_users=[], remove_users=[], update_permissions=None):
        """Update role

        Keyword Args:
            add_users (list): list of user ids to add to role
            remove_users (list): list of users to remove from role.
            update_permission (list): dictionary of new permissions

        Notes:
            Use this if you have created this role with ``save()`` and the role_id is already set.
        """

        return ph_role.update_role(self.role_id, remove_users, add_users, update_permissions)

    @classmethod
    def update_role(cls, role_id, remove_users=[], add_users=[], update_permissions=None):
        """Update role

        Keyword Args:
            role_id (int): id of role
            add_users (list): list of user ids to add to role
            remove_users (list): list of users to remove from role.
            update_permission (list): dictionary of new permissions

        Notes:
            Use this for existing roles which you already know the ids of.
        """

        update_json = {
            'add_users': add_users,
            'remove_users': remove_users,
        }

        if update_permissions and ph_base._exists_in_data_set('permission object', ph_consts.ROLE_PERMISSIONS, [permission['name'] for permission in update_permissions]):
            update_json['update_permissions'] = update_permissions

        response = ph_base._send_request(
            '/rest/role/' + str(role_id),
            'post',
            payload=json.dumps(update_json),
            content_type='application/json'
        )

        return response
    
