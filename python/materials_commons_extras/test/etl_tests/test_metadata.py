import unittest
import pytest
from os import environ
from os import path as os_path
from random import randint
from materials_commons.api import create_project, get_project_by_id
from materials_commons.api.File import File
from materials_commons.api.Directory import Directory
from materials_commons.etl.common.metadata import Metadata
from materials_commons.etl.old_input_spreadsheet import BuildProjectExperiment
from materials_commons.etl.common.meta_data_verify import MetadataVerification


class TestMetadata(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_dir_path = cls.make_test_dir_path()
        cls.test_input_file_path = os_path.join(cls.test_dir_path, "test_input.xlsx")
        cls.test_input_data_dir_path = os_path.join(cls.test_dir_path, "test_data", "data")
        cls.random_name = cls.fake_name("test")

    def test_is_setup_correctly(self):
        self.assertTrue('TEST_DATA_DIR' in environ)
        self.assertIsNotNone(self.test_dir_path)
        self.assertTrue(os_path.isdir(self.test_dir_path))
        self.assertIsNotNone(self.test_input_file_path)
        self.assertTrue(os_path.isfile(self.test_input_file_path))
        self.assertIsNotNone(self.test_input_data_dir_path)
        print("")
        print(self.test_input_data_dir_path)
        self.assertTrue(os_path.isdir(self.test_input_data_dir_path))
        self.assertIsNotNone(self.random_name)
        self.assertTrue("test" in self.random_name)

    def test_basics(self):
        project_name = self.fake_name("Test-Project-")
        experiment_name = self.fake_name("Test-Experiment-")
        project = create_project(project_name, "Project for testing metadata")
        experiment = project.create_experiment(experiment_name, "Experiment for testing metadata")
        metadata_in = Metadata()
        metadata_in.input_excel_file_path = self.test_input_file_path
        metadata_in.project_id = project.id
        metadata_in.experiment_id = experiment.id
        metadata_in.write(experiment.id)

        metadata_out = Metadata()
        metadata_out.read(experiment.id)
        self.assertEqual(metadata_in.input_excel_file_path, metadata_out.input_excel_file_path)
        self.assertEqual(metadata_in.project_id, metadata_out.project_id)
        self.assertEqual(metadata_in.experiment_id, metadata_out.experiment_id)

    @pytest.mark.skip("This tests is failing: review - TEW - July 23, 2018")
    def test_metadata_excel_input_no_files(self):
        builder = BuildProjectExperiment()
        builder.set_rename_is_ok(True)
        builder.build(self.test_input_file_path, None)
        project_id = builder.project.id
        self.assertIsNotNone(project_id)
        experiment_id = builder.experiment.id
        self.assertIsNotNone(experiment_id)

        metadata = Metadata()
        metadata.read(experiment_id)
        self.assertEqual(self.test_input_file_path, metadata.input_excel_file_path)
        self.assertEqual(project_id, metadata.project_id)
        self.assertEqual(experiment_id, metadata.experiment_id)

        project = get_project_by_id(metadata.project_id)
        self.assertIsNotNone(project)
        experiment_list = project.get_all_experiments()
        probe = None
        for experiment in experiment_list:
            if experiment.id == experiment_id:
                probe = experiment
        experiment = probe
        self.assertIsNotNone(experiment)
        processes = experiment.get_all_processes()
        process_table = {}
        for process in processes:
            process_table[process.id] = process
        missing = []
        for process_record in metadata.process_metadata:
            if not process_record['id'] in process_table:
                missing.append(process_record['id'])
        self.assertEqual(len(missing), 0)

    @pytest.mark.skip("This tests is failing: review - TEW - July 23, 2018")
    def test_metadata_excel_input_with_files(self):
        # this test relies heavily on the consistency of the test excel file
        # and the test data dir/file structure
        builder = BuildProjectExperiment()
        builder.set_rename_is_ok(True)
        builder.build(self.test_input_file_path, self.test_input_data_dir_path)
        project_id = builder.project.id
        self.assertIsNotNone(project_id)
        experiment_id = builder.experiment.id
        self.assertIsNotNone(experiment_id)

        metadata = Metadata()
        metadata.read(experiment_id)
        self.assertEqual(self.test_input_file_path, metadata.input_excel_file_path)
        self.assertEqual(project_id, metadata.project_id)
        self.assertEqual(experiment_id, metadata.experiment_id)

        verify = MetadataVerification()
        self.assertTrue(verify.verify(metadata))

        project = get_project_by_id(metadata.project_id)
        self.assertIsNotNone(project)
        experiment = verify.get_experiment(project, metadata.experiment_id)
        self.assertIsNotNone(experiment)
        processes = experiment.get_all_processes()
        process_table = verify.make_process_table(processes)
        missing = []
        for process_record in metadata.process_metadata:
            if not process_record['id'] in process_table:
                missing.append(process_record['id'])
        self.assertEqual(len(missing), 0)

        self.assertIsNotNone(metadata.input_data_dir_path)
        self.assertEquals(self.test_input_data_dir_path, metadata.input_data_dir_path)
        project.local_path = metadata.input_data_dir_path

        for process_record in metadata.process_metadata:
            files = process_record['files']
            if files:
                self.check_files(project, experiment, process_record)

    def check_files(self, project, experiment, process_record):
        files = process_record['files']
        file_list = [x.strip() for x in files.split(',')]
        for file in file_list:
            if file == 'NoDir':  # special case, directory in Excel spread sheet does not exist in data!
                continue
            path = os_path.join(project.local_path, file)
            probe = project._local_path_to_path(path)
            self.assertEqual(probe, file)
            file_or_dir = project.get_by_local_path(path)
            self.assertIsNotNone(
                file_or_dir,
                "The path, " + path + ", does not correspond to a project file or directory")
            if type(file_or_dir) is File:
                self.assertTrue(
                    os_path.isfile(path),
                    "The path, " + path + ", is expected to be a file, but is not")
            if type(file_or_dir) is Directory:
                self.assertTrue(
                    os_path.isdir(path),
                    "The path, " + path + ", is expected to be a directory, but is not")
        process = experiment.get_process_by_id(process_record["id"])
        self.assertIsNotNone(process)

    @classmethod
    def make_test_dir_path(cls):
        test_path = os_path.abspath(environ['TEST_DATA_DIR'])
        test_path = os_path.join(test_path, 'etl_test_data')
        return test_path

    @classmethod
    def fake_name(cls, prefix):
        number = "%05d" % randint(0, 99999)
        return prefix + number
