from materials_commons.api import Template


class AssertHelper():

    def __init__(self, tester):
        self.tester = tester

    def confirm_demo_project_content(self, project, name, number_of_experiments):

        # Expected test values
        project_name = name
        experiment_name = "Demo: Microsegregation in HPDC L380"
        sample_names = [
            'l380', 'L124', 'L124 - 2mm plate', 'L124 - 3mm plate',
            'L124 - 5mm plate', 'L124 - 5mm plate - 3ST', 'L124 - tensil bar, gage'
        ]
        process_names = [
            'Lift 380 Casting Day  # 1', 'Casting L124', 'Sectioning of Casting L124',
            'EBSD SEM Data Collection - 5 mm plate', 'EPMA Data Collection - 5 mm plate - center'
        ]

        experiment = self._get_experiment(project, experiment_name)
        self.tester.assertIsNotNone(experiment)
        self.tester.assertIsNotNone(experiment)
        self.tester.assertIsNotNone(experiment.project)
        self.tester.assertIsNotNone(experiment.processes)
        self.tester.assertEqual(project.id, experiment.project.id)
        self.tester.assertEqual(project.name, project_name)
        self.tester.assertEqual(experiment.name, experiment_name)

        self.tester.assertEqual(len(experiment.processes), len(process_names))
        for name in process_names:
            found_process = None
            for process in experiment.processes:
                if name == process.name:
                    found_process = process
            self.tester.assertIsNotNone(found_process, "Expecting to find process.name == " + name)

        self.tester.assertEqual(len(experiment.samples), len(sample_names))
        for name in sample_names:
            found_sample = None
            for sample in experiment.samples:
                if name == sample.name:
                    found_sample = sample
            self.tester.assertIsNotNone(found_sample, "Expecting to find sample.name == " + name)

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
        self.tester.assertEqual(directory.otype, 'directory')
        self.tester.assertEqual(directory.path, project.name + project_directory_path)

        project_files = directory.get_children()
        self.tester.assertEqual(len(project_files), len(filename_list))
        for name in filename_list:
            found_file = None
            for file in project_files:
                if name == file.name:
                    found_file = file
            self.tester.assertIsNotNone(found_file, "Expecting to find file.name == " + name)

        experiment = self._get_experiment(project, experiment_name)
        self.tester.assertIsNotNone(experiment)

        experiment = experiment.decorate_with_processes()
        experiment = experiment.decorate_with_samples()
        processes = experiment.processes

        processes_reordered = []
        for name in process_names:
            for probe in processes:
                if name == probe.name:
                    processes_reordered.append(probe)
        self.tester.assertEqual(len(processes), len(processes_reordered))
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
                for file in process.files:
                    if name == file.name:
                        found_file = file
                error = "In process " + process.name + ": expecting to find file.name == " + name
                self.tester.assertIsNotNone(found_file, error)
            process_index += 1

    def add_additional_experiment(self, project, experiment_name):

        experiment_description = "A secondary demo experiment"
        experiment = self._get_experiment(project, experiment_name)
        if not experiment:
            experiment = project.create_experiment(
                name=experiment_name,
                description=experiment_description)
        self.tester.assertIsNotNone(experiment.id)
        self.tester.assertEqual(experiment_name, experiment.name)
        self.tester.assertEqual(experiment_description, experiment.description)
        self.tester.assertIsNotNone(experiment.project)
        self.tester.assertEqual(experiment.project.id, project.id)

        process_name = "Setup_Samples"
        create_sample_process = self. \
            _get_process_with_template(experiment, process_name, Template.create)
        if not create_sample_process:
            create_sample_process = experiment.create_process_from_template(Template.create)
            create_sample_process = create_sample_process.rename(process_name)
        self.tester.assertIsNotNone(create_sample_process)
        self.tester.assertIsNotNone(create_sample_process.id)
        self.tester.assertIsNotNone(create_sample_process.name)
        self.tester.assertEqual(create_sample_process.name, process_name)
        self.tester.assertIsNotNone(create_sample_process.process_type)
        self.tester.assertEqual(create_sample_process.process_type, 'create')
        self.tester.assertTrue(create_sample_process.does_transform)
        self.tester.assertIsNotNone(create_sample_process.project)
        self.tester.assertEqual(create_sample_process.project.id, project.id)
        self.tester.assertIsNotNone(create_sample_process.experiment)
        self.tester.assertEqual(create_sample_process.experiment.id, experiment.id)

        sample_name = 'Demo Sample'
        sample = self._get_output_sample_from_process(create_sample_process, sample_name)
        if not sample:
            sample = create_sample_process.create_samples(
                sample_names=[sample_name]
            )[0]
        self.tester.assertIsNotNone(sample)
        self.tester.assertIsNotNone(sample.name)
        self.tester.assertIsNotNone(sample.property_set_id)
        self.tester.assertEqual(sample.name, sample_name)

        return project

    def _get_experiment(self, project, experiment_name):
        experiments = project.get_all_experiments()
        experiment = None
        for ex in experiments:
            if (ex.name == experiment_name):
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
