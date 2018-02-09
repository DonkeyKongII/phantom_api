from datetime import datetime
import json
from phantom_api import ph_base
from phantom_api import ph_consts

class ph_container(object):
    """Facilitates saving and manipulating phantom containers.

    Args:
        label (string): label for container
        name (string): name of container
    
    Keyword Args:
        artifacts (list): list of dictionaries describing artifacts pertaining to this container. Easier to save container, and then save artifacts to it.
        asset_id (list): id of asset ingesting this container
        close_time (list): date of container close (isoformat)
        custom_fields (dict): dictionary of custom cef fields
        data (list): dictionary of custo mdata fields <- i'm not sure how to use this one
        description (string): description of container
        due_time (string): due date/time of container (isoformat)
        end_time (string): end date/time of container (isoformat)
        ingeset_app_id (int): id of app producing container
        kill_chain (string): kill_chain - see phanto api doc for valid values
        owner_id (string): id of owner
        run_automation (bool): defaults to false. Determines of automations should run on creation.
        sensitivity (string): describes sensitivity of conatiner. defaults to amber.
        severity (string): describes severity of container. defaults to medium..
        source_data_identifier (string): id from originating system (e.g. jira ticket id)
        start_time (string): date/time of start (isoformat)
        open_time (string): date/time of open (isoformat), defaults to now.
        status (string): status of container (new, open, or closed). Defaults to new
        tags (list): list of tags for container.

    Attributes:
        id (int): Id of container. Set after running ``save()``

    Example:
        Here is an extremely simple example of how to use this::

            container = ph_container('campaign', 'Test ingestion from api.')
            container.save() # saves the container
            print(container.id) # prints the id of newly saved container
    """

    def __init__(
        self,
        label,
        name,
        artifacts=[],
        asset_id=None,
        close_time=None,
        custom_fields={},
        data={},
        description='',
        due_time=None,
        end_time=None,
        ingest_app_id=None,
        kill_chain=None,
        owner_id=None,
        run_automation=False,
        sensitivity='amber',
        severity='medium',
        source_data_identifier=None,
        start_time=None,
        open_time=datetime.now().isoformat()[:23]+'Z',
        status='new',
        tags=[]
    ):
        self.label = label
        self.name = name
        self.artifacts = artifacts
        self.id = None
        self.asset_id = asset_id
        self.close_time = close_time
        self.custom_fields = custom_fields
        self.data = data
        self.description = description
        self.due_time = due_time
        self.end_time = end_time
        self.ingest_app_id = ingest_app_id
        if kill_chain and ph_base._exists_in_data_set('kill chain', ph_consts.KILL_CHAIN_LIST, kill_chain):
            self.kill_chain = kill_chain
        else:
            self.kill_chain = None
        self.owner_id = owner_id
        self.run_automation = run_automation
        if sensitivity and ph_base._exists_in_data_set('sensitivity', ph_consts.CONTAINER_SENSITIVITY, sensitivity):
            self.sensitivity = sensitivity
        else:
            self.sensitivity = None
        if severity and ph_base._exists_in_data_set('severity', ph_consts.ARTIFACT_SEVERITY, severity):
            self.severity = severity
        self.source_data_identifier = source_data_identifier
        self.start_time = start_time
        self.open_time = open_time
        if status and ph_base._exists_in_data_set('status', ph_consts.CONTAINER_STATUS, status):
            self.status = status
        self.tags = tags

    def save(self):
        """Saves container. 

        Sets the container's id. If container already exists, just sets id of object.
        
        Raises:
            Exception: Raises exception if container fails to save.
        
        Returns:
            dict: Returns a dict indicating if the container was saved and the new id. ``{'id': id_number, 'created', True_or_False}``
        """


        response = ph_base._send_request(
            '/rest/container',
            'post',
            payload=json.dumps(self.render_dictionary()),
            content_type='application/json'
        )

        if response.get(ph_consts.CONTAINER_FAILED_KEY) and ph_consts.CONTAINER_DUPLICATE_MESSAGE not in response[ph_consts.CONTAINER_FAILED_MESSAGE_KEY]:
            raise Exception(str(response)) #response[ph_consts.CONTAINER_FAILED_MESSAGE_KEY])

        self.id = response[ph_consts.CONTAINER_NEW_ID] if response.get(ph_consts.CONTAINER_NEW_ID) else response[ph_consts.CONTAINER_EXISTING_ID]

        container_results = {
            'id': self.id,
            'created': (ph_consts.CONTAINER_NEW_ID in response)
        }

        return container_results

    def render_dictionary(self):
        """Returns a dictionary representation of the object which could easily be converted to json with ``json.loads``
        
        Returns:
            dict: Returns a dictionary representation of object.
        """

        container_json = {
            'label': self.label,
            'name': self.name,
            'artifacts': self.artifacts,
            'custom_fields': self.custom_fields,
            'data': self.data,
            'description': self.description,
            'run_automation': self.run_automation,
            'tags': self.tags
        }

        if self.asset_id:
            container_json['asset_id'] = self.asset_id
        if self.close_time:
            container_json['close_time'] = self.close_time
        if self.due_time:
            container_json['due_time'] = self.due_time
        if self.end_time:
            container_json['end_time'] = self.end_time
        if self.ingest_app_id:
            container_json['ingest_app_id'] = self.ingest_app_id
        if self.kill_chain and ph_base._exists_in_data_set('kill chain', ph_consts.KILL_CHAIN_LIST, self.kill_chain):
            container_json['kill_chain'] = self.kill_chain
        if self.owner_id:
            container_json['owner_id'] = self.owner_id
        if self.severity and ph_base._exists_in_data_set('severity', ph_consts.ARTIFACT_SEVERITY, self.severity):
            container_json['severity'] = self.severity
        if self.sensitivity and ph_base._exists_in_data_set('sensitivity', ph_consts.CONTAINER_SENSITIVITY, self.sensitivity):
            container_json['sensitivity'] = self.sensitivity
        if self.source_data_identifier:
            container_json['source_data_identifier'] = self.source_data_identifier
        if self.start_time:
            container_json['start_time'] = self.start_time
        if self.open_time:
            container_json['open_time'] = self.open_time
        if self.status and ph_base._exists_in_data_set('status', ph_consts.CONTAINER_STATUS, self.status):
            container_json['status'] = self.status
        
        return container_json
    
    @classmethod
    def add_container_comment(cls, container_id, comment):
        """Used to add a comment to container.
        
        Args:
            container_id (int): id of container
            comment (string): comment to be saved
        
        Returns:
            dict: returns id of new comment and whether comment save succesfully (see ``save()`` for example)

        Example:
            Adding a comment to a container for which I already know the container id::

                ph_container.add_container_comment(1069, 'this is a comment')

        Notes:
            Use this if you have not created a container with ``save()`` and you already know a container id.
        """

        container_json = {
            'container_id': container_id,
            'comment': comment
        }

        response = ph_base._send_request(
            '/rest/container_comment',
            'POST',
            payload=json.dumps(container_json),
            content_type = 'application/json'
        )

        return cls._format_container_results(response, 'comment', container_id)

    def add_comment(self, comment):
        """Used to add a comment to container.
        
        Args:
            comment (string): comment to be saved
        
        Returns:
            dict: returns id of new comment and whether comment save succesfully (see ``save()`` for example)

        Example:
            Adding a comment to a container that I previously saved::

                container = ph_container('campaign', 'Test ingestion from api.')
                container.save()
                container.add_comment('first comment')

        Notes:
            Use this if you have created your conatainer with ``save()`` and the container ``id`` attribute has already been set.
        """

        return ph_container.add_container_comment(self.id, comment)


    @classmethod
    def add_container_note(cls, container_id, note_title, note_content, phase_id=None):
        """Add a note to a container
        
        Args:
            container_id (int): id of container
            note_title (string): title of note
            note_content (string): content of note

        Keyword Args:
            phase_id (string): Defaults to None. Phase to which this note belongs.
        
        Returns:
            dict: returns id of new note and whether comment save succesfully (see ``save()`` for example)

        Example:
            Saving a note to a container for which I already know the container id::

                ph_container.add_container_note(1052,'test note2', 'test note 2 title', 'test contents 2')

        Notes:
            Use this if you have not created a container with ``save()`` and you already know a container id.
        """

        container_json = {
            'container_id': container_id,
            'title': note_title,
            'content': note_content,
        }

        if phase_id:
            container_json['phase_id'] = phase_id

        response = ph_base._send_request(
            '/rest/container_note',
            'post',
            payload=json.dumps(container_json),
            content_type = 'application/json'
        )

        return cls._format_container_results(response, 'note', container_id)

    def add_note(self, note_title, note_content, phase_id=None):
        """Add a note to a container
        
        Args:
            note_title (string): title of note
            note_content (string): content of note
            
        Keyword Args:
            phase_id (string): Defaults to None. Phase to which this note belongs.
        
        Returns:
            dict: returns id of new note and whether comment save succesfully (see ``save()`` for example)

        Example:
            Adding a note to container after running ``save()``::

                container = ph_container('campaign', 'Test ingestion from api.')
                container.save()
                container.add_note('test note', 'note title', 'test contents')

        Notes:
            Use this if you have created your conatainer with ``save()`` and the container ``id`` attribute has already been set.    
        """

        return ph_container.add_container_note(self.id, note_title, note_content, phase_id)

    @classmethod
    def pin_to_container_hud(cls, container_id, message, pin_data, playbook_id=None, pin_type='data', pin_style=''):
        """Pin an item to the container HUD.
        
        Args:
            container_id (int): id of container
            message (string): message associated with this pin
            pin_data (string): data that is actually pinned
        
        Keyword Args:
            playbook_id ([type]): Defaults to None. Id of playbook associated with this HUD pin
            pin_type (string): Type of pin to create (determins how it is displayed. Defaults to data. Other options are card_small, card_medium, card_large.
            pin_style (string): Color of pin when using the card types. (white, purple, or red)
        
        Returns:
            dict: returns id of new note and whether comment save succesfully (see ``save()`` for example)
        
        Example:
            Pinning a purple card to the container hud for which I already know the container id::

                ph_container.pin_to_container_hud(1052, 'test message 2', '55', pin_type='card_large', pin_style='purple')

        Notes:
            Use this if you have not created a container with ``save()`` and you already know a container id.
        """

        pin_json = {
            'container_id': container_id,
            'message': message,
            'data': pin_data
        }

        if playbook_id:
            pin_json['playbook_id'] = playbook_id
        if pin_type and ph_base._exists_in_data_set('pin type', ph_consts.CONTAINER_PIN_TYPE, pin_type):
            pin_json['pin_type'] = pin_type
        if pin_style and ph_base._exists_in_data_set('pin style', ph_consts.CONTAINER_PIN_STYLE, pin_style):
            pin_json['pin_style'] = pin_style

        response = ph_base._send_request(
            '/rest/container_pin',
            'post',
            payload=json.dumps(pin_json),
            content_type='application/json'
        )

        return cls._format_container_results(response, 'hud pin', container_id)

    def pin_to_hud(self, message, pin_data, playbook_id=None, pin_type='data', pin_style=''):
        """Pin an item to the container HUD.
        
        Args:
            message (string): message associated with this pin
            pin_data (string): data that is actually pinned
        
        Keyword Args:
            playbook_id ([type]): Defaults to None. Id of playbook associated with this HUD pin
            pin_type (string): Type of pin to create (determins how it is displayed. Defaults to data. Other options are card_small, card_medium, card_large.
            pin_style (string): Color of pin when using the card types. (white, purple, or red)
        
        Returns:
            dict: returns id of new note and whether comment save succesfully (see ``save()`` for example)
        
        Example:
            Pinning a purple card to the container hud for which I already know the container id::

                container = ph_container('campaign', 'Test ingestion from api.')
                container.save()
                container.add_note('test note', 'note title', 'test contents')

        Notes:
            Use this if you have created your conatainer with ``save()`` and the container ``id`` attribute has already been set.   
        """
        
        return ph_container.pin_to_container_hud(self.id, message, pin_data, playbook_id=playbook_id, pin_type=pin_type, pin_style=pin_style)

    @classmethod
    def _format_container_results(cls, response, field_name, container_id):
        if ph_consts.CONTAINER_SUCCESS_KEY not in response or response[ph_consts.CONTAINER_SUCCESS_KEY] == False:
            raise Exception(
                'Error adding container ' + field_name + ' to container id - ' + str(container_id) + '. '
                + (response[ph_consts.CONTAINER_FAILED_MESSAGE_KEY] if response.get(ph_consts.CONTAINER_FAILED_MESSAGE_KEY) else '')
            )
        
        results = {
            'id': response[ph_consts.CONTAINER_NEW_ID],
            'created': (ph_consts.CONTAINER_SUCCESS_KEY in response and response[ph_consts.CONTAINER_SUCCESS_KEY])
        }

        return results

    @classmethod
    def retrieve_container_json(cls, id):
        """Get container data from phantom.

        Args:
            id (int): id of container

        Returns:
            dict: returns dictionary representation of the data
        """

        return ph_base._retrieve_single_instance('container', id)
    
    @classmethod
    def update_container(cls, id, container_data):
        """Update existing container's data

        Args:
            id (int): id of container

        Returns:
            dict: results of update
        """

        return ph_base._update_record('container', id, container_data)

    @classmethod
    def delete_container(cls, id):
        """Delete existing container
        
        Args:
            id (int): id of container
        
        Returns:
            dict: results of delete
        """

        return ph_base._delete_record('container', id)

