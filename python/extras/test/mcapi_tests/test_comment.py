import unittest
from os import environ
from os import path as os_path
from random import randint
from materials_commons.api import create_project, get_all_templates
from materials_commons.api import Template
import extras.demo_project.demo_project as demo
from .assert_helper import AssertHelper

# for test-only dataset - normally datasets are not created through API!
from materials_commons.api import __api as api


class TestComment(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_dir_path = cls.make_test_dir_path()
        if cls.test_dir_path:
            cls.project = cls.build_project(cls.test_dir_path)
            title = "Test Datase - comments test"
            description = "A dataset for testing comments - project: " + cls.project.name
            cls.experiment = cls.project.get_all_experiments()[0]
            cls.dataset = api.create_dataset(cls.project.id, cls.experiment.id, title, description)
            cls.dataset_id = cls.dataset['id']
            processes = cls.experiment.get_all_processes()
            for process in processes:
                api.add_process_to_dataset(cls.project.id, cls.experiment.id, cls.dataset_id, process.id)
            cls.dataset = api.publish_dataset(cls.project.id, cls.experiment.id, cls.dataset_id)

    def test_is_setup_correctly(self):
        self.assertTrue('TEST_DATA_DIR' in environ)
        self.assertIsNotNone(self.test_dir_path)
        self.assertTrue(os_path.isdir(self.test_dir_path))
        self.assertIsNotNone(self.project)
        self.assertIsNotNone(self.project.name)
        self.assertIsNotNone(self.project.id)
        self.assertIsNotNone(self.experiment)
        self.assertIsNotNone(self.experiment.id)
        self.assertIsNotNone(self.dataset)
        self.assertIsNotNone(self.dataset_id)
        self.assertTrue(self.dataset['published'])

    def test_can_add_comment_to_dataset(self):
        pass

    @classmethod
    def build_project(cls, test_dir_path):
        project_name = cls.fake_name("ProjectForCommentTest")
        print("")
        print("Project name: " + project_name)

        builder = demo.DemoProject(test_dir_path)
        project = builder.build_project()
        project = project.rename(project_name)

        return project

    @classmethod
    def make_test_dir_path(cls):
        test_path = os_path.abspath(environ['TEST_DATA_DIR'])
        test_path = os_path.join(test_path, 'demo_project_data')
        return test_path

    @classmethod
    def fake_name(cls, prefix):
        number = "%05d" % randint(0, 99999)
        return prefix + number


