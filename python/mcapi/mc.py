import api
import datetime
from os import path as os_path
from os import listdir
from os import getcwd
from os import pardir as parent_directory
from pathlib import Path

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


def get_process_from_id(project,experiment,process_id):
    results = api.get_process_from_id(project.id, experiment.id, process_id)
    process = make_object(results)
    process.project = project
    process.experiment = experiment
    return process

# -- supporting classes


class MCObject(object):
    def __init__(self, data=None):
        self.otype = "unknown"
        self.owner = ""
        self.name = ""
        self.description = ""
        self.id = ""
        self.birthtime = None
        self.mtime = None
        if not data:
            data = {}

        self.input_data = data

        attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        for a in attr:
            setattr(self, a, data.get(a, None))


    def process_special_objects(self):
        data = self.input_data
        if not data: return
        if _has_key('otype',data):
            type = data['otype']
            # these types are properties and measurements and they get out of jail free
            pass_types = ['number','string','boolean','date','selection','function',\
                    'composition','vector','matrix']
            if type in pass_types: return

            # these cases may need to be further investigated ???
            #  - some of these are sub-classes - to be revisited
            unexpected_types = ['property','sample','experiment_task','experiment','settings']
            if type in unexpected_types: return
        if _has_key('value', data) and _has_key('element',data): return
        if _has_key('value', data) and _has_key('name',data): return
        if _has_key('value', data) and _has_key('unit',data): return
        if _has_key('attribute',data) and data['attribute'] == 'instrument': return
        if _has_key('starred',data): return
        if _has_key('mime',data): return
        if _has_key('property_set_id',data) and _has_key('name',data): return
#   changed name of display function so that it will not interfere with searches
#        prrint "MCObject: called process_special_objects - possible error?"
#        if _has_key('otype',data): prrint "otype = ",data['otype']
#        prrint "input_data = ", self.input_data

class Project(MCObject):
    def __init__(self, name="", description="", remote_url="", data=None):
        # normally, from the data base
        self.id = ""
        self.name = ""
        self.description = ""
        self.size = 0
        self.mediatypes = {}

        self.__all_db_Fields__ = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner',
                                  'size', 'mediatypes']

        # additional fields
        self._top = None
        self.source = remote_url

        if not data:
            data = {}

        # holds Datafile, using id for key;  initally empty, additional calls needed to fill
        self._files = dict()

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
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

    def process_special_objects(self):
        pass

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

    def add_file_using_directory(self, directory, file_name, local_input_path):
        uploaded_file = _create_file_with_upload(self, directory, file_name, local_input_path)
        uploaded_file._project = self
        uploaded_file._parent = directory
        return uploaded_file

class Experiment(MCObject):
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

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
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
    def __init__(self, name=None, description=None, project_id=None, process_type=None, process_name=None, data=None):
        self.does_transform = False
        self.input_files = []
        self.output_files = []
        self.input_samples = []
        self.output_samples = []

        self.owner = ''
        self.setup = []
        self.measurements = []
        self.transformed_samples = []
        self.what = ''
        self.why = ''

        self.project = None
        self.experiment = None

        self.properties_dictionary = {}

        if not data:
            data = {}

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
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


    def process_special_objects(self):
        if (self.setup):
            for i in range(len(self.setup)):
                self.setup[i] = self._transform_setup(self.setup[i])
        if (self.measurements):
            self.measurements = [make_measurement_object(m) for m in self.measurements]
        if (self.input_samples):
            self.input_samples = [make_object(s.input_data) for s in self.input_samples]
        if (self.output_samples):
            self.output_samples = [make_object(s.input_data) for s in self.output_samples]
        if (self.input_files):
            self.input_files = [make_object(s.input_data) for s in self.input_files]
        if (self.output_files):
            self.output_files = [make_object(s.input_data) for s in self.output_files]


    def _transform_setup(self,setup_element):
        setup_element.properties = [self._transform_property(prop) for prop in setup_element.properties]
        return setup_element

    def _transform_property(self,property):
        prop = make_property_object(property)
        return prop

    def create_samples(self, sample_names):
        return _create_samples(self.project, self, sample_names)

    def add_samples_to_process(self, sample_names):
        return _add_samples_to_process(self.project, self.experiment, self, sample_names)

    def add_files(self, files_list):
        return _add_files_to_process(self.project, self.experiment, self, files_list)

    def get_setup_properties_as_dictionary(self):
        if (self.properties_dictionary):
            return self.properties_dictionary
        ret = {}
        for s in self.setup:
            props = s.properties
            for prop in props:
                prop.setup_attribute = s.attribute
                ret[prop.attribute] = prop
        self.properties_dictionary = ret
        return ret

    def set_value_of_setup_property(self,name,value):
        prop = self.get_setup_properties_as_dictionary()[name]
        if (prop):
            prop.value = value

    def set_unit_of_setup_property(self,name,unit):
        prop = self.get_setup_properties_as_dictionary()[name]
        if (prop and (unit in prop.units)):
            prop.unit = unit

    def update_setup_properties(self,name_list):
        dict = self.get_setup_properties_as_dictionary()
        prop_list = []
        for name in name_list:
            prop = dict[name]
            if (prop):
                prop_list.append(prop)
        return _update_process_setup_properties(self.project,self.experiment,self,prop_list)

    def create_measurement(self,data):
        return make_measurement_object(data)

    def set_measurements_for_process_samples(self, property, measurements):
        return _set_measurement_for_process_samples(self.project, \
                self.experiment, self, self.output_samples,\
                property, measurements)


