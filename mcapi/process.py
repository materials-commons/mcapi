import api
from mcobject import MCObject
# from object_factory import make_object

class Process(MCObject):
    def __init__(self, name=None, description=None, project_id=None, process_type=None, process_name=None, data=None):
        self.does_transform = False
        self.input_files = []
        self.output_files = []
        self.input_samples = []
        self.output_samples = []
        self.owner = ''
        self.setup = {
            'files': [],
            'settings': []
        }
        self.transformed_samples = []
        self.what = ''
        self.why = ''

        if (not data): data = {}

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', '_type', 'owner']
        super(Process, self).__init__(data)

        attr = ['files', 'output_samples', 'input_samples', 'setup', 'process_type', 'does_transform',
                'template_id', 'note', 'template_name', 'input_files', 'output_files']
        for a in attr:
            setattr(self, a, data.get(a, None))

        if (process_type): self.process_type = process_type
        if (process_name): self.process_name = process_name
        if (project_id): self.project_id = project_id
        if (name): self.name = name
        if (description): self.description = description


def create_process_from_template(project_id, experiment_id, template_id):
    process_dictionary = api.create_process_from_template(project_id, experiment_id, template_id)
    return Process(data=process_dictionary)


def add_samples_to_process(project_id, experiment_id, process, samples):
    results = api.add_samples_to_process(project_id, experiment_id, process, samples)
    print results
    return process
    # return make_object(results)

