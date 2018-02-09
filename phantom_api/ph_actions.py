from datetime import datetime
import json
from phantom_api import ph_base
from phantom_api import ph_consts

class ph_action(object):
    """Facilitates action execution in phantom

    Args:
        action (string): action name to be run (e.g. ip reputation)
        container_id (int): id of container on which to run action
        name (string): name of action - how it will appear in mission control
    
    Keyword Args:
        targets ([string] or None): list of dictionaries describing targets.
        action_id (int or None): id of running action - auto-set after run() has been called.
        acton_type (string or None): type of action (e.g. investigative, generic, etc.)

    Note:
        For information on how ``targets`` should be configured please see the phantom REST API
        documentation -or- use ``add_target()`` to make this simpler.
    """


    def __init__(
        self,
        action,
        container_id,
        name,
        targets=[],
        action_id=None,
        action_type=None
    ):
        self.action = action
        self.container_id = container_id
        self.name = name
        self.targets = targets
        self.action_id = action_id
        self.action_type = action_type

    def run(self):
        """Used to run a phantom action.

        After ``run()`` is called the action_id is set on the object.
        
        Raises:
            Exception: If action fails, exception is raised.
        
        Returns:
            [int]: Returns the action run id of the phanton action.
        """

        response = ph_base._send_request(
            '/rest/action_run',
            'post',
            payload=json.dumps(self.render_dictionary()),
            content_type='application/json'
        )

        if not(response.get(ph_consts.ACTION_SUCCESS_KEY)):
            raise Exception(response[ph_consts.ACTION_FAILED_MESSAGE_KEY])



        self.action_id = response[ph_consts.ACTION_RUN_ID]

        return response

    def add_target(self, assets, parameters, app_id):
        """Adds targets to the action. Targets indicate the asset, parameters, 
        and apps the action should be run with.
        
        Args:
            assets ([string]): List of asset names against which this action should be run.
            parameters ([dict]): List of dictionaries describing the parameter name and value for the action.
            app_id ([int]): id of the app

        Example:
            Adding ip reputation action with the virus total app for two different ips::

                action = ph_action('ip reputation', 1069, 'vt ip reputation')
                action.add_target(['virustotal'], [{'ip': '8.8.8.8'}, {'ip': '1.1.1.1'}], 35)

        Note:
            app_id can be retrieved by going to the apps->app_name->configure new asset. The app id can 
            bet determined in the url.
        """

        self.targets.append(
            {'assets': assets, 'parameters': parameters, 'app_id': app_id}
        )

    def render_dictionary(self):
        """Renders a dictionary representation of the object that could easily be convered to JSON
        with ``json.loads()``.
        
        Returns:
            dict: Dictionary representation of action.
        """

        action_json = {
            'action': self.action,
            'container_id': self.container_id,
            'name': self.name,
            'targets': self.targets
        }

        return action_json

    def status(self):
        """Returns the status of a running action.
        
        Returns:
            string: Actions status.

        Example:
            Retrieve an action status after ``run()`` is called::

                action = ph_actions(...parameters_go_here...)
                action.run()
                actoin.status() # action status returned

        Note:
            Use this instance method if you either have already run `run()` or you
            manually configured the action_id attribute of the object. Otherwise,
            use the class method ``ph_action.get_action_status``.
        """

        return ph_action.get_action_status(self.action_id)

    @classmethod
    def get_action_status(cls, action_id):
        """Returns status of action.

        This should be used if you want to get the status of an action for which
        you already know the ``action_id``.
        
        Args:
            action_id (int): id of running action.

        Example:
            Get action status::

                ph_action.get_action_status(444) # returns action status
        """

        response = ph_base._send_request(
            '/rest/action_run/' + str(action_id),
            'get'
        )

        return(response)

    def cancel(self):
        """Cancels running action.
        
        Raises:
            Exception: Raises exception if action fails to be cancelled.

        Returns:
            bool: True if action cancelled.

        Example:
            Cancels action after ``run()`` is called::

                action = ph_actions(...parameters_go_here...)
                action.run()
                actoin.cancel() # action cancelled

        Note:
            Use this instance method if you either have already run `run()` or you
            manually configured the action_id attribute of the object. Otherwise,
            use the class method ``ph_action.cancel_action()``.
        """

        return ph_action.cancel_action(self.action_id)

    @classmethod
    def cancel_action(cls, action_id):
        """Cancels action.

        This should be used if you want to cancel an action for which
        you already know the ``action_id``.
        
        Args:
            action_id (int): id of running action.

        Raises:
            Exception: Raises exception if action fails to be cancelled.

        Returns:
            bool: True if action cancelled.

        Example:
            Cancel the action::

                ph_action.cancel_action(444) # cancels action
        """
        response = ph_base._send_request(
            '/request/action_run/' + str(action_id),
            'post',
            payload=json.dumps({'cancel': True})
        )

        if ph_consts.ACTION_CANCEL_FAILED_KEY in response:
            raise Exception(response[ph_consts.ACTION_FAILED_MESSAGE_KEY])

        return True

