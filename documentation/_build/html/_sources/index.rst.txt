.. phantom_api documentation master file, created by
   sphinx-quickstart on Thu Feb  8 21:34:45 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to phantom_api's documentation!
=======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

This documentation is alpha v0.1.

About the phantom_api wrapper.
=======================================

This is designed to be a python interface to phantom REST api, to ease use and speed up development.

The code is broken up into several modules which themselves contain the classes you may need to access. More information
about the modules can be found at :ref:`modindex`:

- ph_actions.py
    - contains classes:
        - ph_action - for starting new actions and getting action status
        - ph_playbook - for starting new playbooks and geting playbook status
- ph_assets.py
    - contains class:
        - ph_asset - for creating an manipulating new and existing assets
- ph_base.py (module file):
    - contains module methods:
        - query - for searching for phantom objects (e.g. containers, artifacts, etc.)
        - get_audit_data - for retrieving audit get_audit_data
- ph_cases.py
    - contains classes:
        - ph_case - case templates
        - ph_phase - case template ph_asset
        - ph_task - case template tasks
- ph_consts.py
    - This file contains constants which you may review for reference but are unlikely to be used by you.
- ph_events.py
    - contains classes:
        - ph_container - for creating and manipulating containers
        - ph_artifact - for creating and manipulating artifacts
- ph_lists.py
    - contains class:
        - ph_list - for creating phantom custom ph_lists
- ph_users.py
    - contains class:
        - ph_user - for creating phantom users
        - ph_role - for creating phantom roles

Addition information about these modules and each supported method can be found in the :ref:`modindex`.

Using the phantom API wrapper.
=======================================
Most of the classes will have instance and classes methods. The instance methods are primarily
designed for when you want to create new objects in phantom while the class methods are for when
an object already exists and you have some information about it but want to get more, or you want to 
update it.

Here is an example using the instance methods to create a role:

.. code-block:: python

    #here I will create a role using the instance methods
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

    role.save() # when I save the role.role_id property is automatically updated

    # update the role now with the instance method
    role.update(add_users=[1,2]) # role now has users with ids 1 and 2 added

Here is an example using the class methods to update a pre-existing role which has an id of 77. Notice that I don't need to needlessly create an instance of ph_role.

.. code-block:: python

    # here I will update an existing rol with id of 77
    ph_role.update_role(role_id=77, add_users=[1,2]) # add users with id's of 1 and 2 to the role

What's next?
=======================================
Testing. Please tests and send me your bugs (i'm sure there are plenty) - ian.forrest@phantom.us

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
