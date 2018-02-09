QUERY_TYPES = (
    'action_run',
    'artifact',
    'asset',
    'app',
    'app_run',
    'container',
    'playbook_run',
    'ph_user',
    'role'
)



QUERY_FILTERS = (
    'exact',
    'iexact',
    'contains',
    'icontains',
    'in',
    'gt',
    'gte',
    'lt',
    'lte',
    'startswith',
    'istartswith',
    'endswith',
    'iendswith',
    'range',
    'year',
    'month',
    'day',
    'week_day',
    'hour',
    'minute',
    'second',
    'isnull',
    'regex',
    'iregex'
)

QUERY_SORT_ORDER = (
    'asc',
    'desc'
)

ROLE_PERMISSIONS=[
    'apps',
    'assets',
    'containers',
    'container_labels',
    'playbooks',
    'system_settings',
    'users_roles'
]

ROLE_ACTIONS=[
    'edit',
    'execute',
    'extra',
    'delete',
    'name',
    'view'
]

PSEUDO_FIELDS = {
    'action_run': (
        'app_runs',
        'approvals'
    ),
    'app_run': (
        'log'
    ),
    'container': (
        'actions',
        'attachments',
        'playbook_runs',
        'artifacts',
        'audit',
        'comments',
        'recommended_actions',
        'recommended_playbooks',
    ),
    'playbook': (
        'audit'
    ),
    'playbook_run': (
        'actions',
        'log'
    ),
    'ph_user': (
        'roles',
        'audit'
    ),
    'role': (
        'users',
        'audit'
    )
}

AUDIT_TYPES = (
    'playbook',
    'container',
    'authentication',
    'administration',
    'ph_user',
    'role'
)

AUDIT_FORMAT = (
    'json',
    'csv'
)

KILL_CHAIN_LIST = (
    'Reconnaissance',
    'Weaponization',
    'Delivery',
    'Exploitation',
    'Intallation',
    'Command & Control',
    'Actions on Objectives'
)

ARTIFACT_SEVERITY = (
    'low',
    'medium',
    'high'
)

CONTAINER_SENSITIVITY = (
    'white',
    'green',
    'amber',
    'red'
)

CONTAINER_STATUS = (
    'new',
    'open',
    'closed'
)

CONTAINER_PIN_TYPE = (
    'data',
    'card_small',
    'card_medium',
    'card_large'
)

CONTAINER_PIN_STYLE = (
    '',
    'white',
    'purple',
    'red'
)

ACTION_SUCCESS_KEY = 'success'
ACTION_STATUS_KEY = 'status'
ACTION_FAILED_MESSAGE_KEY = 'message'
ACTION_RUN_ID = 'action_run_id'
ACTION_CANCEL_FAILED_KEY = 'failed'

PLAYBOOK_RUN_ID = 'playbook_run_id'
PLAYBOOK_FAILED_MESSAGE_KEY = 'message'
PLAYBOOK_CANCEL_FAILED_KEY = 'failed'

ASSET_SUCCESS_KEY = 'success'
ASSET_FAILED_MESSAGE_KEY = 'message'
ASSET_NEW_ID = 'id'

ARTIFACT_FAILED_KEY = 'failed'
ARTIFACT_SUCCESS_KEY = 'success'
ARTIFACT_FAILED_MESSAGE_KEY = 'message'
ARTIFACT_DUPLICATE_MESSAGE = 'artifact already exists'
ARTIFACT_EXISTING_ID = 'existing_artifact_id'
ARTIFACT_NEW_ID = 'id'

CONTAINER_FAILED_KEY = 'failed'
CONTAINER_SUCCESS_KEY = 'success'
CONTAINER_FAILED_MESSAGE_KEY = 'message'
CONTAINER_DUPLICATE_MESSAGE = 'duplicate with source_data_identifier'
CONTAINER_EXISTING_ID = 'existing_container_id'
CONTAINER_NEW_ID = 'id'

USER_SUCCESS_KEY = 'success'
USER_FAILED_MESSAGE_KEY = 'message'
USER_NEW_ID = 'id'

ROLE_SUCCESS_KEY = 'success'
ROLE_FAILED_MESSAGE_KEY = 'message'
ROLE_NEW_ID = 'id'

CASE_SUCCESS_KEY = 'success'
CASE_FAILED_MESSAGE_KEY = 'message'
CASE_NEW_ID = 'id'

PHASE_SUCCESS_KEY = 'success'
PHASE_FAILED_MESSAGE_KEY = 'message'
PHASE_NEW_ID = 'id'

TASK_SUCCESS_KEY = 'success'
TASK_FAILED_MESSAGE_KEY = 'message'
TASK_NEW_ID = 'id'

LIST_SUCCESS_KEY = 'success'
LIST_FAILED_MESSAGE_KEY = 'message'
LIST_NEW_ID = 'id'

ACTION_FAILED_STATUS = 'failed'
ACTION_PENDING_STATUS = 'pending'
ACTION_RUNNING_STATUS = 'running'
ACTION_SUCCESS_STATUS = 'success'

PLAYBOOK_FAILED_STATUS = 'failed'
PLAYBOOK_RUNNING_STATUS = 'running'
PLAYBOOK_SUCCESS_STATUS = 'success'

USER_PERMISSION_OBJECT_NAMES = (
    'apps',
    'assets',
    'containers',
    'container_labels',
    'playbooks',
    'system_settings',
    'users_roles'
)