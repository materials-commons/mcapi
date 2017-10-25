import unittest
from os import environ
from os import path as os_path
from materials_commons.api import create_project, Template
from materials_commons.api import get_all_projects


class TestDemoProjectBasic(unittest.TestCase):

    def test_demo_project(self):
        project_name = "Demo Test Project"
        project_description = "A project for trying things out."
        project = self._get_project(project_name)
        if not project:
            project = create_project(
                name=project_name,
                description=project_description)
        self.assertIsNotNone(project)
        self.assertIsNotNone(project.id)
        self.assertEqual(project_name, project.name)
        self.assertTrue(project_description in project.description)

        experiment_name = "Demo Experiment"
        experiment_description = "A demo experiment generated for your use"
        experiment = self._get_experiment(project, experiment_name)
        if not experiment:
            experiment = project.create_experiment(
                name=experiment_name,
                description=experiment_description)
        self.assertIsNotNone(experiment.id)
        self.assertEqual(experiment_name, experiment.name)
        self.assertEqual(experiment_description, experiment.description)
        self.assertIsNotNone(experiment.project)
        self.assertEqual(experiment.project.id, project.id)

        process_name = "Setup_Samples"
        create_sample_process = self. \
            _get_process_with_template(experiment, process_name, Template.create)
        if not create_sample_process:
            create_sample_process = experiment.create_process_from_template(Template.create)
            create_sample_process = create_sample_process.rename(process_name)
        self.assertIsNotNone(create_sample_process)
        self.assertIsNotNone(create_sample_process.id)
        self.assertIsNotNone(create_sample_process.name)
        self.assertEqual(create_sample_process.name, process_name)
        self.assertIsNotNone(create_sample_process.process_type)
        self.assertEqual(create_sample_process.process_type, 'create')
        self.assertTrue(create_sample_process.does_transform)
        self.assertIsNotNone(create_sample_process.project)
        self.assertEqual(create_sample_process.project.id, project.id)
        self.assertIsNotNone(create_sample_process.experiment)
        self.assertEqual(create_sample_process.experiment.id, experiment.id)

        sample_name = 'Demo Sample'
        sample = self._get_output_sample_from_process(create_sample_process, sample_name)
        if not sample:
            sample = create_sample_process.create_samples(
                sample_names=[sample_name]
            )[0]
        self.assertIsNotNone(sample)
        self.assertIsNotNone(sample.name)
        self.assertIsNotNone(sample.property_set_id)
        self.assertEqual(sample.name, sample_name)

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
        self.assertIsNotNone(sample_file)
        self.assertIsNotNone(sample_file.name)
        self.assertEqual(sample_file.name, filename_for_sample)

        create_sample_process = experiment.get_process_by_id(create_sample_process.id)
        files = create_sample_process.get_all_files()
        create_sample_process.files = files

        if not self._process_has_file(create_sample_process, sample_file):
            create_sample_process.add_files([sample_file])
            create_sample_process = experiment.get_process_by_id(create_sample_process.id)
            files = create_sample_process.get_all_files()
            create_sample_process.files = files
        self.assertIsNotNone(create_sample_process.files)
        self.assertEqual(len(create_sample_process.files), 1)
        file1 = create_sample_process.files[0]
        self.assertIsNotNone(file1)
        self.assertIsNotNone(file1.id)
        self.assertEqual(file1.id, sample_file.id)

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
        self.assertEqual(measurement_out.name, measurement.name)
        composition = measurement_out
        self.assertEqual(composition.name, "Composition")
        self.assertEqual(composition.attribute, "composition")
        self.assertEqual(composition.otype, "composition")
        self.assertEqual(composition.unit, "at%")
        value_list = composition.value
        self.assertEqual(value_list[0]['element'], "Al")
        self.assertEqual(value_list[0]['value'], 94)
        self.assertEqual(value_list[1]['element'], "Ca")
        self.assertEqual(value_list[1]['value'], 1)
        self.assertEqual(value_list[2]['element'], "Zr")
        self.assertEqual(value_list[2]['value'], 5)

    # Support methods

    def _get_project(self, project_name):
        projects = get_all_projects()
        project = None
        for p in projects:
            if p.name == project_name:
                project = p
        return project

    def _get_experiment(self, project, experiment_name):
        experiments = project.get_all_experiments()
        experiment = None
        for ex in experiments:
            if ex.name == experiment_name:
                experiment = ex
        return experiment

    def _get_process_with_template(self, experiment, process_name, template_id):
        experiment = experiment.decorate_with_processes()
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
        directory_list = project.get_directory_list(directory_path)
        directory = directory_list[-1]
        if directory.shallow:
            directory = project.get_directory(directory.id)
        children = directory.get_children()
        selected_file = None
        for entry in children:
            if entry.otype == 'file' and entry.name == filename:
                selected_file = entry
        return selected_file

    def _process_has_file(self, process, file_arg):
        selected_file = None
        for check_file in process.files:
            if check_file.id == file_arg.id:
                selected_file = check_file
        return selected_file

    def _make_test_dir_path(self, file_name):
        self.assertTrue('TEST_DATA_DIR' in environ)
        test_path = os_path.abspath(environ['TEST_DATA_DIR'])
        self.assertIsNotNone(test_path)
        self.assertTrue(os_path.isdir(test_path))
        test_file = os_path.join(test_path, 'test_upload_data', file_name)
        self.assertTrue(os_path.isfile(test_file))
        return test_file
