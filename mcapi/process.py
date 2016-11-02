from mcapi import api, MCObject


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


__process_example__ = {u'files': [], u'_type': u'process', u'name': u'Create Samples', u'output_samples': [],
                       u'setup': [{u'_type': u'settings', u'name': u'Instrument', u'attribute': u'instrument',
                                   u'properties': [
                                       {u'_type': u'string', u'description': u'', u'attribute': u'manufacturer',
                                        u'value': u'', u'setup_id': u'366f693b-068e-4294-b0d2-31dbf2b7e05d',
                                        u'id': u'e9c0a2c3-ee42-457f-b64e-e9b85b634467', u'unit': u'',
                                        u'name': u'Manufacturer'},
                                       {u'_type': u'string', u'description': u'', u'attribute': u'supplier',
                                        u'value': u'', u'setup_id': u'366f693b-068e-4294-b0d2-31dbf2b7e05d',
                                        u'id': u'59d51a7e-5936-49bb-86dc-ee06b2380772', u'unit': u'',
                                        u'name': u'Supplier'},
                                       {u'_type': u'selection', u'description': u'', u'attribute': u'production_method',
                                        u'value': u'', u'setup_id': u'366f693b-068e-4294-b0d2-31dbf2b7e05d',
                                        u'id': u'9980e935-fb01-497b-abe8-9fb85f131715', u'unit': u'',
                                        u'name': u'Production method'},
                                       {u'_type': u'date', u'description': u'', u'attribute': u'manufacturing_date',
                                        u'value': u'', u'setup_id': u'366f693b-068e-4294-b0d2-31dbf2b7e05d',
                                        u'id': u'61f6be41-67c1-46dc-8244-6a106570518a', u'unit': u'',
                                        u'name': u'Manufacturing Date'}],
                                   u'setup_id': u'366f693b-068e-4294-b0d2-31dbf2b7e05d',
                                   u'process_id': u'd8cf9165-1803-4250-aedc-23e78717494d',
                                   u'birthtime': {u'timezone': u'+00:00', u'$reql_type$': u'TIME',
                                                  u'epoch_time': 1478031698.441},
                                   u'id': u'366f693b-068e-4294-b0d2-31dbf2b7e05d'}], u'does_transform': True,
                       u'process_type': u'create', u'template_id': u'global_Create Samples', u'note': u'',
                       u'input_samples': [], u'template_name': u'Create Samples',
                       u'mtime': {u'timezone': u'+00:00', u'$reql_type$': u'TIME', u'epoch_time': 1478031698.405},
                       u'owner': u'terry.weymouth@gmail.com',
                       u'birthtime': {u'timezone': u'+00:00', u'$reql_type$': u'TIME', u'epoch_time': 1478031698.405},
                       u'output_files': [], u'id': u'd8cf9165-1803-4250-aedc-23e78717494d', u'input_files': []}
