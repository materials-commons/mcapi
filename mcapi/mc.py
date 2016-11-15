import api


# -- top level project functions --
def list_projects():
    results = api.projects()
    projects = []
    for r in results:
        projects.append(Project(data=r))
    return projects


def create_project(name, description):
    ids = api.create_project(name, description)
    project_id = ids['project_id']
    project = fetch_project_by_id(project_id)
    return project


def fetch_project_by_id(project_id):
    results = api.fetch_project(project_id)
    return Project(data=results)

# -- supproting classes


class MCObject(object):
    def __init__(self, data=None):
        self._type = "unknown"
        self.owner = ""
        self.name = ""
        self.description = ""
        self.id = ""
        self.birthtime = None
        self.mtime = None
        if not data:
            data = {}

        attr = ['id', 'name', 'description', 'birthtime', 'mtime', '_type', 'owner']
        for a in attr:
            setattr(self, a, data.get(a, None))


class Project(MCObject):
    @staticmethod
    def from_json(data):
        if data['_type'] == 'project':
            return make_object(data)
        return None

    def __init__(self, name="", description="", remote_url="", data=None):
        # normally, from the data base
        self.id = ""
        self.name = ""
        self.description = ""
        self.size = 0
        self.mediatypes = {}

        self.__all_db_Fields__ = ['id', 'name', 'description', 'birthtime', 'mtime', '_type', 'owner',
                                  'size', 'mediatypes']

        # additional fields
        self._top = None
        self.source = remote_url

        if not data:
            data = {}

        # holds Datafile, using id for key;  initally empty, additional calls needed to fill
        self._files = dict()

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', '_type', 'owner']
        super(Project, self).__init__(data)

        attr = ['size', 'mediatypes']
        for a in attr:
            setattr(self, a, data.get(a, None))

        if name:
            data['name'] = name

        if description:
            data['description'] = description

        if id:
            data['id'] = id

    def create_experiment(self, name, description):
        return _create_experiment(self, name, description)

    def _set_top_directory(self, directory):
        self._top = directory
        return directory

    def get_top_directory(self):
        if not self._top:
            self._set_top_directory(_fetch_directory(self, "top"))
        return self._top

    def get_directory_list(self, path):
        directory = self.get_top_directory()
        if path == "/":
            return [directory]
        if path.endswith("/"):
            path = path[0:-1]
        return directory.get_descendant_list_by_path(path)

    def add_directory(self, path):
        directory = self.get_directory_list(path)[-1]
        directory._project = self
        return directory

    def get_directory(self, path):
        return self.get_directory_list(path)[-1]

    def add_file_using_directory(self, directory, file_name, input_path):
        uploaded_file = _create_file_with_upload(self, directory, file_name, input_path)
        return uploaded_file


