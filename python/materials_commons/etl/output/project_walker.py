# ----
# NOTE: this code may be incomplete and in superseded by use of metadata file.
# ----
from materials_commons.api import get_project_by_id


class Walker:
    def walk(self, experiment):
        print("Walking", experiment.name)
        processes = experiment.get_all_processes()
        process_table = self.make_process_dic(processes)
        roots = []
        print(len(process_table))
        for process in processes:
            if not process.input_samples:
                print(process.name, len(process.input_samples), len(process.output_samples))
                roots.append(process)
                process_table.pop(process.id)
        front = []
        for proc in roots:
            self.push_on(front, proc)
        while front:
            print("process remaining: ", len(front))
            proc = self.pop_from(front)
            print("for proc", proc.name)
            children = self.all_child_nodes(proc, process_table)
            print("children count:", len(children))
            proc.children = children
            for child in children:
                child.parent = proc
                process_table.pop(child.id)
                self.push_on(front, child)
        return roots

    def unify_roots(self, roots):
        header_tree = roots[0]
        for proc in roots[1:]:
            header_tree = self.merge_into_tree(header_tree, proc)
        return header_tree

    def merge_into_tree(self, tree, proc):
        if not proc:
            return tree
        if not tree:
            return proc
        if tree.id == proc.id:
            self.merge_attributes_into(tree, proc)
        match_pair_list = self.find_match_in(tree, proc)
        if match_pair_list:
            self.merge_into_tree(match_pair_list[0], match_pair_list[1])
        else:
            pass

    def merge_attributes_into(self, tree, proc):
        return tree

    def find_match_in(self, tree, proc):
        return tree

    def print_path(self, indent, proc):
        padding = ""
        for i in range(0, indent):
            padding += "  "
        print(padding, proc.name, len(proc.measurements), len (proc.setup[0].properties) , proc.id)
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
                print(prop.attribute, prop.value)
                if prop.value:
                    print(padding, "|- PARAM", prop.attribute, prop.value, prop.unit)
        for child in proc.children:
            self.print_path(indent + 1, child)

    def all_child_nodes(self, proc, process_table):
        if not process_table:
            return []
        children = []
        for key in process_table:
            probe = process_table[key]
            if self.is_child(proc, probe):
                children.append(probe)
        return children

    def is_child(self, parent, candidate):
        for sample in parent.output_samples:
            for match in candidate.input_samples:
                if sample.id == match.id and sample.property_set_id == match.property_set_id:
                    return True
        return False

    def push_on(self, list, obj):
        list.append(obj)

    def pop_from(self, list):
        obj = list[len(list) - 1]
        list.remove(obj)
        return obj

    def make_process_dic(self, processes):
        table = {}
        for proc in processes:
            table[proc.id] = proc
        return table

    def find_project(self, project_id):
        return get_project_by_id(project_id)

    def find_experiment(self, project, experiment_id):
        experiments = project.get_all_experiments()
        for experiment in experiments:
            if experiment_id == experiment.id:
                return experiment
        return None

def main(pid, eid):
    walker = Walker()
    project = walker.find_project(pid)
    if not project:
        print("No project:", pid)
        exit(-1)
    experiment = walker.find_experiment(project, eid)
    if not experiment:
        print("No experiment:", eid)
        exit(-1)
    roots = walker.walk(experiment)
    print("---------------------------")
    print("|         roots           |")
    print("---------------------------")
    for proc in roots:
        walker.print_path(0, proc)


if __name__ == '__main__':
    project_id = "0842d48a-f194-4ba3-b9e8-9a98c12ee4b3"
    experiment_id = "d6cf836d-4686-45e7-8339-4c24d7d17e0f"
    main(project_id, experiment_id)
