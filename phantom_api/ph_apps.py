from datetime import datetime
import json
from phantom_api import ph_base
from phantom_api import ph_consts
import base64

class ph_app(object):
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
        app_path
    ):
        self.app_path = app_path
        self.app_code = None

    def install(self):
        app_contents = None
        try:
            with open(self.app_path, 'r') as app_file:
                app_contents = app_file.read()
        except Exception as err:
            raise Exception('Unable to read file - {}. Details: '.format(self.app_path, err.message))

        self.app_code = base64.b64encode(app_contents)

        payload = {'app': self.app_code}

        response = ph_base._send_request(
            '/rest/app',
            'post',
            payload=json.dumps(payload),
            content_type='application/json'
        )

        if not(response.get('success')):
            raise Exception('Unable to save app. Details: {}'.format(str(response)))

        return response