class Experiment(MCObject):
    @staticmethod
    def from_json(data):
        if data['_type'] == 'experiment':
            return make_object(data)
        return None

    def __init__(self, project_id=None, name=None, description=None,
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

        if not data:
            data = {}

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', '_type', 'owner']
        super(Experiment, self).__init__(data)

        attr = ['project_id', 'status', 'tasks', 'funding', 'publications',
                'notes', 'papers', 'collaborators', 'note', 'citations',
                'goals', 'aims']
        for a in attr:
            setattr(self, a, data.get(a, None))

        if name:
            self.name = name
        if description:
            self.description = description
        if project_id:
            self.project_id = project_id

        attr = ['tasks', 'publications', 'notes', 'collaborators', 'citations',
                'goals', 'aims']
        for a in attr:
            array = getattr(self, a)
            if not array:
                array = []
            setattr(self, a, array)

    def create_process_from_template(self, template_id):
        return _create_process_from_template(self.project, self, template_id)


class Process(MCObject):
    @staticmethod
    def from_json(data):
        if data['_type'] == 'process':
            return make_object(data)
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

        if not data:
            data = {}

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', '_type', 'owner']
        super(Process, self).__init__(data)

        attr = ['files', 'output_samples', 'input_samples', 'setup', 'process_type', 'does_transform',
                'template_id', 'note', 'template_name', 'input_files', 'output_files']
        for a in attr:
            setattr(self, a, data.get(a, None))

        if process_type:
            self.process_type = process_type
        if process_name:
            self.process_name = process_name
        if project_id:
            self.project_id = project_id
        if name:
            self.name = name
        if description:
            self.description = description

    def create_samples(self, sample_names):
        return _create_samples(self.project, self, sample_names)

    def add_samples_to_process(self, sample_names):
        return _add_samples_to_process(self.project, self.experiment, self, sample_names)

    # noinspection PyMethodMayBeStatic
    def add_files(self, files_list):
        return files_list


class Sample(MCObject):
    @staticmethod
    def from_json(data):
        return Sample(data=data)  # no _type attrubute in Sample JSON

    def __init__(self, name=None, data=None):
        self.id = None
        self.name = ""

        self.property_set_id = ''
        self.project = None
        self.process = None

        if not data:
            data = {}

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', '_type', 'owner']
        super(Sample, self).__init__(data)

        attr = ['property_set_id']
        for a in attr:
            setattr(self, a, data.get(a, None))

        if name:
            self.name = name


class Directory(MCObject):
    @staticmethod
    def from_json(data):
        if data['_type'] == 'directory':
            return make_object(data)
        if data['_type'] == 'datadir':
            return make_object(data)
        return None

    def __init__(self, name="", path="", data=None):
        # normally, from the data base
        self.id = ""
        self.name = ""
        self.checksum = ""
        self.path = ""
        self.size = 0

        # additional fields
        self._project = None
        self._parent = None

        # NOTE: children are not stored locally, but always fetch from remote!
        # see self.getChild(name)

        if not data:
            data = {}

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', '_type', 'owner']
        super(Directory, self).__init__(data)

        attr = ['checksum', 'path', 'size']
        for a in attr:
            setattr(self, a, data.get(a, None))

        # kw args
        if name:
            self.name = name
        if path:
            self.path = path

    def get_children(self):
        results = api.directory_by_id(self._project.id, self.id)
        ret = []
        for dir_or_file in results['children']:
            its_type = dir_or_file['_type']
            if its_type == 'file':
                ret.append(File(data=dir_or_file))
            if its_type == 'directory':
                ret.append(Directory(data=dir_or_file))
        return ret

    def get_descendant_list_by_path(self, path):
        results = api.directory_by_path(self._project.id, self.id, path)
        dir_list = []
        for dir_data in results['dirs']:
            dir_list.append(Directory.from_json(dir_data))
        return dir_list

    def add_file(self, file_name, input_path):
        return self._project.add_file_using_directory(self, file_name, input_path)


class File(MCObject):
    @staticmethod
    def from_json(data):
        if data['_type'] == 'datafile':
            return make_object(data)
        return None

    def __init__(self, data=None):
        # normally, from the data base
        self.id = ""
        self.name = ""
        self.description = ""
        self.owner = ""

        self.size = 0
        self.uploaded = 0
        self.checksum = ""
        self.current = True
        self.mediatype = {}
        self.tags = []
        self.notes = []

        # from database, not inserted now, additional code needed
        self.samples = []
        self.processes = []

        # additional fields, not inserted now, additional code needed
        self._project = None
        self._parent = None

        if not data:
            data = {}

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', '_type', 'owner']
        super(File, self).__init__(data)

        attr = ['size', 'uploaded', 'checksum', 'current', 'owner', 'usesid']
        for a in attr:
            setattr(self, a, data.get(a, None))

        attr = ['tags', 'notes']
        for a in attr:
            setattr(self, a, data.get(a, []))

        attr = ['mediatype']
        for a in attr:
            setattr(self, a, data.get(a, dict()))


class Template:
    # global static
    create = "global_Create Samples"
    compute = "global_Computation"

    def __init__(self):
        pass


def make_object(data):
    holder = make_base_object_for_type(data)
    for key in data.keys():
        value = data[key]
        if _is_object(value):
            value = make_object(value)
        elif _is_list(value):
            value = map(make_object, value)
        setattr(holder, key, value)
    return holder


def make_base_object_for_type(data):
    if _data_has_type(data):
        object_type = data['_type']
        if object_type == 'process':
            return Process(data=data)
        if object_type == 'project':
            return Project(data=data)
        if object_type == 'experiment':
            return Experiment(data=data)
        if object_type == 'sample':
            return Sample(data=data)
        if object_type == 'datadir':
            return Directory(data=data)
        if object_type == 'directory':
            return Directory(data=data)
        if object_type == 'datafile':
            return File(data=data)
        if object_type == 'experiment_task':
            # Experiment task not implemented
            return MCObject(data=data)
        else:
            return MCObject(data=data)
    else:
        if _has_key('timezone', data):
            return MCObject(data=data)
        if _has_key('unit', data):
            return MCObject(data=data)
        if _has_key('starred', data):
            return MCObject(data=data)
        return MCObject(data=data)


# -- general support functions
def _is_object(value):
    return isinstance(value, dict)


def _is_list(value):
    return isinstance(value, list)


def _has_key(key, data):
    return key in data.keys()


def _data_has_type(data):
    return _has_key('_type', data)


# -- support function for Experiment --
def _create_experiment(project, name, description):
    experiment_json = api.create_experiment(project.id, name, description)
    experiment = Experiment(data=experiment_json)
    experiment.project = project
    return experiment


# -- support functions for Process --
def _create_process_from_template(project, experiment, template_id):
    results = api.create_process_from_template(project.id, experiment.id, template_id)
    process = Process.from_json(results)
    process.project = project
    process.experiment = experiment
    return process


def _add_samples_to_process(project, experiment, process, samples):
    results = api.add_samples_to_process(project.id, experiment.id, process, samples)
    process = Process.from_json(results)
    process.project = project
    process.experiment = experiment
    return process


# -- support functions for Sample --

def _create_samples(project, process, sample_names):
    samples_array_dict = api.create_samples(project.id, process.id, sample_names)
    samples_array = samples_array_dict['samples']
    samples = map((lambda x: Sample.from_json(x)), samples_array)
    samples = map((lambda x: _decorate_sample_with(x, 'project', project)), samples)
    samples = map((lambda x: _decorate_sample_with(x, 'process', process)), samples)
    return samples


def _decorate_sample_with(sample, attr_name, attr_value):
    setattr(sample, attr_name, attr_value)
    return sample


# -- support function for Directory --
def _fetch_directory(project, directory_id):
    results = api.directory_by_id(project.id, directory_id)
    directory = Directory.from_json(results)
    directory._project = project
    return directory


# -- support functions for File --
def _create_file_with_upload(project, directory, file_name, input_path):
    project_id = project.id
    directory_id = directory.id
    results = api.file_upload(project_id, directory_id, file_name, input_path)
    uploaded_file = File.from_json(results)
    return uploaded_file


def _download_data_to_file(project, file_object, output_file_path):
    project_id = project.id
    file_id = file_object.id
    output_file_path = api.file_download(project_id, file_id, output_file_path)
    return output_file_path
