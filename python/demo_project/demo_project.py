from os import environ
from os import path as os_path
from mcapi import create_project, Template
from mcapi import list_projects
from mcapi import get_process_from_id


class DemoProject:
    def __init__(self):
        pass

    def build_project(self):
        project_name = "Demo Project"
        project_description = "A project for trying things out."
        project = self._get_project(project_name)
        if not project:
            project = create_project(
                name=project_name,
                description=project_description)

        experiment_name = "Demo Experiment"
        experiment_description = "A demo experiment generated for your use"
        experiment = self._get_experiment(project, experiment_name)
        if not experiment:
            experiment = project.create_experiment(
                name=experiment_name,
                description=experiment_description)

        process_name = "Setup_Samples"
        create_sample_process = self. \
            _get_process_with_template(experiment, process_name, Template.create)
        if not create_sample_process:
            create_sample_process = experiment.create_process_from_template(Template.create)
            create_sample_process.add_name(process_name)

        sample_name = 'Demo Sample'
        sample = self._get_output_sample_from_process(create_sample_process, sample_name)
        if not sample:
            sample = create_sample_process.create_samples(
                sample_names=[sample_name]
            )[0]

        filepath_for_sample = self._make_test_dir_path('sem.tif')
        directory_path = "/FilesForSample"
        filename_for_sample = "SampleFile.tif"
        sample_file = self._get_file_from_project(project, directory_path, filename_for_sample)
        if not sample_file:
            sample_file = project.add_file_using_directory(
                project.add_directory(directory_path),
                filename_for_sample,
                filepath_for_sample
            )

        create_sample_process = get_process_from_id(project, experiment, create_sample_process.id)
        if not self._process_has_file(create_sample_process, sample_file):
            create_sample_process.add_files([sample_file])
            create_sample_process = get_process_from_id(project, experiment, create_sample_process.id)

        measurement_data = {
            "name": "Composition",
            "attribute": "composition",
            "otype": "composition",
            "unit": "at%",
            "value": [
                {"element": "Al", "value": 94},
                {"element": "Ca", "value": 1},
                {"element": "Zr", "value": 5}],
            "is_best_measure": True
        }
        measurement = create_sample_process.create_measurement(data=measurement_data)
        measurement_property = {
            "name": "Composition",
            "attribute": "composition"
        }
        create_sample_process_updated = \
            create_sample_process.set_measurements_for_process_samples(
                measurement_property, [measurement])
        measurement_out = create_sample_process_updated.measurements[0]
        composition = measurement_out
        value_list = composition.value

    # Support methods

    def _get_project(self, project_name):
        projects = list_projects()
        project = None
        for p in projects:
            if p.name == project_name:
                project = p
        return project

    def _get_experiment(self, project, experiment_name):
        experiments = project.fetch_experiments()
        experiment = None
        for ex in experiments:
            if (ex.name == experiment_name):
                experiment = ex
        return experiment

    def _get_process_with_template(self, experiment, process_name, template_id):
        experiment = experiment.fetch_and_add_processes()
        processes = experiment.processes
        selected_process = None
        for process in processes:
            if template_id == process.template_id and process_name == process.name:
                selected_process = process
        return selected_process

    def _get_output_sample_from_process(self, process, sample_name):
        samples = process.output_samples
        selected_sample = None
        for sample in samples:
            if sample.name == sample_name:
                selected_sample = sample
        return selected_sample

    def _get_file_from_project(self, project, directory_path, filename):
        directory = project.get_directory(directory_path)
        children = directory.get_children()
        selected_file = None
        for entry in children:
            if entry.otype == 'file' and entry.name == filename:
                selected_file = entry
        return selected_file

    def _process_has_file(self, process, file):
        selected_file = None
        for check_file in process.files:
            if check_file.id == file.id:
                selected_file = check_file
        return selected_file

    def _make_data_dir_path(self, file_name):
        # self.assertTrue('TEST_DATA_DIR' in environ)
        test_path = os_path.abspath(environ['DEMO_DATA_DIR'])
        test_file = os_path.join(test_path, 'test_upload_data', file_name)
        return test_file
