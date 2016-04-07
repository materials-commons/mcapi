import api


class Process(object):
    def __init__(self, project_id, process_type, process_name, name):
        self.project_id = project_id
        self._type = process_type
        self.process_name = process_name
        self.name = name
        self.description = ''
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


