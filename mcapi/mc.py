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
        _type = "unknown"
        owner = ""
        name = ""
        description = ""
        id = ""
        birthtime = None
        mtime = None
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

    def __init__(self, name=None, description=None, id=None, remote_url=None, data=dict()):
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
        self.source = remote_url

        if (name):
            data['name'] = name

        if (description):
            data['description'] = description

        if (id):
            data['id'] = id

        super(Project, self).__init__(data)

        #        print "Constructing Project"
        #        for k in data.keys():
        #          print k
        #        print ""

        self._top = None

        # holds Datadir, using id for key; initally empty, additional calls needed to fill
        self._datadir = dict()

        # holds Datafile, using id for key;  initally empty, additional calls needed to fill
        self._datafile = dict()

class Experiment(MCObject):
    def __init__(self, project_id=None, name=None, description=None, id=None, goals=None, aims=None, tasks=None,
                 data={}):
        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', '_type', 'owner']
        super(Experiment, self).__init__(data)

        attr = ['status', 'tasks', 'funding', 'publications', 'notes', 'papers',
                'collaborators', 'note', 'citations', 'goals', 'aims']
        for a in attr:
            setattr(self, a, data.get(a, None))

        if (name): self.name = name
        if (description): self.description = description
        if (project_id): self.project_id = project_id
        if (id): self.id = id

        if (goals):
            self.goals = goals
        else:
            self.goals = []

        if (aims):
            self.aims = aims
        else:
            self.aims = []

        if (tasks):
            self.tasks = tasks
        else:
            self.tasks = []

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

class Sample(MCObject):
    def __init__(self, name=None, data=None):
        self.pproperty_set_id = ''

        if (not data): data = {}

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', '_type', 'owner']
        super(Sample, self).__init__(data)

        attr = ['property_set_id']
        for a in attr:
            setattr(self, a, data.get(a, None))

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
