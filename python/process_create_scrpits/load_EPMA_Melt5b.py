import openpyxl
import datetime
from mcapi import create_project, get_all_templates

# Excel Spreadsheet, from Tracy: ./input_data/EPMA_Melt5b_MC_Demo.xlsx
# meaning of values are hardcoded
# A - ignore
# B - sample name - first time sample/gemoentry/location is hit, defines a sample type, location
# C, D - ignore
# E - sample casting geometry
# F-H - sample location
#     F - along width
#     G - along thickness
#     H - location
# I-Q - measurement values
#     I - reference standard
#     J - number of points sampled
#     K,L - number of good points using two standards of "goodness": 98-101 and 98-100.5
#     M,N - the accumulated measurement value for each goodness set
#     O - judgment of overall quailty
#     P,Q - start row and end row for the points collected
# R - results file(s) name ([name].xlsx and [name].txt)


class WorkflowBuilder:
    def parse_sheet(self,sheet):
        workflow_list = []
        for row in sheet.iter_rows(min_row=2):
            values = []
            for cell in row:
                values.append(cell.value)
            workflow_list.append(
                {
                    'material': values[1],
                    'geometry': values[4],
                    "width": values[5],
                    "thickness": values[6],
                    "location": values[7],
                    "standard": values[8],
                    "points": values[9],
                    "goodpoint_101": values[10],
                    "goodpoint_100p5": values[11],
                    "fg_101": values[12],
                    "fg_100p5": values[13],
                    "quality": values[14],
                    "start_row": values[15],
                    "end_row": values[16],
                    "data_file": values[17]
                }
            )


        time_stamp = '%s' % datetime.datetime.now()
        project_name = "Example-From-Script: " + time_stamp
        project_description = "Example workflow, created from script on " + time_stamp
        project = create_project(project_name,project_description)

        experiment = project.create_experiment("EPMA-Melt5b","EPMA measurements of Melt5b samples")

        template_table = self._make_template_table()

        create_processes = {}
        section_processes = {}

        for workflow in workflow_list:

            create_process_name = 'Create ' + workflow["material"]
            create_process_output_sample_name = workflow["material"]
            section_process_name = 'Section ' + workflow["material"]
            section_process_output_sample_name = workflow["material"] + "::" + workflow['geometry']
            epma_process_name = 'EPMA Data Collection - ' \
                                + workflow['geometry'] + ' - ' + workflow['location']

            if not create_process_name in create_processes:
                template_id = self._template_id_with(template_table, 'Create Samples')
                process = experiment.create_process_from_template(template_id)
                process.rename(create_process_name)
                samples = process.create_samples(sample_names=[create_process_output_sample_name])
                create_processes[create_process_name] = {
                    'process' : process,
                    'sample' : samples[0]
                }

            measurement_input_sample = None
            if not section_process_name in section_processes:
                template_id = self._template_id_with(template_table, 'Sectioning')
                process = experiment.create_process_from_template(template_id)
                process.rename(section_process_name)
                samples = process.create_samples(sample_names=[section_process_output_sample_name])
                process_and_sample = create_processes[create_process_name]
                create_sample_output = process_and_sample['sample']
                process.add_input_samples_to_process([create_sample_output])
                section_output_samples = {}
                section_output_samples[section_process_output_sample_name] = samples[0]
                section_processes[section_process_name] = {
                    'process': process,
                    'samples': section_output_samples
                }
                measurement_input_sample = samples[0]
            else:
                process_and_samples = section_processes[section_process_name]
                samples = process_and_samples['samples']
                if not section_process_output_sample_name in samples:
                    process = process_and_samples['process']
                    section_samples = process.create_samples(sample_names=[section_process_output_sample_name])
                    process_and_samples['samples'][section_process_output_sample_name] = section_samples[0]
                measurement_input_sample = process_and_samples['samples'][section_process_output_sample_name]

            template_id = self._template_id_with(template_table, 'EPMA')
            process = experiment.create_process_from_template(template_id)
            process.rename(epma_process_name)
            process.add_input_samples_to_process([measurement_input_sample])

        print project_name

    # Support methods

    def _make_template_table(self):
        template_list = get_all_templates()
        table = {}
        for template in template_list:
            table[template.id] = template
        return table

    def _template_id_with(self,table,match):
        found_id = None
        for key in table:
            if match in key:
                found_id = key
        return found_id

    def _get_or_create_process(self, experiment, process_name, template_id):
        experiment = experiment.decorate_with_processes()
        processes = experiment.processes
        selected_process = None
        for process in processes:
            if template_id == process.template_id and process_name == process.name:
                selected_process = process
        process = selected_process
        if not process:
            process = experiment.create_process_from_template(template_id)
            process.rename(process_name)
        return process

    def _get_or_create_output_sample_from_process(self, process, sample_names):
        samples = process.output_samples
        selected_samples = []
        for sample in samples:
            if sample.name in sample_names:
                selected_samples.append(sample)
        samples = selected_samples
        if not samples:
            samples = process.create_samples(
                sample_names=sample_names
            )
        return samples


def main():
    wb = openpyxl.load_workbook(filename='input_data/EPMA_Melt5b_MC_Demo.xlsx',read_only=True)
    ws = wb['Sheet1']
    process_by_row_list = WorkflowBuilder().parse_sheet(ws)


if __name__ == '__main__':
    main()

