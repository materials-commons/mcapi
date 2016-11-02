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


def add_samples_to_process(project_id, experiment_id, process, samples):
    results = api.add_samples_to_process(project_id, experiment_id, process, samples)
    print "add_samples_to_process: ", results
    return process


__process_example_create__ = \
    {u'files': [], u'_type': u'process', u'name': u'Create Samples', u'output_samples': [],
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

__process_example_compute__ = \
    {"_type": "process",
     "birthtime": {"$reql_type$": "TIME", "epoch_time": 1478095876.274, "timezone": "+00:00"},
     "does_transform": False,
     "files": [],
     "id": "e3364790-9af9-41c0-b670-5ad9db34a649",
     "input_files": [],
     "input_samples": [
         {"_type": "sample", "birthtime": {"$reql_type$": "TIME", "epoch_time": 1478091442.893, "timezone": "+00:00"},
          "description": "", "direction": "in", "files": [], "group_size": 0, "has_group": False,
          "id": "8cb2f37d-f65b-4ef9-ace1-78a2e706ca96", "is_grouped": False,
          "mtime": {"$reql_type$": "TIME", "epoch_time": 1478091442.893, "timezone": "+00:00"}, "name": "Test Sample 1",
          "owner": "terry.weymouth@gmail.com", "process_id": "e3364790-9af9-41c0-b670-5ad9db34a649", "processes": [
             {"_type": "process",
              "birthtime": {"$reql_type$": "TIME", "epoch_time": 1478095217.082, "timezone": "+00:00"},
              "does_transform": False, "id": "b0c20bf5-170a-4803-8e1c-9766a940cd5c",
              "mtime": {"$reql_type$": "TIME", "epoch_time": 1478095217.082, "timezone": "+00:00"},
              "name": "Computation", "note": "", "owner": "terry.weymouth@gmail.com",
              "process_id": "b0c20bf5-170a-4803-8e1c-9766a940cd5c", "process_type": "analysis",
              "sample_id": "8cb2f37d-f65b-4ef9-ace1-78a2e706ca96", "template_id": "global_Computation",
              "template_name": "Computation"}, {"_type": "process",
                                                "birthtime": {"$reql_type$": "TIME", "epoch_time": 1478091442.647,
                                                              "timezone": "+00:00"}, "does_transform": True,
                                                "id": "c144444d-26c6-424e-8d37-8e0e80660fb8",
                                                "mtime": {"$reql_type$": "TIME", "epoch_time": 1478091442.647,
                                                          "timezone": "+00:00"}, "name": "Create Samples", "note": "",
                                                "owner": "terry.weymouth@gmail.com",
                                                "process_id": "c144444d-26c6-424e-8d37-8e0e80660fb8",
                                                "process_type": "create",
                                                "sample_id": "8cb2f37d-f65b-4ef9-ace1-78a2e706ca96",
                                                "template_id": "global_Create Samples",
                                                "template_name": "Create Samples"}, {"_type": "process", "birthtime": {
                 "$reql_type$": "TIME", "epoch_time": 1478095876.274, "timezone": "+00:00"}, "does_transform": False,
                                                                                     "id": "e3364790-9af9-41c0-b670-5ad9db34a649",
                                                                                     "mtime": {"$reql_type$": "TIME",
                                                                                               "epoch_time": 1478095876.274,
                                                                                               "timezone": "+00:00"},
                                                                                     "name": "Computation", "note": "",
                                                                                     "owner": "terry.weymouth@gmail.com",
                                                                                     "process_id": "e3364790-9af9-41c0-b670-5ad9db34a649",
                                                                                     "process_type": "analysis",
                                                                                     "sample_id": "8cb2f37d-f65b-4ef9-ace1-78a2e706ca96",
                                                                                     "template_id": "global_Computation",
                                                                                     "template_name": "Computation"}],
          "properties": [], "property_set_id": "d712f11c-2238-479f-828a-99cebee9d534",
          "sample_id": "8cb2f37d-f65b-4ef9-ace1-78a2e706ca96"}],
     "mtime": {"$reql_type$": "TIME", "epoch_time": 1478095876.274, "timezone": "+00:00"}, "name": "Computation",
     "note": "", "output_files": [], "output_samples": [], "owner": "terry.weymouth@gmail.com",
     "process_type": "analysis", "setup": [{"_type": "settings", "attribute": "job_settings",
                                            "birthtime": {"$reql_type$": "TIME", "epoch_time": 1478095876.34,
                                                          "timezone": "+00:00"},
                                            "id": "7449b13e-3049-40b9-89ff-06a786c75603", "name": "Job Settings",
                                            "process_id": "e3364790-9af9-41c0-b670-5ad9db34a649", "properties": [
            {"_type": "number", "attribute": "walltime", "description": "",
             "id": "580d2bb8-fbfb-4ce2-9093-f86b9198c271", "name": "Walltime",
             "setup_id": "7449b13e-3049-40b9-89ff-06a786c75603", "unit": "s", "value": ""},
            {"_type": "string", "attribute": "submit_script", "description": "",
             "id": "c6a8d83b-8ae9-4e97-ab5e-edc921d50a29", "name": "Submit Script",
             "setup_id": "7449b13e-3049-40b9-89ff-06a786c75603", "unit": "", "value": ""},
            {"_type": "number", "attribute": "memory_per_processor", "description": "",
             "id": "4cf8bc30-e58d-4f20-ac6c-a3b3a7fbcef8", "name": "Memory per Processor",
             "setup_id": "7449b13e-3049-40b9-89ff-06a786c75603", "unit": "", "value": ""},
            {"_type": "number", "attribute": "number_of_processors", "description": "",
             "id": "0ee050aa-2564-4b9e-9735-d7a30655c782", "name": "Number of Processors",
             "setup_id": "7449b13e-3049-40b9-89ff-06a786c75603", "unit": "", "value": ""}],
                                            "setup_id": "7449b13e-3049-40b9-89ff-06a786c75603"}],
     "template_id": "global_Computation", "template_name": "Computation"}

__added_sample_results__ = \
    {u'files': [], u'_type': u'process', u'name': u'Computation', u'output_samples': [], u'setup': [
        {u'_type': u'settings', u'name': u'Job Settings', u'attribute': u'job_settings', u'properties': [
            {u'_type': u'number', u'description': u'', u'attribute': u'memory_per_processor', u'value': u'',
             u'setup_id': u'9a8bfeac-124e-462e-ba89-c83e37380024', u'id': u'4f346cb1-9de8-48df-92a7-c1e1575334da',
             u'unit': u'', u'name': u'Memory per Processor'},
            {u'_type': u'number', u'description': u'', u'attribute': u'number_of_processors', u'value': u'',
             u'setup_id': u'9a8bfeac-124e-462e-ba89-c83e37380024', u'id': u'c35d71d2-dc9a-44b6-94c9-41ab97b1055a',
             u'unit': u'', u'name': u'Number of Processors'},
            {u'_type': u'string', u'description': u'', u'attribute': u'submit_script', u'value': u'',
             u'setup_id': u'9a8bfeac-124e-462e-ba89-c83e37380024', u'id': u'717f9f64-8c55-4216-bb8e-5b36cab92884',
             u'unit': u'', u'name': u'Submit Script'},
            {u'_type': u'number', u'description': u'', u'attribute': u'walltime', u'value': u'',
             u'setup_id': u'9a8bfeac-124e-462e-ba89-c83e37380024', u'id': u'53be1d96-cc84-40fd-8c5c-b126f295dbe9',
             u'unit': u's', u'name': u'Walltime'}], u'setup_id': u'9a8bfeac-124e-462e-ba89-c83e37380024',
         u'process_id': u'b21d4346-d33d-4ad5-8096-a9e7392cee6a',
         u'birthtime': {u'timezone': u'+00:00', u'$reql_type$': u'TIME', u'epoch_time': 1478100133.808},
         u'id': u'9a8bfeac-124e-462e-ba89-c83e37380024'}], u'does_transform': False, u'process_type': u'analysis',
     u'template_id': u'global_Computation', u'note': u'', u'input_samples': [
        {u'files': [], u'property_set_id': u'433e5e15-16a6-400b-b526-df1769ccb86e', u'_type': u'sample',
         u'description': u'', u'name': u'Test Sample 1', u'processes': [
            {u'_type': u'process', u'name': u'Create Samples', u'template_name': u'Create Samples',
             u'sample_id': u'67a8d27a-026e-4c0b-8b0d-6805ede722fe', u'does_transform': True, u'process_type': u'create',
             u'template_id': u'global_Create Samples', u'note': u'',
             u'process_id': u'63af6b82-8bde-4110-ba73-4c413cc333ba',
             u'mtime': {u'timezone': u'+00:00', u'$reql_type$': u'TIME', u'epoch_time': 1478100133.467},
             u'owner': u'terry.weymouth@gmail.com',
             u'birthtime': {u'timezone': u'+00:00', u'$reql_type$': u'TIME', u'epoch_time': 1478100133.467},
             u'id': u'63af6b82-8bde-4110-ba73-4c413cc333ba'},
            {u'_type': u'process', u'name': u'Computation', u'template_name': u'Computation',
             u'sample_id': u'67a8d27a-026e-4c0b-8b0d-6805ede722fe', u'does_transform': False,
             u'process_type': u'analysis', u'template_id': u'global_Computation', u'note': u'',
             u'process_id': u'b21d4346-d33d-4ad5-8096-a9e7392cee6a',
             u'mtime': {u'timezone': u'+00:00', u'$reql_type$': u'TIME', u'epoch_time': 1478100133.769},
             u'owner': u'terry.weymouth@gmail.com',
             u'birthtime': {u'timezone': u'+00:00', u'$reql_type$': u'TIME', u'epoch_time': 1478100133.769},
             u'id': u'b21d4346-d33d-4ad5-8096-a9e7392cee6a'}], u'sample_id': u'67a8d27a-026e-4c0b-8b0d-6805ede722fe',
         u'direction': u'in', u'id': u'67a8d27a-026e-4c0b-8b0d-6805ede722fe',
         u'process_id': u'b21d4346-d33d-4ad5-8096-a9e7392cee6a', u'properties': [], u'is_grouped': False,
         u'mtime': {u'timezone': u'+00:00', u'$reql_type$': u'TIME', u'epoch_time': 1478100133.663},
         u'owner': u'terry.weymouth@gmail.com',
         u'birthtime': {u'timezone': u'+00:00', u'$reql_type$': u'TIME', u'epoch_time': 1478100133.663},
         u'has_group': False, u'group_size': 0}], u'template_name': u'Computation',
     u'mtime': {u'timezone': u'+00:00', u'$reql_type$': u'TIME', u'epoch_time': 1478100133.769},
     u'owner': u'terry.weymouth@gmail.com',
     u'birthtime': {u'timezone': u'+00:00', u'$reql_type$': u'TIME', u'epoch_time': 1478100133.769},
     u'output_files': [], u'id': u'b21d4346-d33d-4ad5-8096-a9e7392cee6a', u'input_files': []}
