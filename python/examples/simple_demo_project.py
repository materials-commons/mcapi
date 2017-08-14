from mcapi import create_project, get_all_templates
import os.path

local_path = './example_data/simple_demo_data'
BASE_DIRECTORY = os.path.abspath(local_path)

class SimpleDemoBuilder:
    def __init__(self):
        self.template_table = self._make_template_table()

    def buildProject(self):
        name = "My Simple Project"
        description = "A simple demo project from a script"
        project = create_project(name, description)
        self.project = project

        experiment_name = "My experiment"
        description = "A sample experiment"
        experiment = project.create_experiment(experiment_name, description)
        self.experiment = experiment

        template_id = self._template_id_with(self.template_table, "Create Sample")
        create_sample_process = experiment.create_process_from_template(template_id)
        create_sample_process.rename("Create my sample")

        sample_name = "Sample"
        samples = create_sample_process.create_samples([sample_name])
        sample = samples[0]

        template_id = self._template_id_with(self.template_table, "Low Cycle Fatigue")
        transform_process = experiment.create_process_from_template(template_id)
        transform_process.rename("Subject to bending")

        transform_process.add_input_samples_to_process([sample])
        transform_process.decorate_with_output_samples()
        transformed_sample = transform_process.output_samples[0]

        template_id = self._template_id_with(self.template_table, "SEM")
        measurement_process = experiment.create_process_from_template(template_id)
        measurement_process.rename("Observe with SEM")

        measurement_process.add_input_samples_to_process([transformed_sample])

        project.local_path = BASE_DIRECTORY
        project.add_file_by_local_path(os.path.join(project.local_path,"example_data/SEM.png"))

    def _make_template_table(self):
        template_list = get_all_templates()
        table = {}
        for template in template_list:
            table[template.id] = template
        return table

    def _template_id_with(self, table, match):
        found_id = None
        for key in table:
            if match in key:
                found_id = key
        return found_id


builder = SimpleDemoBuilder()
builder.buildProject()

print "Built simple demo project with name = " + builder.project.name
print "With processes..."
processes = builder.project.get_all_processes()
for process in processes:
    print "    " + process.name
