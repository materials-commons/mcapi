from materials_commons.api import get_all_projects


def walk(experiment):
    print("Walking", experiment.name)
    processes = experiment.get_all_processes()
    process_table = make_process_dic(processes)
    roots = []
    print(len(process_table))
    for process in processes:
        if not process.input_samples:
            print(process.name, len(process.input_samples), len(process.output_samples))
            roots.append(process)
            process_table.pop(process.id)
    front = []
    for proc in roots:
        push_on(front, proc)
    while front:
        print("process remaining: ", len(front))
        proc = pop_from(front)
        print("for proc", proc.name)
        children = all_child_nodes(proc, process_table)
        print("children count:", len(children))
        proc.children = children
        for child in children:
            child.parent = proc
            process_table.pop(child.id)
            push_on(front, child)
    return roots


def unify_roots(roots):
    header_tree = roots[0]
    for proc in roots[1:]:
        header_tree = merge_into_tree(header_tree, proc)
    return header_tree


def merge_into_tree(tree, proc):
    if not proc:
        return tree
    if not tree:
        return proc
    if tree.id == proc.id:
        merge_attributes_into(tree, proc)
    match_pair_list = find_match_in(tree, proc)
    if match_pair_list:
        merge_into_tree(match_pair_list[0], match_pair_list[1])
    else:
        pass


def merge_attributes_into(tree, proc):
    return tree


def find_match_in(tree, proc):
    return tree


def print_path(indent, proc):
    padding = ""
    for i in range(0, indent):
        padding += "  "
    print(padding, proc.name, len(proc.measurements), proc.id)
    measurements = proc.measurements
    for m in measurements:
        header = "|- MEAS" + str("(*)" if m.is_best_measure else "")
        if isinstance(m.value, list):
            for el in m.value:
                print(padding, header, m.attribute + "." + el['element'], el['value'], m.unit)
        else:
            print(padding, header, m.attribute, m.value, m.unit)
    setup_list = proc.setup
    for s in setup_list:
        for prop in s.properties:
            if prop.value:
                print(padding, "|- PARAM", prop.attribute, prop.value, prop.unit)
    for child in proc.children:
        print_path(indent + 1, child)


def all_child_nodes(proc, process_table):
    if not process_table:
        return []
    children = []
    for key in process_table:
        probe = process_table[key]
        if is_child(proc, probe):
            children.append(probe)
    return children


def is_child(parent, candidate):
    for sample in parent.output_samples:
        for match in candidate.input_samples:
            if sample.id == match.id and sample.property_set_id == match.property_set_id:
                return True
    return False


def push_on(list, obj):
    list.append(obj)


def pop_from(list):
    obj = list[len(list) - 1]
    list.remove(obj)
    return obj


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
        print("No project:", project_name)
        exit(-1)
    experiment = find_experiment(project, experiment_name)
    if not experiment:
        print("No experiment:", experiment_name)
        exit(-1)
    roots = walk(experiment)
    print("---------------------------")
    print("|         roots           |")
    print("---------------------------")
    for proc in roots:
        print_path(0, proc)
    header_proc = unify_roots(roots)
    print("---------------------------")
    print("|         header          |")
    print("---------------------------")
    print_path(0, header_proc)


if __name__ == '__main__':
    project = "Tracy's Project"
    experiment = "EPMA Experiment"
    main(project, experiment)
