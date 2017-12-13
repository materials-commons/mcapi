from materials_commons.api import get_all_projects

def walk(experiment):
    print("Walking", experiment.name)
    processes = experiment.get_all_processes()
    process_table = make_process_dic(processes)
    roots = []
    print(len(process_table))
    for process in processes:
        if not process.input_samples:
            print (process.name, len(process.input_samples), len(process.output_samples))
            roots.append(process)
            process_table.pop(process.id)


def make_process_dic(processes):
    table = {}
    for proc in processes:
        table[proc.id] = proc
    return table

def find_project(name):
    projects = get_all_projects()
    probe = None
    for project in projects:
        if project.name == name:
            probe = project
    return probe


def find_experiment(project, name):
    experiments = project.get_all_experiments()
    probe = None
    count = 0
    for experiment in experiments:
        if experiment.name == name:
            probe = experiment
    if not probe:
        return None
    if count > 1:
        print("Exit! Found more the one experiment with name = ", name)
        return None
    return probe

def main(project_name, experiment_name):
    project = find_project(project_name)
    if not project:
        print("No project:",project_name)
        exit(-1)
    experiment = find_experiment(project,experiment_name)
    if not experiment:
        print("No experiment:", experiment_name)
        exit(-1)
    walk(experiment)

if __name__ == '__main__':
    project = "Tracy's Project"
    experiment = "EPMA Experiment"
    main(project, experiment)