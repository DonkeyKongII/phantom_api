from datetime import datetime
import json
from phantom_api import ph_base
from phantom_api import ph_consts

class ph_asset(object):
    """Used to configure assets in phantom.

    Args:
        name (string): name of asset
        product_name (string): product name (must match product name in app definition)
        product_vendor (string): product vendor (must match product vendor in app definition)
        
    Keyword Args:        
        configuration (dict): configuration parameters for asset
        description (string): description of asset
        primary_users ([int]): list of approver user ids
        primary_voting ([int]): number of approver users required for approval
        secondary_users ([int]): list of secondary user ids
        secondary_voting ([int]): number of secondary approver users required for approval
        tags ([string]): list of tags for asset
        action_whitelist (dict): dictionary of actions that are whiteliste for roles and/or users
        ingest_container_label (string): label name for ingested events by this app
        ingest_interval_mins (int): frequency with which app should poll data source
        ingest_poll (bool): Polling turned on?
        ingest_start_time (date: Date polling should start (isoformat)
        asset_id (int): id of asset - set after ``save()`` or can be manually configured.

    Note:
        * Review phantom REST api details for action_whitelist format
        * ``ingest_`` arguments are only necessary if this is an ingest app.

    """


    def __init__(
        self,
        name,
        product_name,
        product_vendor,
        configuration={},
        description='',
        primary_users=[],
        primary_voting=0,
        secondary_users=[],
        secondary_voting=0,
        tags=[],
        asset_type='',
        action_whitelist={},
        ingest_container_label=None,
        ingest_interval_mins=None,
        ingest_poll=True,
        ingest_start_time=datetime.now().isoformat()[:23]+'Z',
        asset_id=None
    ):
        self.name = name
        self.product_name = product_name
        self.product_vendor = product_vendor
        self.configuration=configuration
        self.description=description
        self.primary_users=primary_users
        self.primary_voting=primary_voting
        self.secondary_users=secondary_users
        self.secondary_voting=secondary_voting
        self.tags=tags
        self.asset_type=asset_type
        self.action_whitelist=action_whitelist
        self.ingest_container_label=ingest_container_label
        self.ingest_interval_mins=ingest_interval_mins
        self.ingest_poll=ingest_poll
        self.ingest_start_time=ingest_start_time
        self.asset_id=asset_id

    def render_dictionary(self):
        """Renders a dictionary representation of the object that could easily be convered to JSON
        with ``json.loads()``.
        
        Returns:
            dict: Dictionary representation of asset.
        """      
        asset_json = {
            'name': self.name,
            'product_name': self.product_name,
            'product_vendor': self.product_vendor,
            'configuration': self.configuration,
            'description': self.description,
            'primary_users': self.primary_users,
            'primary_voting': self.primary_voting,
            'secondary_users': self.secondary_users,
            'secondary_voting': self.secondary_voting,
            'tags': self.tags,
            'type': self.asset_type,
            'action_whitelist': self.action_whitelist
        }

        if self.ingest_container_label:
            asset_json['ingest'] = {
                'container_label': self.ingest_container_label,
                'interval_mins': self.ingest_interval_mins,
                'poll': self.ingest_poll,
                'start_time_epoch_utc': self.ingest_start_time
            }

        return asset_json

    def save(self):
        """Saves asset.
        
        Raises:
            Exception: Exception raised if issue saving asset.
        
        Returns:
            int: Returns asset id of newly saved asset.
        """

        response = ph_base._send_request(
            '/rest/asset',
            'post',
            payload=json.dumps(self.render_dictionary()),
            content_type='application/json'
        )

        if not response.get(ph_consts.ASSET_NEW_ID):
            message = response[ph_consts.ASSET_FAILED_MESSAGE_KEY] if response.get(ph_consts.ASSET_FAILED_MESSAGE_KEY) else 'Error creating asset.'
            raise Exception(message)

        self.asset_id = response['id']

        return response['id']

    @classmethod
    def update_asset(cls, id, asset_data):
        """Update an existing asset.
        
        Args:
            id (int): asset id
            asset_data (dict): dictionary of udpated asset info.
        
        Returns:
            dict: Returns json data from the command.
        """

        return ph_base._update_record('asset', id, asset_data)

    @classmethod
    def delete_asset(cls, id):
        """Deletes asset.
        
        Args:
            id (int): Id of the asset to be deleted.

        Returns:
            dict: Returns json data from the command.
        """

        return ph_base._delete_record('asset', id)