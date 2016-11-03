import api
from mc import Sample

def create_samples(project_id, process_id, sample_names):
    samples_array_dict = api.create_samples(project_id, process_id, sample_names)
    samples_array = samples_array_dict['samples']
    return map((lambda x: Sample(data=x)), samples_array)
