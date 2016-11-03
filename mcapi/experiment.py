import api
from mc import Experiment

def create_experiment(project_id, name, description):
    experiment_json = api.create_experiment(project_id, name, description)
    return Experiment(data=experiment_json)

