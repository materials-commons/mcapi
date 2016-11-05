from random import randint
from mcapi import create_project, Template, get_remote_config_url

print "This example is running on the REST interface at " + get_remote_config_url()
print "Using the configuration (config.json) in ~/.materialscommons/"

def fake_name(prefix):
    number="%05d" % randint(0,99999)
    return prefix+number

project_name = "API-Project"
experiment_name = fake_name("Experiment-")

print "Creating experiment, " + experiment_name + " in project " + project_name

project_description = "a test project generated from api"
experiment_description = "a test experiment generated from api"
sample_name = 'Test Sample 1'
process1_name = "Create Simulation Sample"
process2_name = "Monte Carlo Simulation"

## the workflow ##
project = create_project(
    name=project_name,
    description=project_description)

experiment = project.create_experiment(
    name=experiment_name,
    description=experiment_description)

create_sample_process = experiment.create_process_from_template(Template.create)
sample = create_sample_process.create_samples([sample_name])[0]

compute_process = experiment. \
    create_process_from_template(Template.compute). \
    add_samples_to_process([sample])
