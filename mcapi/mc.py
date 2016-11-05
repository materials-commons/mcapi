import api

class MCObject(object):
    """
    Base class for Materials Commons objects.

    Attributes
    ----------
      id: str
        ID of the object

      name: str
        Name of the object

      description: str
        Description of the object

      birthtime: int
        Creation time of the object

      mtime: int
        Last modification time

    """

    def __init__(self, data=dict()):
        self._type = "unknown"
        self.owner = ""
        self.name = ""
        self.description = ""
        self.id = ""
        self.birthtime = None
        self.mtime = None
        attr = ['id', 'name', 'description', 'birthtime', 'mtime', '_type', 'owner']
        for a in attr:
            setattr(self, a, data.get(a, None))

class Project(MCObject):
    """
    Materials Commons Project object.

    Attributes
    ----------
    (those of MCObject, plus...)

    top: mcapi.Datadir
      Top-level Datadir in this Project

    source: a URL string or None
      Where this project is hosted

    """

    @staticmethod
    def from_json(data):
        if (data['_type'] == 'project'): return make_object(data)
        return None

    def __init__(self, name="", description="", id="", remote_url="", data=dict()):
        """
        Arguments
        ----------
        name: str, optional
        descrition: str, optional
        id: str, optional
            project id
        remote_url: rul, str
            host of the project, optional
        data:
            generally, data in dictionary form, as returned from the rest api
        """
        # normally, from the data base
        self.id = ""
        self.name = ""
        self.description = ""
        self.size = 0
        self.mediatypes = {}

        self.__all_db_Fields__ = ['id', 'name', 'description', 'birthtime', 'mtime', '_type', 'owner',
                             'size','mediatypes']

        # additional fields
        # counts
        self._count_of = {
            'directory':-1,
            'file':-1,
            'experiment'
            'process':-1,
            'sample':-1
        }
        self._top = None
        self._top_id = ""
        self.source = remote_url
        # holds Datadir, using id for key; initally empty, additional calls needed to fill
        self._directories = dict()
        # holds Datafile, using id for key;  initally empty, additional calls needed to fill
        self._files = dict()
        #

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', '_type', 'owner']
        super(Project, self).__init__(data)

        attr = ['size','mediatypes']
        for a in attr:
            setattr(self, a, data.get(a, None))

        if (name):
            data['name'] = name

        if (description):
            data['description'] = description

        if (id):
            data['id'] = id

    def create_experiment(self, name, description):
        return create_experiment(self,name,description)

    def set_top_directory(self,directory):
        self._top = directory
        return directory

    def get_top_directory(self):
        return self._top

    def file_upload(self, path):
        return file_upload(self, path)

class Experiment(MCObject):

    @staticmethod
    def from_json(data):
        if (data['_type'] == 'experiment'): return make_object(data)
        return None

    def __init__(self, project_id=None, name=None, description=None, id=None,
                 goals=None, aims=None, tasks=None,
                 data=None):

        self.id = None
        self.name = ""
        self.description = ""

        self.project_id = None
        self.project = None

        self.status = None
        self.funding = ''
        self.note = ''

        self.tasks = None
        self.publications = None
        self.notes = None
        self.papers = None
        self.collaborators = None
        self.citations = None
        self.goals = None
        self.aims = None

        if (not data): data = {}

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', '_type', 'owner']
        super(Experiment, self).__init__(data)

        attr = ['project_id', 'status', 'tasks', 'funding', 'publications',
                'notes', 'papers','collaborators', 'note', 'citations',
                'goals', 'aims']
        for a in attr:
            setattr(self, a, data.get(a, None))

        if (name): self.name = name
        if (description): self.description = description
        if (project_id): self.project_id = project_id
        if (id): self.id = id

        attr = ['tasks', 'publications', 'notes', 'collaborators', 'citations',
                'goals', 'aims']
        for a in attr:
            array = getattr(self,a)
            if (not array): array = []
            setattr(self,a,array)

    def create_process_from_template(self,template_id):
        return create_process_from_template(self.project, self, template_id)

class Process(MCObject):

    @staticmethod
    def from_json(data):
        if (data['_type'] == 'process'): return make_object(data)
        return None

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

        self.project = None
        self.experiment = None

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

    def create_samples(self, sample_names):
        return create_samples(self.project,self,sample_names)

    def add_samples_to_process(self, sample_names):
        return add_samples_to_process(self.project,self.experiment,self,sample_names)