class Sample(MCObject):
    def __init__(self, name=None, data=None):
        self.id = None
        self.name = ""

        self.property_set_id = ''
        self.project = None
        self.process = None

        self.properties = []

        if not data:
            data = {}

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        super(Sample, self).__init__(data)

        attr = ['property_set_id','properties']
        for a in attr:
            setattr(self, a, data.get(a, None))

        attr = ['properties']
        for a in attr:
            array = getattr(self, a)
            if not array:
                array = []
            setattr(self, a, array)

        if name:
            self.name = name

    def process_special_objects(self):
        if (self.properties):
            self.properties = [make_measured_property(p.input_data) for p in self.properties]


class Directory(MCObject):
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

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
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
            its_type = dir_or_file['otype']
            if its_type == 'file':
                obj = File(data=dir_or_file)
            if its_type == 'directory':
                obj = Directory(data=dir_or_file)
            obj._project = self._project
            obj._parent = self
            ret.append(obj)
        return ret

    def get_descendant_list_by_path(self, path):
        results = api.directory_by_path(self._project.id, self.id, path)
        dir_list = []
        parent = self
        for dir_data in results['dirs']:
            directory = make_object(dir_data)
            directory._project = self._project
            directory._parent = parent
            parent = directory;
            dir_list.append(directory)
        return dir_list

    def add_file(self, file_name, input_path, verbose=False):
        if verbose:
            print "uploading:", os_path.relpath(input_path, getcwd()), " as:", file_name
        result = self._project.add_file_using_directory(self, file_name, input_path)
        return result

    def add_directory_tree(self, dir_name, input_dir_path, verbose=False):
        if (not os_path.isdir(input_dir_path)): return self
        dir_tree_table = make_dir_tree_table(input_dir_path,dir_name,dir_name,{})
        result = []
        for relative_dir_path in dir_tree_table.keys():
            file_dict = dir_tree_table[relative_dir_path]
            dirs = self.get_descendant_list_by_path(relative_dir_path)
            directory = dirs[-1]
            for file_name in file_dict.keys():
                input_path = file_dict[file_name]
                result.append(directory.add_file(file_name,input_path,verbose))
        return result

    def process_special_objects(self):
        pass


def make_dir_tree_table(base_path, dir_name, relative_base, table_so_far):
    local_path = os_path.join(base_path, dir_name)
    file_dictionary = {}
    for file in listdir(local_path):
        path = os_path.join(local_path, file)
        if (os_path.isfile(path)):
            file_dictionary[file] = path
    table_so_far[relative_base] = file_dictionary
    for dir in listdir(local_path):
        path = os_path.join(local_path, dir)
        base = os_path.join(relative_base, dir)
        if (os_path.isdir(path)):
            table_so_far = make_dir_tree_table(local_path, dir, base, table_so_far)
    return table_so_far


class File(MCObject):
    def __init__(self, data=None):
        # normally, from the data base
        self.id = ""
        self.name = ""
        self.description = ""
        self.owner = ""

        self.path = ""
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

        # additional fields
        self._project = None
        self._directory = None

        if not data:
            data = {}

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
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

    def process_special_objects(self):
        pass

    def download_file_content(self,local_download_file_path):
        filepath = _download_data_to_file(self._project, self, local_download_file_path)
        return filepath


class Measurement(MCObject):
    def __init__(self, data=None):
        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        super(Measurement, self).__init__(data)
        self.attribute = ''
        self.unit = ''
        self.value = ''
        self.is_best_measure = False
        attr = ['attribute','unit', 'value', 'is_best_measure']
        for a in attr:
            setattr(self, a, data.get(a, None))


class MeasurementComposition(Measurement):
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementComposition, self).__init__(data)


class MeasurementString(Measurement):
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementString, self).__init__(data)


class MeasurementMatrix(Measurement):
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementMatrix, self).__init__(data)


class MeasurementVector(Measurement):
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementVector, self).__init__(data)


class MeasurementSelection(Measurement):
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementSelection, self).__init__(data)


class MeasurementFile(Measurement):
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementFile, self).__init__(data)


