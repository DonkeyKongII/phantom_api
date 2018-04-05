import json
from phantom_api import ph_base
from phantom_api import ph_consts

class ph_case(object):
    """Facilitates the creation of case templates.
    
    Args:
        name (string): name of case template
        id (int): id of case template - set after calling ``save()`` or can be configured manually.
    """    
    def __init__(
        self,
        name,
        id=None,
        is_default=False
    ):
        self.name = name
        self.id = id
        self.is_default = is_default
        self.phases = []
        

    def save(self):
        """Saves case template
        
        Raises:
            Exception: Raises exception if case failed to be saved.
        
        Returns:
            int: Returns case template id of newly saved case template.
        """

        response = ph_base._send_request(
                    '/rest/workflow_template',
                    'post',
                    payload=json.dumps(self.render_dictionary()),
                    content_type='application/json'
                )

        if ph_consts.CASE_SUCCESS_KEY not in response:
            raise Exception(
                'Error saving case - ' + self.name + '. '
                + response[ph_consts.CASE_FAILED_MESSAGE_KEY]
            )
        elif ph_consts.CASE_NEW_ID in response:
            self.id = response[ph_consts.CASE_NEW_ID]

        return True
    
    def add_phase(self, phase):
        """Add a phase object to the case.
        
        Args:
            phase (ph_phase): A ph_phase object describing a case phase.
        
        Raises:
            Exception: Exception raised if attempting to add a phase with a phase number that already exists.
        
        Returns:
            bool: Returns true if successfully saved phase.
        """

        if phase.order in [phase.order for phase in self.phases]:
            raise Exception(
                'A phase with this order number (' + str(phase.order)
                + ') has already been added. Change order or use create_phase_space '
                + 'to move all preexisting phases starting at ' + str(phase.order)
                + ' up one.'
            )

        self.phases.append(phase)

        return True

    def create_phase_space(self, order):
        """Creates and empty space between existing phases to make room for a new phase.
        
        Args:
            order (int): Phase order number where you want to insert the new phase.
        
        Raises:
            Exception: Exception raised if the phase number doesn't exist.
        
        Returns:
            bool: True if space was successfully created.

        Example:
            There is a three phase case. You want to add a phase between phases 2 and 3::

                c = ph_case(...parameters_go_here...)
                c.create_phase_space(3)
                c.add_phase(new_phase_3) # phase order defined in phase object
        """

        if order not in [phase.order for phase in self.phases]:
            raise Exception(
                'No existing phase has order number >= ' + str(order) + '. Phase order '
                + 'not changed.'
            )
        for phase in self.phases:
            if phase.order >= order:
                phase.order += 1

        return True

    def render_dictionary(self):
        """Returns a dictionary representation of the case template that can easily be converted to json
        with ``json.loads``
        
        Returns:
            dict: Dictionary representation of case template object.
        """

        template_json = {
            'name': self.name,
            'is_default': self.is_default,
            'phases': []
        }

        for phase in self.phases:
            template_json['phases'].append(phase.render_dictionary())

        return template_json

    def delete(self):
        return ph_case.delete(self.id)

    @classmethod
    def delete_case(cls, case_id):
        response = ph_base._send_request(
            '/rest/workflow_template/' + str(case_id),
            'delete' 
        )

        return response