class ph_artifact(object):
    """Facilitates the saving and manipulation of artifacts

    Args:
        cef (dict): cef data representation of artifact.
        container_id (int): id of container
        label (string): label of container
    
    Keyword Args:
        cef_types (dict): ``contains`` information for custom data types
        data (dict): custom data field
        description (string): desctiption of the artifact
        end_time (string): end date/time (isoformat) defaults to now
        ingest_app_id (int): id of the app the produced the artifact
        kill_chain (string): kill chain
        name (string): name of artifact
        owner_id (int): id of owner
        run_automation (bool): determines wether automation should be run on ingest. defaults to True
        severity (int): severity of artifact
        source_data_identifier (string): id from source system, defaults to '0'
        start_time (string): start date/time (isoformat) defaults to now
        tags (list): list of tags associated with artifact
        artifact_type (string): type of artifact

    Attributes:
        id (int): id of artifact set after ``save()`` is called.

    """
    def __init__(
        self,
        cef,
        container_id,
        label,
        cef_types={},
        description='',
        data={},
        end_time=datetime.now().isoformat()[:23]+'Z',
        ingest_app_id=None,
        kill_chain=None,
        name='',
        owner_id=None,
        run_automation=True,
        severity='medium',
        source_data_identifier=0,
        start_time=datetime.now().isoformat()[:23]+'Z',
        tags=[],
        artifact_type=''
    ):
        self.cef = cef
        self.id = None
        self.container_id = container_id
        self.label = label
        self.cef_types = cef_types
        self.description = description
        self.data = data
        self.end_time = end_time
        self.ingest_app_id = ingest_app_id
        if(kill_chain and ph_base._exists_in_data_set('kill chain', ph_consts.KILL_CHAIN_LIST, kill_chain)):
            self.kill_chain = kill_chain
        else:
            self.kill_chain = None
        self.name = name
        self.owner_id = owner_id
        self.run_automation = run_automation
        if(severity and ph_base._exists_in_data_set('severity', ph_consts.ARTIFACT_SEVERITY, severity)):
            self.severity = severity
        else:
            self.severity = None
        self.source_data_identifier=source_data_identifier
        self.start_time = start_time
        self.tags = tags
        self.artifact_type = artifact_type

    def render_dictionary(self):
        """Returns a dictionary representation of the object which could easily be converted to json with ``json.loads``
        
        Returns:
            dict: Returns a dictionary representation of object.
        """
        artifact_json = {
            'cef': self.cef,
            'container_id': self.container_id,
            'label': self.label,
            'end_time': self.end_time,
            'start_time': self.start_time,
            'source_data_identifier': self.source_data_identifier,
            'name': self.name,
            'tags': self.tags,
            'run_automation': self.run_automation,
            'type': self.artifact_type,
            'descriptoin': self.description
        }

        if self.severity and ph_base._exists_in_data_set('Artifact Severity', ph_consts.ARTIFACT_SEVERITY, self.severity):
            artifact_json['severity'] = self.severity
        if self.cef_types:
            artifact_json['cef_types'] = self.cef_types
        if self.data:
            artifact_json['data'] = self.data
        if self.ingest_app_id:
            artifact_json['ingest_app_id'] = self.ingest_app_id
        if self.kill_chain and ph_base._exists_in_data_set('Kill Chain Value', ph_consts.KILL_CHAIN_LIST, self.kill_chain):
            artifact_json['kill_chain'] = self.kill_chain
        if self.owner_id:
            artifact_json['owner_id'] = self.owner_id

        return artifact_json
    
    def save(self):
        """Saves artifact. 

        Sets the arifacts id. Sets the ``id`` attribute of the artifact to the new artifact id returned from phantom.
        
        Raises:
            Exception: Raises exception if artifact fails to save.
        
        Returns:
            dict: Returns a dict indicating if the artifact was saved and the new id. ``{'id': id_number, 'created', True_or_False}``
        """
        response = ph_base._send_request(
            '/rest/artifact',
            'post',
            payload=json.dumps(self.render_dictionary()),
            content_type='application/json'
        )

        if response.get(ph_consts.ARTIFACT_FAILED_KEY) and response[ph_consts.ARTIFACT_FAILED_MESSAGE_KEY] != ph_consts.ARTIFACT_EXISTING_ID:
            raise Exception(response[ph_consts.ARTIFACT_FAILED_MESSAGE_KEY])

        self.id = response[ph_consts.ARTIFACT_NEW_ID] if response.get(ph_consts.ARTIFACT_NEW_ID) else response[ph_consts.ARTIFACT_EXISTING_ID]

        artifact_results = {
            'id': self.id,
            'created': ('id' in response)
        }

        return artifact_results

    @classmethod
    def retrieve_artifact_json(cls, id=None):
        """Get artifact data from phantom.

        Args:
            id (int): id of artifact

        Returns:
            dict: returns dictionary representation of the data
        """
        return ph_base._retrieve_single_instance('artifact', id)

    @classmethod 
    def update_artifact(cls, id, artifact_data):
        """Update existing artifact's data

        Args:
            id (int): id of artifact

        Returns:
            dict: results of update
        """
        return ph_base._update_record('artifact', id, artifact_data)

    @classmethod
    def delete_artifact(cls, id):
        """Delete existing artifact
        
        Args:
            id (int): id of artifact
        
        Returns:
            dict: results of delete
        """
        return ph_base._delete_record('artifact', id)
    