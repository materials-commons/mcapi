from mcapi import api, MCObject

class Experiment(MCObject):
    def __init__(self, project_id, name, description="", id=None,
                 goals=None, aims=None, tasks=None, data={}):

        super(Experiment, self).__init__(data)

        self.name = name,
        self.description = description
        self.project_id = project_id
        if (id):
            self.id = id
        if (goals):
            self.goals = goals
        else:
            self.goals = []

        if (aims):
            self.aims = aims
        else:
            self.aims = []

        if (tasks):
            self.tasks = tasks
        else:
            self.tasks = []

def create_experiment(project_id, name, description):
    experiment_json = api.create_experiment(project_id, name, description)
