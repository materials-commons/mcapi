from materials_commons.api import get_project_by_id
from materials_commons.etl.input.metadata import Metadata

metadata_path = "/Users/weymouth/Desktop/metadata.json"


class Walker:
    def walk(self, experiment):
        print("Walking", experiment.name, "of", experiment.project.name)
        processes = experiment.get_all_processes()
        process_table = self.make_process_dic(processes)
        roots = []
        # print(len(process_table))
        for process in processes:
            if not process.input_samples:
                roots.append(process)
                process_table.pop(process.id)
        front = []
        for proc in roots:
            self.push_on(front, proc)
        while front:
            # print("process remaining: ", len(front))
            proc = self.pop_from(front)
            # print("for proc", proc.name)
            children = self.all_child_nodes(proc, process_table)
            # print("children count:", len(children))
            proc.children = children
            for child in children:
                child.parent = proc
                process_table.pop(child.id)
                self.push_on(front, child)
        return roots

    # def unify_roots(self, roots):
    #     header_tree = roots[0]
    #     for proc in roots[1:]:
    #         header_tree = self.merge_into_tree(header_tree, proc)
    #     return header_tree
    #
    # def merge_into_tree(self, tree, proc):
    #     if not proc:
    #         return tree
    #     if not tree:
    #         return proc
    #     if tree.id == proc.id:
    #         self.merge_attributes_into(tree, proc)
    #     match_pair_list = self.find_match_in(tree, proc)
    #     if match_pair_list:
    #         self.merge_into_tree(match_pair_list[0], match_pair_list[1])
    #     else:
    #         pass

    # def merge_attributes_into(self, tree, proc):
    #     return tree
    #
    # def find_match_in(self, tree, proc):
    #     return tree

    def print_path(self, indent, proc):
        padding = ""
        for i in range(0, indent):
            padding += "  "
        print(padding, proc.name, proc.id)
        print(padding, self.processSamplesText(proc))
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

    @staticmethod
    def processSamplesText(process):
        text = "Samples: "
        samples = process.input_samples
        if samples:
            names = []
            for s in samples:
                names.append(s.name)
            text += '(' + ','.join(names) + ')'
        else:
            text += '()'
        text += ' --> '
        samples = process.output_samples
        if samples:
            names = []
            for s in samples:
                names.append(s.name)
            text += '(' + ','.join(names) + ')'
        else:
            text += '()'
        return text

    @staticmethod
    def is_child(parent, candidate):
        for sample in parent.output_samples:
            for match in candidate.input_samples:
                if sample.id == match.id and sample.property_set_id == match.property_set_id:
                    return True
        return False

    @staticmethod
    def push_on(list, obj):
        list.append(obj)

    @staticmethod
    def pop_from(list):
        obj = list[len(list) - 1]
        list.remove(obj)
        return obj

    @staticmethod
    def make_process_dic(processes):
        table = {}
        for proc in processes:
            table[proc.id] = proc
        return table

    @staticmethod
    def find_project(project_id):
        return get_project_by_id(project_id)

    @staticmethod
    def find_experiment(project, experiment_id):
        experiments = project.get_all_experiments()
        for experiment in experiments:
            if experiment_id == experiment.id:
                return experiment
        return None


def main():
    metadata = Metadata()
    metadata.read(metadata_path)
    pid = metadata.project_id
    eid = metadata.experiment_id

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
    main()
