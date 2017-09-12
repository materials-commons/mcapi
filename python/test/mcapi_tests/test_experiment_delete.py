import unittest
from os import environ
from os import path as os_path
from random import randint
import demo_project as demo
import assert_helper as aid


def _fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix+number

class TestExperimentDelete(unittest.TestCase):

    def test_delete(self):
        self.helper = aid.AssertHelper(self)

        self.old_experiment = None
        self.new_experiment = None
        project = self._build_project()
        self.assertIsNotNone(self.old_experiment)
        self.assertIsNotNone(self.new_experiment)

        project_name = self.test_project_name

        self.helper.confirm_demo_project_content(project, project_name, 2)

        experiment = self.old_experiment
        self.assertIsNotNone(experiment)
        self.assertEqual(experiment.otype,"experiment")
        self.assertIsNotNone(experiment.project)
        self.assertIsNotNone(experiment.project.id)
        self.assertEqual(experiment.project,project)
        self.assertEqual(experiment.project.id,project.id)

        deleted_experiment = experiment.delete()

        self.assertEqual(len(deleted_experiment.delete_tally.datasets), 0)
        self.assertEqual(len(deleted_experiment.delete_tally.best_measure_history), 0)
        self.assertEqual(len(deleted_experiment.delete_tally.processes), 0)
        self.assertEqual(len(deleted_experiment.delete_tally.samples), 0)
        self.assertEqual(len(deleted_experiment.delete_tally.experiment_notes), 0)
        self.assertEqual(len(deleted_experiment.delete_tally.experiment_task_processes), 0)
        self.assertEqual(len(deleted_experiment.delete_tally.experiment_tasks), 1)
        self.assertEqual(len(deleted_experiment.delete_tally.notes), 0)
        self.assertEqual(len(deleted_experiment.delete_tally.reviews), 0)
        self.assertEqual(len(deleted_experiment.delete_tally.experiments), 1)

    def test_delete_dry_run(self):
        self.helper = aid.AssertHelper(self)

        self.old_experiment = None
        self.new_experiment = None
        project = self._build_project()
        self.assertIsNotNone(self.old_experiment)
        self.assertIsNotNone(self.new_experiment)

        project_name = self.test_project_name

        self.helper.confirm_demo_project_content(project, project_name, 2)

        experiment = self.old_experiment
        self.assertIsNotNone(experiment)
        self.assertEqual(experiment.otype,"experiment")
        self.assertIsNotNone(experiment.project)
        self.assertIsNotNone(experiment.project.id)
        self.assertEqual(experiment.project,project)
        self.assertEqual(experiment.project.id,project.id)

        deleted_experiment = experiment.delete(dry_run=True)

        self.assertEqual(len(deleted_experiment.delete_tally.datasets), 0)
        self.assertEqual(len(deleted_experiment.delete_tally.best_measure_history), 1)
        self.assertEqual(len(deleted_experiment.delete_tally.processes), 5)
        self.assertEqual(len(deleted_experiment.delete_tally.samples), 7)
        self.assertEqual(len(deleted_experiment.delete_tally.experiment_notes), 0)
        self.assertEqual(len(deleted_experiment.delete_tally.experiment_task_processes), 0)
        self.assertEqual(len(deleted_experiment.delete_tally.experiment_tasks), 1)
        self.assertEqual(len(deleted_experiment.delete_tally.notes), 0)
        self.assertEqual(len(deleted_experiment.delete_tally.reviews), 0)
        self.assertEqual(len(deleted_experiment.delete_tally.experiments), 1)

        self.assertEqual(deleted_experiment.delete_tally.experiments[0],self.old_experiment.id)

        experiments = project.get_all_experiments()
        self.assertEqual(len(experiments),2)

        old_experiment = None
        new_experiment = None
        for experiment in experiments:
            if experiment.id == self.old_experiment.id:
                old_experiment = experiment
            if experiment.id == self.new_experiment.id:
                new_experiment = experiment

        self.assertIsNotNone(old_experiment)
        self.assertIsNotNone(new_experiment)

        self.helper.confirm_demo_project_content(project, project_name, 2)

    def test_delete_fully(self):
        self.helper = aid.AssertHelper(self)

        self.old_experiment = None
        self.new_experiment = None
        project = self._build_project()
        self.assertIsNotNone(self.old_experiment)
        self.assertIsNotNone(self.new_experiment)

        project_name = self.test_project_name

        self.helper.confirm_demo_project_content(project, project_name, 2)

        experiment = self.old_experiment
        self.assertIsNotNone(experiment)
        self.assertEqual(experiment.otype,"experiment")
        self.assertIsNotNone(experiment.project)
        self.assertIsNotNone(experiment.project.id)
        self.assertEqual(experiment.project,project)
        self.assertEqual(experiment.project.id,project.id)

        deleted_experiment = experiment.delete(delete_processes_and_samples=True)

        self.assertEqual(len(deleted_experiment.delete_tally.datasets), 0)
        self.assertEqual(len(deleted_experiment.delete_tally.best_measure_history), 1)
        self.assertEqual(len(deleted_experiment.delete_tally.processes), 5)
        self.assertEqual(len(deleted_experiment.delete_tally.samples), 7)
        self.assertEqual(len(deleted_experiment.delete_tally.experiment_notes), 0)
        self.assertEqual(len(deleted_experiment.delete_tally.experiment_task_processes), 0)
        self.assertEqual(len(deleted_experiment.delete_tally.experiment_tasks), 1)
        self.assertEqual(len(deleted_experiment.delete_tally.notes), 0)
        self.assertEqual(len(deleted_experiment.delete_tally.reviews), 0)
        self.assertEqual(len(deleted_experiment.delete_tally.experiments), 1)
        self.assertEqual(deleted_experiment.delete_tally.experiments[0],self.old_experiment.id)

        experiments = project.get_all_experiments()
        self.assertEqual(len(experiments),1)
        self.assertEqual(experiments[0].id,self.new_experiment.id)

    def _build_project(self):

        project_name = _fake_name("ExpDeleteTest")
        print("")
        print("Project name: " + project_name)

        self.test_project_name = project_name

        builder = demo.DemoProject(self._make_test_dir_path())

        table = builder._make_template_table()
        self.assertIsNotNone(builder._template_id_with(table, 'Create'))
        self.assertIsNotNone(builder._template_id_with(table, 'Sectioning'))
        self.assertIsNotNone(builder._template_id_with(table, 'EBSD SEM'))
        self.assertIsNotNone(builder._template_id_with(table, 'EPMA'))

        project = builder.build_project()

        name = 'Demo Project'
        self.helper.confirm_demo_project_content(project, name, 1)

        project = project.rename(project_name)
        self.assertEqual(project.name, project_name)

        experiments = project.get_all_experiments()
        old_experiment_id = experiments[0].id

        new_experiment_name = "Test: Additional Experiment"
        project = self.helper.add_additional_experiment(project, new_experiment_name)

        experiments = project.get_all_experiments()
        old_experiment = None
        new_experiment = None
        for experiment in experiments:
            if experiment.id == old_experiment_id:
                old_experiment = experiment
            if experiment.name == new_experiment_name:
                new_experiment = experiment

        self.assertIsNotNone(old_experiment)
        self.assertIsNotNone(new_experiment)
        self.old_experiment = old_experiment
        self.new_experiment = new_experiment

        return project

    def _make_test_dir_path(self):
        self.assertTrue('TEST_DATA_DIR' in environ)
        test_path = os_path.abspath(environ['TEST_DATA_DIR'])
        self.assertIsNotNone(test_path)
        self.assertTrue(os_path.isdir(test_path))
        test_path = os_path.join(test_path, 'demo_project_data')
        self.assertIsNotNone(test_path)
        self.assertTrue(os_path.isdir(test_path))
        return test_path

