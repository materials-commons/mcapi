import unittest
import sys
from os import environ
from os import path as os_path
import materials_commons_extras.demo_project.demo_project as demo


class TestDemoProject(unittest.TestCase):
    def test_build_demo_project(self):

        # Expected test values
        project_name = 'Demo Project'
        experiment_name = "Demo: Microsegregation in HPDC L380"
        sample_names = [
            'l380', 'L124', 'L124 - 2mm plate', 'L124 - 3mm plate',
            'L124 - 5mm plate', 'L124 - 5mm plate - 3ST', 'L124 - tensil bar, gage'
        ]
        process_names = [
            'Lift 380 Casting Day  # 1', 'Casting L124', 'Sectioning of Casting L124',
            'EBSD SEM Data Collection - 5 mm plate', 'EPMA Data Collection - 5 mm plate - center'
        ]

        builder = demo.DemoProject(self._make_test_dir_path())

        if (builder.does_project_exist()):
            project = builder.get_existing_project()
            project.rename("Set aside", "Forcing existing demo project to be set aside")

        table = builder._make_template_table()
        self.assertIsNotNone(builder._template_id_with(table, 'Create'))
        self.assertIsNotNone(builder._template_id_with(table, 'Sectioning'))
        self.assertIsNotNone(builder._template_id_with(table, 'EBSD SEM'))
        self.assertIsNotNone(builder._template_id_with(table, 'EPMA'))

        project = builder.build_project()

        self.assertIsNotNone(project)
        experiments = project.get_all_experiments()
        self.assertEqual(len(experiments), 1)
        experiment = experiments[0]
        self.assertIsNotNone(experiment)
        self.assertIsNotNone(experiment.project)
        self.assertIsNotNone(experiment.processes)
        self.assertEqual(project.id, experiment.project.id)
        self.assertEqual(project.name, project_name)
        self.assertEqual(experiment.name, experiment_name)

        self.assertEqual(len(experiment.processes), len(process_names))
        for name in process_names:
            found_process = None
            for process in experiment.processes:
                if name == process.name:
                    found_process = process
            self.assertIsNotNone(found_process, "Expecting to find process.name == " + name)

        self.assertEqual(len(experiment.samples), len(sample_names))
        for name in sample_names:
            found_sample = None
            for sample in experiment.samples:
                if name == sample.name:
                    found_sample = sample
            self.assertIsNotNone(found_sample, "Expecting to find sample.name == " + name)

        project_directory_path = "/FilesForSample"

        filename_list = [
            'LIFT Specimen Die.jpg',
            'L124_photo.jpg',
            'LIFT HPDC Samplesv3.xlsx',
            'Measured Compositions_EzCast_Lift380.pptx',
            'GSD_Results_L124_MC.xlsx',
            'Grain_Size_EBSD_L380_comp_5mm.tiff',
            'Grain_Size_EBSD_L380_comp_core.tiff',
            'Grain_Size_EBSD_L380_comp_skin.tiff',
            'Grain_Size_Vs_Distance.tiff',
            'L124_plate_5mm_TT_GF2.txt',
            'L124_plate_5mm_TT_IPF.tif',
            'EPMA_Analysis_L124_Al.tiff',
            'EPMA_Analysis_L124_Cu.tiff',
            'EPMA_Analysis_L124_Si.tiff',
            'ExperimentData_Lift380_L124_20161227.docx',
            'Samples_Lift380_L124_20161227.xlsx'
        ]

        directory = project.get_directory_list(project_directory_path)[-1]
        self.assertEqual(directory.otype, 'directory')
        self.assertEqual(directory.path, project.name + project_directory_path)

        project_files = directory.get_children()
        self.assertEqual(len(project_files), len(filename_list))
        for name in filename_list:
            found_file = None
            for the_file in project_files:
                if name == the_file.name:
                    found_file = the_file
            self.assertIsNotNone(found_file, "Expecting to find file.name == " + name)

        experiment = project.get_all_experiments()[0]
        experiment = experiment.decorate_with_processes()
        experiment = experiment.decorate_with_samples()
        processes = experiment.processes

        processes_reordered = []
        for name in process_names:
            for probe in processes:
                if name == probe.name:
                    processes_reordered.append(probe)
        self.assertEqual(len(processes), len(processes_reordered))
        processes = processes_reordered

        for process in processes:
            process.decorate_with_output_samples()
            files = process.get_all_files()
            process.files = files

        process_file_list = [
            [0, 2, 3], [0, 1], [1], [4, 5, 6, 7, 8, 9, 10], [11, 12, 13, 14, 15]
        ]

        process_index = 0
        for file_index_list in process_file_list:
            process = processes[process_index]
            for file_index in file_index_list:
                name = filename_list[file_index]
                found_file = None
                for the_file in process.files:
                    if name == the_file.name:
                        found_file = the_file
                error = "In process " + process.name + ": expecting to find file.name == " + name
                self.assertIsNotNone(found_file, error)
            process_index += 1

    def _make_test_dir_path(self):
        self.assertTrue('TEST_DATA_DIR' in environ)
        test_path = os_path.abspath(environ['TEST_DATA_DIR'])
        self.assertIsNotNone(test_path)
        self.assertTrue(os_path.isdir(test_path))
        test_path = os_path.join(test_path, 'demo_project_data')
        self.assertIsNotNone(test_path)
        self.assertTrue(os_path.isdir(test_path))
        return test_path