class Sample(MCObject):

    @staticmethod
    def from_json(data):
        return Sample(data=data) # no _type attrubute in Sample JSON

    def __init__(self, name=None, data=None):
        self.id = None
        self.name = ""

        self.property_set_id = ''
        self.project = None
        self.process = None

        if (not data): data = {}

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', '_type', 'owner']
        super(Sample, self).__init__(data)

        attr = ['property_set_id']
        for a in attr:
            setattr(self, a, data.get(a, None))

        if (name): self.name = name

class Directory(MCObject):

    @staticmethod
    def from_json(data):
        return Sample(data=data) # no _type attrubute in Sample JSON

    def __init__(self, name=None, parent=None, data=None):
        self.id = None
        self.name = None
        self.parent_id = None
        self.parent = None
        self.project_id = None
        self.project = None

        if (not data): data = {}

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', '_type', 'owner']
        super(Sample, self).__init__(data)

        attr = ['project','project_id', 'parent', 'parent_id']
        for a in attr:
            setattr(self, a, data.get(a, None))

        if (self.project): # in database project and not project_id !!
            self.project_id = self.project
            self.project = None

        if (self.parent): # in database parent and not parent_datadir_id or parent_id !!
            self.parent_id = self.parent
            self.parent = None

        # kw args
        if (name): self.name = name
        if (parent):
            self.parent_id = parent.id
            self.parent = parent

class Template():
    create = "global_Create Samples"
    compute = "global_Computation"

def make_object(data):
    holder = make_base_object_for_type(data)
    for key in data.keys():
        value = data[key]
        if (is_object(value)):
            value = make_object(value)
        elif (is_list(value)):
            value = map(make_object, value)
        setattr(holder, key, value)
    return holder

def make_base_object_for_type(data):
    if (data_has_type(data)):
        type = data['_type']
        if (type == 'process'):
            return Process(data=data)
        if (type == 'project'):
            return Project(data=data)
        if (type == 'experiment'):
            return Experiment(data=data)
        if (type == 'sample'):
            return Sample(data=data)
        if (type == 'experiment_task'):
            # print ("Experiment task not implemented")
            return MCObject(data=data)
        else:
            # print "unrecognized type: ", data
            return MCObject(data=data)
    else:
        if (has_key('timezone', data)):
            #            return utcfromtimestamp(data['time'])
            return MCObject(data=data)
        if (has_key('unit', data)):
            # print ("Unit not implemented")
            return MCObject(data=data)
        if (has_key('starred', data)):
            # print ("Flags not implemented")
            return MCObject(data=data)
        # print "No _type: ", data
        return MCObject(data=data)

def is_object(value):
    return isinstance(value, dict)

def is_list(value):
    return isinstance(value, list)

def has_key(key, data):
    return key in data.keys()

def data_has_type(data):
    return has_key('_type', data)

# -- project --
def list_projects():
    results = api.projects()
    projects = []
    for r in results:
        projects.append(Project(data=r))
    return projects

def create_project(name,description):
    ids = api.create_project(name,description)
    project_id = ids['project_id']
    datadir_id = ids['datadir_id']
    print project_id, datadir_id
    project = fetch_project_by_id(project_id)
    print project
    return project

def fetch_project_by_id(project_id):
    results = api.fetch_project(project_id)
    print results
    return Project(data=results)

# -- Experiment --

def create_experiment(project, name, description):
    experiment_json = api.create_experiment(project.id, name, description)
    experiment = Experiment(data=experiment_json)
    experiment.project = project
    return experiment

# -- Process --

def create_process_from_template(project, experiment, template_id):
    results = api.create_process_from_template(project.id, experiment.id, template_id)
    process = Process.from_json(results)
    process.project = project
    process.experiment = experiment
    return process


def add_samples_to_process(project, experiment, process, samples):
    results = api.add_samples_to_process(project.id, experiment.id, process, samples)
    process = Process.from_json(results)
    process.project = project
    process.experiment = experiment
    return process

# -- Sample --

def create_samples(project, process, sample_names):
    samples_array_dict = api.create_samples(project.id, process.id, sample_names)
    print "smaples json",samples_array_dict
    samples_array = samples_array_dict['samples']
    samples = map((lambda x: Sample.from_json(x)), samples_array)
    samples = map((lambda x: decorate_sample_with(x, 'project', project)), samples)
    samples = map((lambda x: decorate_sample_with(x, 'process', process)), samples)
    return samples

def decorate_sample_with(sample, attr_name, attr_value):
    setattr(sample, attr_name, attr_value)
    return sample

# -- directory --
def fetch_directory(project, id):
    results = api.directory_by_id(project.id,id)
    print results
    return None

# -- file --
def file_upload(project,input_path,output_path):
    project_id = project.id
    results = api.file_upload(project_id,input_path,output_path)
    print results
    return project
