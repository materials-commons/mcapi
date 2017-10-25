from os import environ
from os import path as os_path
from random import randint
import extras.demo_project.demo_project as demo
# for test-only dataset - normally datasets are not created through API!
from materials_commons.api import __api as api
from materials_commons.api import get_project_by_id


def _fake_name(prefix):
    number = "%04d" % randint(0, 9999)
    return prefix+number


def _build_project():
    project_name = _fake_name("ExpDeleteTest")
    print("")
    print("Project name: " + project_name)
    builder = demo.DemoProject(_make_test_dir_path())
    project = builder.build_project()
    project = project.rename(project_name)
    return project


def _make_test_dir_path():
    if 'TEST_DATA_DIR' not in environ:
        print("'TEST_DATA_DIR' is not defined. quiting.")
        exit(1)

    test_path = os_path.abspath(environ['TEST_DATA_DIR'])
    if not test_path:
        print("Path not valid: " + environ['TEST_DATA_DIR'])
        exit(1)

    if not os_path.isdir(test_path):
        print("Path is not a directory: " + test_path)
        exit(1)

    test_path = os_path.join(test_path, 'demo_project_data')
    if not os_path.isdir(test_path):
        print("Path is not a directory: " + test_path)
        exit(1)

    return test_path


def _add_dataset(project, experiment, title):
    project_id = project.id
    experiment_id = experiment.id
    results = api.create_dataset(project_id, experiment_id, title, "Example dataset for testing")
    return results


def _add_process_to_dataset(project, experiment, dataset, process):
    project_id = project.id
    experiment_id = experiment.id
    dataset_id = dataset['id']
    process_id = process.id
    results = api.add_process_to_dataset(project_id, experiment_id, dataset_id, process_id)
    return results


def _generate_demo_project():
    project = _build_project()
    experiment = project.get_all_experiments()[0]
    dataset = _add_dataset(project, experiment, "Test datasets")
    processes = project.get_all_processes()
    for process in processes:
        _add_process_to_dataset(project, experiment, dataset, process)
    project = get_project_by_id(project.id)

    print(dataset)
