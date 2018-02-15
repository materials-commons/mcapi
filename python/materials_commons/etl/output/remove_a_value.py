import sys
import argparse
from materials_commons.api import get_all_projects

def get_project(project_name):
    project = None
    project_list = get_all_projects()
    for proj in project_list:
        if proj.name == project_name:
            project = proj
            break
    return project


def get_experiment(project, experiment_name):
    experiment = None
    experiment_list = project.get_all_experiments()
    found = []
    for exp in experiment_list:
        if exp.name == experiment_name:
            found.append(exp)
    if found:
        experiment = found[0]
    return experiment


def first_process_with_set_up(experiment):
    process_list = experiment.get_all_processes()
    found = None
    for process in process_list:
        for s in process.setup:
            for prop in s.properties:
                if (prop.value is not None) and (str(prop.value).strip() != ""):
                    print(process.id, prop.attribute, prop.value)
                    found = process
    return found


def remote_first_param(process):
    pass


def first_process_with_measurements(experiment):
    process_list = experiment.get_all_processes()
    found = None
    for process in process_list:
        pass
    return found


def remove_first_measurement(process):
    pass


def main(project_name, experiment_name):
    project = get_project(project_name)
    if not project:
        print("Could not find project", project_name)
        exit(-1)
    print("Project", project.name, project.id)
    experiment = get_experiment(project, experiment_name)
    if not experiment:
        print("Count not find experiment:", experiment_name)
        exit(-1)
    print("Experiment", experiment.name, experiment.id)
    process = first_process_with_set_up(experiment)
    if not process:
        print("No processes with setup parameters in experiment:", experiment_name)
    else:
        print("Param - Process", process.name, process.id)
        if not remote_first_param(process):
            print("Could not remove paramter from process")

    process = first_process_with_measurements(experiment)
    if not process:
        print("No processes with measurments in experiment:", experiment_name)
    else:
        print("Param - Process", process.name, process.id)
        if not remove_first_measurement(process):
            print("Could not remove measurement from process")


if __name__ == '__main__':
    argv = sys.argv
    parser = argparse.ArgumentParser()
    parser.add_argument('proj', type=str, help="Project Name")
    parser.add_argument('exp', type=str, help="Experiment Name")
    args = parser.parse_args(argv[1:])
    main(args.proj, args.exp)
