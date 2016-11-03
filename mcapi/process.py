import api
from mc import Process

def create_process_from_template(project_id, experiment_id, template_id):
    process_dictionary = api.create_process_from_template(project_id, experiment_id, template_id)
    return Process(data=process_dictionary)


def add_samples_to_process(project_id, experiment_id, process, samples):
    results = api.add_samples_to_process(project_id, experiment_id, process, samples)
    print results
    return Process.fromJson(results)