class ph_playbook(object):
    """Facilitates playbook execution in phantom.

    Args:
        container_id (int): id of the container against which the playbook should be run.
        playbook_id (int): id of the playbook

    Keyword Args:
        scope (sting): Default value is ```new```
        run_playbook (bool): Run the playbook. Defaults to ``True``
        playbook_run_id (int): set after calling ``run()``

    Note:
        I have not found a reason for setting run_playbook to anything but ``True``
    """

    def __init__(
        self,
        container_id,
        playbook_id,
        scope='new',
        run_playbook=True,
        playbook_run_id=None
    ):
        self.container_id = container_id
        self.playbook_id = playbook_id
        self.scope = scope
        self.playbook_run_id = playbook_run_id
        self.run_playbook = run_playbook

    def render_dictionary(self):
        """Renders a dictionary representation of the object that could easily be convered to JSON
        with ``json.loads()``.
        
        Returns:
            dict: Dictionary representation of playbook.
        """

        playbook_json = {
            'container_id': self.container_id,
            'playbook_id': self.playbook_id,
            'scope': self.scope,
            'run': self.run_playbook
        }

        return playbook_json

    def run(self):
        """Runs the playbook

        After ``run()`` is called, the playbook_run_id attribute is set.
        
        Raises:
            Exception: Raises Exception if playbook fails to run.
        
        Returns:
            [dict]: Returns the response dictionary from the playbook run.
        """

        response = ph_base._send_request(
            '/rest/playbook_run',
            'post',
            payload=json.dumps(self.render_dictionary()),
            content_type='application/json'
        )

        if ph_consts.PLAYBOOK_RUN_ID not in response:
            raise Exception(response[ph_consts.PLAYBOOK_FAILED_MESSAGE_KEY])

        self.playbook_run_id = response[ph_consts.PLAYBOOK_RUN_ID]

        return response

    def status(self):
        """Gets the status of a playbook.
        
        Returns:
            dict: Gets the response details of playbook status.

        Example:
            Get the playbook status::

                pb = ph_playbook(...parameters_go_here...)
                pb.run()

        Note:
            Use this if you have already called ``run()`` or you have manually
            set the playbook_run_id of the this playbook object. Otherwise,
            use the class method get_playbook_status.
        """

        return ph_playbook.get_playbook_status(self.playbook_run_id)

    @classmethod
    def get_playbook_status(cls, playbook_run_id):
        """Gets the status of a playbook.
        
        Args:
            playbook_run_id (int): Playbook run id from a running playbook or running playbook.
        
        Returns:
            dict: Returns playbook status.

        Example:
            Get playbook status::

                ph_playbook.get_playbook_status(111)
        """

        response = ph_base._send_request(
            '/rest/playbook_run/' + str(playbook_run_id),
            'get'
        )

        return response

    def cancel(self):
        """Cancels running playbooks.

        Raises:
            Exception: Raises exception if action fails to be cancelled.
        
        Returns:
            bool: True if action cancelled.

        Example:
            Cancels action after ``run()`` is called::

                pb = ph_playbook(...parameters_go_here...)
                pb.run()
                pb.cancel() # action cancelled

        Note:
            Use this instance method if you either have already run `run()` or you
            manually configured the playbook_run_id attribute of the object. Otherwise,
            use the class method ``ph_playbook.cancel_playbook()``.
        """
        return ph_playbook.cancel_playbook(self.playbook_run_id)

    @classmethod
    def cancel_playbook(cls, playbook_run_id):
        """Cancels action.

        This should be used if you want to cancel an action for which
        you already know the ``playbook_run_id``.
        
        Args:
            playbook_run_id (int): id of running playbook.

        Raises:
            Exception: Raises exception if action fails to be cancelled.
        
        Returns:
            bool: True if action cancelled.

        Example:
            Cancel the playbook::

                ph_action.cancel_playbook(111) # cancels playbook
        """

        response = ph_base._send_request(
            '/request/playbook_run/' + str(playbook_run_id),
            'post',
            payload=json.dumps({'cancel': True})
        )

        if ph_consts.PLAYBOOK_CANCEL_FAILED_KEY in response:
            raise Exception(response[ph_consts.PLAYBOOK_FAILED_MESSAGE_KEY])

        return True