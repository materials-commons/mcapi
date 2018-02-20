import argparse
import random
import sys

from materials_commons.api import get_all_projects, get_all_templates


class Modifier:
    def __init__(self):
        self.project = None
        self.experiment = None
        self.process_table = None
        self.template_table = None

    def modify(self):
        self.remove_a_process()
        #    self.remove_a_parameter()
        #    self.remove_a_measurement()
        self.add_a_measurement()
        self.add_a_parameter()
        self.add_a_process()

    def get_project(self, project_name):
        project = None
        project_list = get_all_projects()
        for proj in project_list:
            if proj.name == project_name:
                project = proj
                break
        self.project = project
        return project

    def get_experiment(self, experiment_name):
        project = self.project
        if not project:
            return None
        experiment = None
        experiment_list = project.get_all_experiments()
        found = []
        for exp in experiment_list:
            if exp.name == experiment_name:
                found.append(exp)
        if found:
            experiment = found[0]
        self.experiment = experiment
        self._make_process_table()
        return experiment

    def remove_a_process(self):
        process = self._pick_random_noncreate_leaf_process()
        if not process:
            print("Remove process, no non-create leaf process(!?)")
        else:
            print("Remove process:", process.name, process.id)
            del self.process_table[process.id]
            process.delete()

    def add_a_process(self):
        template_name = "Generic Measurement"
        template_id = self._get_template_id(template_name)
        process = self.experiment.create_process_from_template(template_id)
        print("New process", process.name, process.id)
        self.template_table[process.id] = process
        parent = self.find_a_process_with_output_samples()
        if parent:
            print("Found parent", parent.name)
            input_sample = parent.output_samples[0]
            print("Added as child", process.name)
            process.add_input_samples_to_process([input_sample])

    def remove_a_parameter(self):
        pass

    def add_a_parameter(self):
        process = self._pick_random_process()
        additional_parameter = {
            "name": 'fakeparam',
            "attribute": 'fakeparam',
            "otype": 'number',
            "value": 9999,
            "unit": ''
        }
        process.update_additional_setup_properties([additional_parameter])
        print("Add a parameter", additional_parameter['attribute'],
              additional_parameter['value'], additional_parameter['unit'])

    def remove_a_measurement(self):
        pass

    def add_a_measurement(self):
        process = self._pick_random_process()
        measurement_data = {
            "name": 'fake',
            "attribute": 'fake',
            "otype": 'number',
            "value": 9999,
            "is_best_measure": True,
            "unit": ''
        }
        measurement = process.create_measurement(data=measurement_data)
        measurement_property = {
            "name": measurement_data['name'],
            "attribute": measurement_data['attribute']
        }
        process.set_measurements_for_process_samples(measurement_property, [measurement])
        print("Add a measurement", measurement.attribute, measurement.value, measurement.unit)

    def holder(self):
        process = self.first_process_with_set_up(self.experiment)
        if not process:
            print("No processes with setup parameters in experiment:", self.experiment.name)
        else:
            print("Param - Process", process.name, process.id)
            if not self.remove_first_param(process):
                print("Could not remove paramter from process")

        process = self.first_process_with_measurements(self.experiment)
        if not process:
            print("No processes with measurments in experiment:", self.experiment.name)
        else:
            print("Param - Process", process.name, process.id)
            if not self.remove_first_measurement(process):
                print("Could not remove measurement from process")

    @staticmethod
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

    @staticmethod
    def remove_first_param(process):
        found = None
        for s in process.setup:
            for prop in s.properties:
                if (prop.value is not None) and (str(prop.value).strip() != ""):
                    found = prop
                    break
        if found:
            pass
        return False

    @staticmethod
    def first_process_with_measurements(experiment):
        process_list = experiment.get_all_processes()
        found = None
        for process in process_list:
            measurements = process.measurements
            if measurements:
                found = process
                break
        return found

    @staticmethod
    def remove_first_measurement(process):
        measurements = process.measurements
        found = None
        for measure in measurements:
            found = measure
            break
        if found:
            pass
        return False

    def find_a_process_with_output_samples(self):
        for process_id in self.process_table:
            process = self.process_table[process_id]
            if process.output_samples:
                print("Found process with output samples:", process.name)
                return process
        print("Process with output samples not found")
        return None

    def _pick_random_process(self):
        table = self.process_table
        process = random.choice(list(table.items()))[1]
        return process

    def _pick_random_noncreate_leaf_process(self):
        process_list = []
        process = None
        for process_id in self.process_table:
            process = self.process_table[process_id]
            if process.category == 'create_sample':
                continue
            if not process.output_samples:
                process_list.append(process)
            elif not self._has_a_child_process(process):
                process_list.append(process)
        if not process_list:
            return process
        if process_list:
            process = random.choice(process_list)
        return process

    def _has_a_child_process(self, probe_process):
        outputs = probe_process.output_samples
        all_processes = [item[1] for item in list(self.process_table.items())]
        for sample in outputs:
            for process in all_processes:
                if process.id == probe_process.id:
                    continue
                if sample.id in [x.id for x in process.input_samples]:
                    return True
        return False

    def _make_template_table(self):
        template_list = get_all_templates()
        table = {}
        for template in template_list:
            table[template.id] = template
        self.template_table = table

    def _get_template_id(self, match):
        if not self.template_table:
            self._make_template_table()
        table = self.template_table
        found_id = None
        for key in table:
            if match in key:
                found_id = key
        return found_id

    def _make_process_table(self):
        processes = self.experiment.get_all_processes()
        table = {}
        for process in processes:
            table[process.id] = process
        self.process_table = table


def main(project_name, experiment_name):
    work = Modifier()

    project = work.get_project(project_name)
    if not project:
        print("Could not find project", project_name)
        exit(-1)
    print("Project", project.name, project.id)

    experiment = work.get_experiment(experiment_name)
    if not experiment:
        print("Count not find experiment:", experiment_name)
        exit(-1)
    print("Experiment", experiment.name, experiment.id)

    work.modify()


if __name__ == '__main__':
    argv = sys.argv
    parser = argparse.ArgumentParser()
    parser.add_argument('proj', type=str, help="Project Name")
    parser.add_argument('exp', type=str, help="Experiment Name")
    args = parser.parse_args(argv[1:])
    main(args.proj, args.exp)
