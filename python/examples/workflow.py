from random import randint
from os import path as os_path
from os import environ
import sys
from mcapi import create_project, Template, get_remote_config_url, get_process_from_id

def fake_name(prefix):
    number="%05d" % randint(0,99999)
    return prefix+number

def make_test_dir_path(file_name):
    path = os_path.abspath(environ['EXAMPLE_DATA_DIR'])
    file = os_path.join(path, file_name)
    return file


# fail early, if possible
if not 'EXAMPLE_DATA_DIR' in environ:
    print "This program requires that the environment variable EXAMPLE_DATA_DIR",\
        "be set to the path of the directory for the test files"
    sys.exit()

test_path = os_path.abspath(environ['EXAMPLE_DATA_DIR'])
if not os_path.isdir(test_path):
    print "The environment variable EXAMPLE_DATA_DIR is set to", test_path,\
        "which is not a directory, it must be the directory for the test files"
    sys.exit()

test_file1 = 'sem.tif'
filepath1 = make_test_dir_path(test_file1)
test_file2 = 'fractal.jpg'
filepath2 = make_test_dir_path(test_file2)
if not (os_path.isfile(filepath1) and os_path.isfile(filepath2)):
    print "The environment variable EXAMPLE_DATA_DIR is set to", test_path,\
        "and must contain the two test files:", test_file1, "and", test_file2,\
        "-- However, at least one of them is missing"
    sys.exit()

# start
print "This example is running on the REST interface at " + get_remote_config_url()
print "Using the configuration (config.json) in ~/.materialscommons/"

print "---- start ----"
project_name = "Workflow Project - example"
project_description = "a test project generated from api"
project = create_project(
    name=project_name,
    description=project_description)
print "Created or reused project:", project_name

experiment_name = fake_name("Experiment-")
experiment_description = "a test experiment generated from api"
experiment = project.create_experiment(
    name=experiment_name,
    description=experiment_description)
print "Created experiment:", experiment_name

create_sample_process = experiment.create_process_from_template(Template.create)

sample_name = 'Test Sample 1'
sample = create_sample_process.create_samples(
    sample_names=[sample_name]
)[0]

filepath_for_sample = make_test_dir_path(test_file1)
filename_for_sample = "SampleFile.tif"
sample_file = project.add_file_using_directory(
    project.add_directory("/FilesForSample"),
    filename_for_sample,
    filepath_for_sample
)
create_sample_process.add_files([sample_file])
create_sample_process = get_process_from_id(project,experiment,create_sample_process.id)
print "Created a 'Create Sample' process with sample: ", sample_name
print "   and attached file:", filename_for_sample," in directory /FilesForSample"

# process2_name = "Monte Carlo Simulation"
compute_process = experiment. \
    create_process_from_template(Template.compute). \
    add_samples_to_process([sample])

compute_process.set_value_of_setup_property('number_of_processors',5)
compute_process.set_value_of_setup_property('memory_per_processor',16)
compute_process.set_unit_of_setup_property('memory_per_processor','gb')
compute_process.set_value_of_setup_property('walltime',12)
compute_process.set_unit_of_setup_property('walltime','h')
compute_process.set_value_of_setup_property('submit_script',"exec.sh")
compute_process = compute_process.update_setup_properties([
        'number_of_processors','memory_per_processor','walltime','submit_script'
])

filepath_for_compute = make_test_dir_path(test_file2)
filename_for_compute = "ResultsFile.jpg"
compute_file = project.add_file_using_directory(
    project.add_directory("/FilesForCompute"),
    filename_for_compute,
    filepath_for_compute
)
compute_process.add_files([compute_file])
compute_process = get_process_from_id(project,experiment,compute_process.id)
print "Created a 'Compute' process with attached file:", filename_for_compute," in directory /FilesForCompute"
print "    and properties of: number of processors = 5, memory per processor = 16gb,"
print "    wall time = 12h, and the submit script = 'exec.sh' "

measurement_data = {
    "name":"Composition",
    "attribute":"composition",
    "otype":"composition",
    "unit":"at%",
    "value":[
        {"element":"Al","value":94},
        {"element":"Ca","value":1},
        {"element":"Zr","value":5}],
    "is_best_measure":True
}
measurement = create_sample_process.create_measurement(data=measurement_data)

measurement_property = {
            "name":"Composition",
            "attribute":"composition"
        }
create_sample_process_updated = \
    create_sample_process.\
    set_measurements_for_process_samples(\
        measurement_property, [measurement])
print "Added a Composition measurement to the 'Create Sample' process's samples with:"
print "  Al at 94%, Ca at 1%, and Zr at 5%"

print "---- done ----"