class MeasurementInteger(Measurement):
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementInteger, self).__init__(data)

class MeasurementNumber(Measurement):
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementNumber, self).__init__(data)

class MeasurementBoolean(Measurement):
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementBoolean, self).__init__(data)

class MeasurementSample(Measurement):
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementSample, self).__init__(data)

class MeasurementFile(Measurement):
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementFile, self).__init__(data)

class Property(MCObject):
    def __init__(self, data=None):
        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        super(Property, self).__init__(data)

        self.setup_id = ''
        self.required = False
        self.unit = ''
        self.attribute = ''
        self.value = ''

        self.units = []   # of string
        self.choices = [] # of string

        attr = ['setup_id', 'required', 'unit', 'attribute', 'value']
        for a in attr:
            setattr(self, a, data.get(a, None))

        attr = ['units', 'choices']
        for a in attr:
            setattr(self, a, data.get(a, []))


class MeasuredProperty(Property):
    def __init__(self, data=None):
        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner',
        # 'setup_id', 'required', 'unit', 'attribute', 'value', 'units', 'choices']
        super(MeasuredProperty, self).__init__(data)

        self.best_measure = []  # of Measurement

        attr = ['best_measure']
        for a in attr:
            setattr(self, a, data.get(a, []))

    def process_special_objects(self):
        if (self.best_measure):
            for i in range(len(self.best_measure)):
                measure_data = self.best_measure[i]
                measurement = make_measurement_object(measure_data)
                self.best_measure[i] = measurement


class NumberProperty(Property):
    def __init__(self, data=None):
        super(NumberProperty, self).__init__(data)


class StringProperty(Property):
    def __init__(self, data=None):
        super(StringProperty, self).__init__(data)


class BooleanProperty(Property):
    def __init__(self, data=None):
        super(BooleanProperty, self).__init__(data)


class DateProperty(Property):
    def __init__(self, data=None):
        super(DateProperty, self).__init__(data)


class SelectionProperty(Property):
    def __init__(self, data=None):
        super(SelectionProperty, self).__init__(data)


class FunctionProperty(Property):
    def __init__(self, data=None):
        super(FunctionProperty, self).__init__(data)


class CompositionProperty(Property):
    def __init__(self, data=None):
        super(CompositionProperty, self).__init__(data)


class VectorProperty(Property):
    def __init__(self, data=None):
        super(VectorProperty, self).__init__(data)


class MatrixProperty(Property):
    def __init__(self, data=None):
        super(MatrixProperty, self).__init__(data)


class Template:
    # global static
    create = "global_Create Samples"
    compute = "global_Computation"
    primitive_crystal_structure= "global_Primitive Crystal Structure"

    def __init__(self):
        pass


def make_object(data):
    if _is_datetime(data):
        return make_datetime(data)
    if _is_object(data):
        holder = make_base_object_for_type(data)
        for key in data.keys():
            value = data[key]
            if _is_object(value):
                value = make_object(value)
            elif _is_list(value):
                value = map(make_object, value)
            setattr(holder, key, value)
        holder.process_special_objects()
        return holder
    else:
        return data


def make_base_object_for_type(data):
    if _data_has_type(data):
        object_type = data['otype']
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
        if object_type == 'file':
            return File(data=data)
        if object_type == 'experiment_task':
            # Experiment task not implemented
            return MCObject(data=data)
        else:
            return MCObject(data=data)
    else:
        if _has_key('unit', data):
            return MCObject(data=data)
        if _has_key('starred', data):
            return MCObject(data=data)
        return MCObject(data=data)

def make_property_object(obj):
    data = obj
    if isinstance(obj,MCObject):
        data = obj.input_data
    if _data_has_type(data):
        object_type = data['otype']
        holder = None
        if object_type == 'number':
            holder = NumberProperty(data=data)
        if object_type == 'string':
            holder = StringProperty(data=data)
        if object_type == 'boolean':
            holder = BooleanProperty(data=data)
        if object_type == 'date':
            holder = DateProperty(data=data)
        if object_type == 'selection':
            holder = SelectionProperty(data=data)
        if object_type == 'function':
            holder = FunctionProperty(data=data)
        if object_type == 'composition':
            holder = CompositionProperty(data=data)
        if object_type == 'vector':
            holder = VectorProperty(data=data)
        if object_type == 'matrix':
            holder = MatrixProperty(data=data)
        if (not holder):
            raise Exception("No Property Object, unrecognized otype = " + object_type, data)
        holder.process_special_objects()
        return holder
    else:
        raise Exception("No Property Object, otype not defined", data)

def make_datetime(data):
    timestamp = int(data['epoch_time'])
    return datetime.datetime.utcfromtimestamp(timestamp)

def make_measured_property(data):
    property = MeasuredProperty(data)
    property.process_special_objects()
    return property

