import unittest
from random import randint
from os.path import getsize
from pathlib import Path
from mcapi import create_project, Template
from mcapi import create_file_with_upload

def fake_name(prefix):
    number="%05d" % randint(0,99999)
    return prefix+number

class TestFileInProject(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.project_name = fake_name("Project - ")
        self.project_description = "Test project, " + self.project_name
        self.experiment_name = fake_name("Experiment-")
        self.experiment_description = "a test experiment generated from api"
        self.filepath = 'test/test_upload_data/fractal.jpg'
        self.test_dir_path = "/testDir1/testdir2/testdir3"
        self.filename = "test.jpg"

        self.project = create_project(
            name = self.project_name,
            description = self.project_description)

        experiment = self.project.create_experiment(
            name = self.experiment_name,
            description = self.experiment_description)

        self.process = experiment.create_process_from_template(Template.create)

        self.test_dir = self.project.add_directory(self.testDirPath)
        self.file = self.project.add_file_using_directory(
            self.test_dir, self.filename, self.filepath)

        path = Path(self.filepath)
        self.file_name = path.parts[-1]
        input_path = str(path.absolute())
        self.byte_count = getsize(input_path)

        self.file = self.project.add_file_using_directory(self.rootDir, self.file_name, input_path)

    def test_is_setup_correctly(self):
        self.assertIsNotNone(self.project.id)
        self.assertEqual(self.project_name,self.project.name)
        self.assertEqual(self.project_description,self.project.description)

        path1 = "/" + self.testDir.name.split("/", 1)[1]
        path2 = self.testDirPath
        if path2.endswith("/"): path2 = path2[:-1]
        self.assertEqual(path1, path2)

        self.assertIsNotNone(self.process.process_type)
        self.assertEqual(self.process.process_type, 'create')
        self.assertTrue(self.process.does_transform)

        file = self.file
        byte_count = self.byte_count
        self.assertIsNotNone(file)
        self.assertEqual(file.size, byte_count)
        found = None
        decendents = self.rootDir.get_children()
        for one in decendents:
            if (one._type == 'file') and (one.name == self.file_name):
                found = one
        self.assertIsNotNone(found)
        self.assertEqual(found.size, byte_count)
        self.assertEqual(file.id,found.id)

    def test_add_file_to_process(self):
        files1 = [file]
        files2 = self.process.add_files([file])

        self.assertEqual(files1[0].id,files2[0].id)

        files2 = self.process.get_files()
        self.assertEqual(files1[0].id,files2[0].id)