class ph_phase(object):
    """Faclilitates the saving of new case phases.

    Args:
        name (string): name of phase
        order (int): order number of phase
    
    Keyword Args:
        id (int): id of saved phase. Set after ``save()`` is called.
        template_id (int): Use only if saving a phase to an existing case.
    """
    
    def __init__(
        self,
        name,
        order,
        id=None,
        template_id=None,
        tasks=[]
    ):
        self.name = name
        self.order = order
        self.template_id = template_id
        self.tasks = tasks
        if not(ph_base.ready()):
            raise Exception('pa_base has not been initiated.')
    
    def save(self):
        """Saves the phase. 
        
        Raises:
            Exception: Raises exception if save is attempted without saving template id.
            Exception: Raises exception if phase failed to save.
        
        Returns:
            bool: Returns True if phase successfully saved.

        Note:
            This should only be used if you are saving phases to existing case templates.
            If you are creating an entirely new case template. Use the ``add_phase()`` method
            of ``ph_case`` to add this phase to that case, and the call ``save()`` on the case.
        """

        if self.template_id is None:
            raise Exception(
                'Phase can only be saved if template ID is set to existing '
                +'case template id.'
            )

        response = ph_base._send_request(
            '/rest/workflow_phase_template',
            'post',
            payload=json.dumps(self.render_dictionary()),
            content_type='application/json'
        )

        if ph_consts.PHASE_SUCCESS_KEY not in response:
            raise Exception(
                'Error trying to save phase - ' + self.name + '. '
                + response[ph_consts.PHASE_FAILED_MESSAGE_KEY]
            )
        elif ph_consts.PHASE_NEW_ID in response:
            self.id = response[ph_consts.PHASE_NEW_ID]

        return True

    def add_task(self, task):
        """Add a task to this phase.
        
        Args:
            task (ph_task): Task object to add to phase.
        
        Raises:
            Exception: Exception raised if task with same order number has already been added.
        
        Returns:
            bool: Returns True if save successful.
        """

        if task.order in [task.order for task in self.tasks]:
            raise Exception(
                'A task with this order number (' + str(task.order)
                + ') has already been added. Change order or use create_task_space '
                + 'to move all preexisting tasks starting at ' + str(task.order)
                + ' up one.'
            )
        
        self.tasks.append(task)

        return True

    def create_task_space(self, order):
        """Creates and empty space between existing tasks to make room for a new task.
        
        Args:
            order (int): Phase order number where you want to insert the new task.
        
        Raises:
            Exception: Exception raised if the task number doesn't exist.
        
        Returns:
            bool: True if space was successfully created.

        Example:
            There is a three task phase. You want to add a task between tasks 2 and 3::

                c = ph_task(...parameters_go_here...)
                c.create_task_space(3)
                c.add_task(new_task_3) # task order defined in phase object
        """
        if order not in [task.order for task in self.tasks]:
            raise Exception(
                'No existing task has order number >= ' + str(order) + '. Task order '
                + 'not changed.'
            )
        for task in self.tasks:
            if task.order >= order:
                task.order += 1

        return True

    def render_dictionary(self):
        """Returns a dictionary representation of the object that can easily be converted to json
        with ``json.loads``
        
        Returns:
            dict: dictionary representation of task object.
        """

        phase_json = {
            'name': self.name,
            'order': self.order,
            'tasks': []
        }

        for task in self.tasks:
            phase_json['tasks'].append(task.render_dictionary())

        if self.template_id:
            phase_json['template_id'] = self.template_id

        return phase_json

class ph_task(object):
    """Facilitates the saving of case template tasks.

    Args:
        name (string): task name
        description (string): description of task
        order (int): order number of task

    Keyword Args:
        id (int): set after ``save()`` is called.
        actions ([string]): list of actions to be associated with this task (e.g. ['ip reputation', 'ip lookup'])
        playbooks ([dict]): list of dictionary describing playbooks.
        phase_id (int): Used only if the task is being saved to an existing phase.

    Note:
        Rather than set ``playbooks`` directly, it is easier to use ``add_playbook()`` which allows you to send in
        source repo and playbook name.
    """


    def __init__(
        self,
        name,
        description,
        order,
        id=None,
        actions=[],
        playbooks=[],
        phase_id=None
    ):
        self.name = name
        self.description = description
        self.order = order
        self.actions = actions
        self.playbooks = playbooks
        self.phase_id = phase_id
        if not(ph_base.ready()):
            raise Exception('pa_base has not been initiated.')

    def save(self):
        if self.phase_id is None:
            raise Exception(
                'Tasks can only be saved if phase ID is set to existing '
                +'phase id.'
            )

        response = ph_base._send_request(
            '/rest/workflow_task_template',
            'post',
            payload=json.dumps(self.render_dictionary()),
            content_type='application/json'
        )

        if ph_consts.TASK_SUCCESS_KEY not in response:
            raise Exception(
                'Error trying to save task - ' + self.name + '. '
                + response[ph_consts.TASK_FAILED_MESSAGE_KEY]
            )
        elif ph_consts.TASK_NEW_ID in response:
            self.id = response[ph_consts.TASK_NEW_ID]

        return True


    def add_playbook(self, repository, playbook_name):
        """Adds playbook to task.
        
        Args:
            repository (string): respository name
            playbook_name (string): name of playbook to be associated.
        
        Returns:
            bool: Returns true playbook was appended to playbook list.

        Note:
            This does not save the playbook to the task in phantom. It merely
            appends the playbook to the task, for later saving.
        """

        self.playbooks.append({'scm': repository, 'playbook': playbook_name})

        return True

    def add_action(self, action_name):
        """Adds action to task.
        
        Args:
            action_name (string): name of action to run.
        
        Returns:
            bool: Returns true playbook was appended to playbook list.

        Note:
            This does not save the playbook to the task in phantom. It merely
            appends the playbook to the task, for later saving.
        """

        self.actions.append(action_name)

        return True

    def render_dictionary(self):
        """Creates a dictionary representation of the task object that can easily
        converted to json with ``json.loads``

        Returns:
            dict: dictionary representation of task object.
        """

        task_json = {
            'name': self.name,
            'description': self.description,
            'order': self.order,
            'actions': self.actions,
            'playbooks': self.playbooks
        }

        if self.phase_id:
            task_json['phase_id'] = self.phase_id
        
        return task_json

    @classmethod
    def update_task(cls, task_id, task_json):
        response = ph_base._send_request(
            '/rest/workflow_task_template/' + str(task_id),
            'post',
            payload=json.dumps(task_json),
            content_type='application/json'
        )

        return response