def make_measurement_object(obj):
    data = obj
    if isinstance(obj,MCObject):
        data = obj.input_data
    if _data_has_type(data):
        object_type = data['otype']
        holder = None
        if object_type == 'composition':
            holder = MeasurementComposition(data=data)
        if object_type == 'string':
            holder = MeasurementString(data=data)
        if object_type == 'matrix':
            holder = MeasurementMatrix(data=data)
        if object_type == 'vector':
            holder = MeasurementVector(data=data)
        if object_type == 'selection':
            holder = MeasurementSelection(data=data)
        if object_type == 'file':
            holder = MeasurementFile(data=data)
        if object_type == 'integer':
            holder = MeasurementInteger(data=data)
        if object_type == 'number':
            holder = MeasurementNumber(data=data)
        if object_type == 'boolean':
            holder = MeasurementBoolean(data=data)
        if object_type == 'sample':
            holder = MeasurementSample(data=data)
        if object_type == 'file':
            holder = MeasurementFile(data=data)
        if (holder):
            holder.process_special_objects()
            return holder
        raise Exception("No Measurement Object, unrecognized otype = " + object_type, data)
    else:
        raise Exception("No Measurement Object, otype not defined", data)

# -- general support functions
def _is_object(value):
    return isinstance(value, dict)


def _is_list(value):
    return isinstance(value, list)


def _has_key(key, data):
    return _is_object(data) and key in data.keys()


def _data_has_type(data):
    return _has_key('otype', data)

def _is_datetime(data):
    return _has_key('$reql_type$', data) and data['$reql_type$'] == 'TIME'


# -- support function for Experiment --
def _create_experiment(project, name, description):
    experiment_json = api.create_experiment(project.id, name, description)
    experiment = Experiment(data=experiment_json)
    experiment.project = project
    return experiment


# -- support functions for Process --
def _create_process_from_template(project, experiment, template_id):
    results = api.create_process_from_template(project.id, experiment.id, template_id)
    process = make_object(results)
    process.project = project
    process.experiment = experiment
    return process


def _add_samples_to_process(project, experiment, process, samples):
    results = api.add_samples_to_process(project.id, experiment.id, process, samples)
    process = make_object(results)
    process.project = project
    process.experiment = experiment
    return process


def _add_files_to_process(project, experiment, process, file_list):
    results = api.add_files_to_process(project.id, experiment.id, process, file_list)
    process = make_object(results)
    process.project = project
    process.experiment = experiment
    return process


def _update_process_setup_properties(project, experiment, process, prop_list):
    results = api.update_process_setup_properties(
            project.id, experiment.id, process, prop_list)
    process = make_object(results)
    process.project = project
    process.experiment = experiment
    return process


def _set_measurement_for_process_samples(project, experiment, process,\
            samples, property, measurements):
    project_id = project.id
    experiment_id = experiment.id
    process_id = process.id
    samples_parameter = []
    for sample in samples:
        samples_parameter.append({\
            'id': sample.id, \
            'property_set_id': sample.property_set_id
        })
    measurement_parameter = []
    for measurement in measurements:
        measurement_parameter.append({\
            'name': measurement.name, \
            'attribute': measurement.attribute, \
            'otype': measurement.otype, \
            'value': measurement.value, \
            'unit' : measurement.unit, \
            'is_best_measure': measurement.is_best_measure
        })
    success_flag = api.set_measurement_for_process_samples(\
            project_id, experiment_id, process_id, \
            samples_parameter, property, measurement_parameter)
    if not success_flag:
        # throw exception?
        return None
    return get_process_from_id(project, experiment, process_id)


# -- support functions for Sample --

def _create_samples(project, process, sample_names):
    samples_array_dict = api.create_samples(project.id, process.id, sample_names)
    samples_array = samples_array_dict['samples']
    samples = map((lambda x: make_object(x)), samples_array)
    samples = map((lambda x: _decorate_sample_with(x, 'project', project)), samples)
    samples = map((lambda x: _decorate_sample_with(x, 'process', process)), samples)
    return samples


def _decorate_sample_with(sample, attr_name, attr_value):
    setattr(sample, attr_name, attr_value)
    return sample


# -- support function for Directory --
def _fetch_directory(project, directory_id):
    results = api.directory_by_id(project.id, directory_id)
    directory = make_object(results)
    directory._project = project
    return directory


# -- support functions for File --
def _create_file_with_upload(project, directory, file_name, input_path):
    project_id = project.id
    directory_id = directory.id
    results = api.file_upload(project_id, directory_id, file_name, input_path)
    uploaded_file = make_object(results)
    uploaded_file._project = project
    uploaded_file._directory = directory
    return uploaded_file


def _download_data_to_file(project, file_object, output_file_path):
    project_id = project.id
    file_id = file_object.id
    output_file_path = api.file_download(project_id, file_id, output_file_path)
    return output_file_path
