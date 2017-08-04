from mcapi import create_project, get_all_templates

class SimpleDemoBuilder:

    def __init__(self,name):
        self.name = name
        self.template_table = self._make_template_table()

    def buildProject(self):
        description = "A simple demo project from a script"
        project = create_project(self.name,description)
        self.project = project

        experiment_name = "My experiment"
        description = "An single experiment"
        experiment = project.create_experiment(experiment_name, description)
        self.experiment = experiment

        template_id = self._template_id_with(self.template_table,"Create Sample")
        create_sample_process = experiment.create_process_from_template(template_id)
        create_sample_process.rename("Create my sample")

        template_id = self._template_id_with(self.template_table,"Low Cycle Fatigue")
        transform_process = experiment.create_process_from_template(template_id)
        transform_process.rename("Subject to bending")

        template_id = self._template_id_with(self.template_table, "SEM")
        measurement_process = experiment.create_process_from_template(template_id)
        measurement_process.rename("Observe with SEM")

        sample_name = "Sample"
        samples = create_sample_process.create_samples([sample_name])
        sample = samples[0]

        transform_process.add_input_samples_to_process([sample])
        transform_process.decorate_with_output_samples()
        transformed_sample = transform_process.output_samples[0]

        measurement_process.add_input_samples_to_process([transformed_sample])

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


builder = SimpleDemoBuilder("My Simple Project")
builder.buildProject()

print "Built simple demo project with name = " + builder.project.name
print "With processes..."
processes = builder.project.get_all_processes()
for process in processes:
    print "    " + process.name

