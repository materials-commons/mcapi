import api
import datetime
from os import path as os_path
from os import listdir
from os import getcwd


# -- top level project functions --
def create_project(name, description):
    results = api.create_project(name, description)
    project_id = results['id']
    project = get_project_by_id(project_id)
    return project


def get_project_by_id(project_id):
    results = api.get_project_by_id(project_id)
    return Project(data=results)


def get_all_projects():
    results = api.projects()
    projects = []
    for r in results:
        projects.append(Project(data=r))
    return projects


# -- top level user function ---
def get_all_users():
    results = api.get_all_users()
    users = map(make_object, results)
    return users


# -- top level template function ---
def get_all_templates():
    templates_array = api.get_all_templates()
    templates = map((lambda x: make_object(x)), templates_array)
    return templates


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
        self.shallow = True

        attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        for a in attr:
            setattr(self, a, data.get(a, None))

    def process_special_objects(self):
        data = self.input_data
        if not data:
            return
        if _has_key('otype', data):
            obj_type = data['otype']
            # these types are properties and measurements and they get out of jail free
            pass_types = ['number', 'string', 'boolean', 'date', 'selection', 'function',
                          'composition', 'vector', 'matrix']
            if obj_type in pass_types:
                return

            # these cases may need to be further investigated ???
            #  - some of these are sub-classes - to be revisited
            unexpected_types = ['property', 'sample', 'experiment_task', 'experiment', 'settings']
            if obj_type in unexpected_types:
                return
        if _has_key('value', data) and _has_key('element', data):
            return
        if _has_key('value', data) and _has_key('name', data):
            return
        if _has_key('value', data) and _has_key('unit', data):
            return
        if _has_key('attribute', data) and data['attribute'] == 'instrument':
            return
        if _has_key('starred', data):
            return
        if _has_key('mime', data):
            return
        if _has_key('property_set_id', data) and _has_key('name', data):
            return


# These print statements for debugging cases where special processing case is missed
# changed name of display function so that it will not interfere with searches
#        prrint "MCObject: called process_special_objects - possible error?"
#        if _has_key('otype',data): prrint "otype = ",data['otype']
#        prrint "input_data = ", self.input_data

class User(MCObject):
    def __init__(self, data=None):
        # normally, from the data base
        self.id = ""
        self.fullname = ""
        self.email = ""

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        super(User, self).__init__(data)

        attr = ['fullname', 'email']
        for a in attr:
            setattr(self, a, data.get(a, None))

    def can_access(self, project):
        results = api.user_can_access_project(self.id, project.id, project.name)
        return results


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
        self.delete_tally = {}

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

    # Project - basic rethods: rename, put, delete

    def rename(self, name, description=None):
        if not description:
            description = self.description
        results = api.update_project(self.id, name, description)
        project_id = results['id']
        project = get_project_by_id(project_id)
        return project

    def put(self):
        # TODO: Project.put()
        pass

    def delete(self, dry_run=False):
        if dry_run:
            results = api.delete_project_dry_run(self.id)
        else:
            results = api.delete_project(self.id)
        self.delete_tally = DeleteTally(data=results)
        return self

    # Project - Experiment-related methods - basic: create, get_by_id, get_all (in context)

    def create_experiment(self, name, description):
        experiment_json_dict = api.create_experiment(self.id, name, description)
        experiment = make_object(experiment_json_dict)
        experiment.project = self
        return experiment

    def get_experiment_by_id(self, experiment_id):
        # TODO: Project.get_experiment_by_id(id)
        pass

    def get_all_experiments(self):
        list_results = api.fetch_experiments(self.id)
        experiments = map((lambda x: make_object(x)), list_results)
        experiments = map((lambda x: _decorate_object_with(x, 'project', self)), experiments)
        return experiments

    # Project - Dirctroy-related methods - basic: create, get_by_id, get_all (in context)

    def created_directory(self, name, path):
        # TODO: Project.create_directory(name, path)
        pass

    def get_directory_by_id(self, directory_id):
        # TODO: Project.get_dirctroy_by_id(id)
        pass

    def get_all_directories(self):
        results = api.directory_by_id(self.id, "all")
        directories = []
        for item in results:
            item['otype'] = 'directory'
            directory = make_object(item)
            directory._project = self
            directories.append(directory)
        return directories

    def _set_top_directory(self, directory):
        self._top = directory
        return directory

    def get_top_directory(self):
        if not self._top:
            results = api.directory_by_id(self.id, "top")
            directory = make_object(results)
            directory._project = self
            self._set_top_directory(directory)
        return self._top

    def get_directory_list(self, path):
        top_directory = self.get_top_directory()
        return top_directory.get_descendant_list_by_path(path)

    def get_directory(self, directory_id):
        results = api.directory_by_id(self.id, directory_id)
        directory = make_object(results)
        directory._project = self
        directory.shallow = False
        return directory

    def create_or_get_all_directories_on_path(self, path):
        directory = self.get_top_directory()
        if path == "/":
            return [directory]
        if path.endswith("/"):
            path = path[0:-1]
        return directory.create_descendant_list_by_path(path)

    def add_directory(self, path):
        # TODO: Project.add_directory(path) - refactor this should check for and fail if path does not exist
        # TODO: Project.add_directory(path) - refactor add optional flag to create parent path if it does note exist
        directory = self.create_or_get_all_directories_on_path(path)[-1]
        directory._project = self
        return directory

    def add_file_using_directory(self, directory, file_name, local_input_path):
        project_id = self.id
        directory_id = directory.id
        results = api.file_upload(project_id, directory_id, file_name, local_input_path)
        uploaded_file = make_object(results)
        uploaded_file._project = self
        uploaded_file._directory = directory
        uploaded_file._directory_id = directory.id
        return uploaded_file

    def fetch_sample_by_id(self, sample_id):
        sample_json_dict = api.get_project_sample_by_id(self.id, sample_id)
        sample = make_object(sample_json_dict)
        sample.project = self
        return sample


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

        self.category = None

        self.samples = []
        self.processes = {}  # a set
        self.delete_tally = {}

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

    def process_special_objects(self):
        if self.samples:
            self.samples = [make_object(s.input_data) for s in self.samples]
        if self.processes:
            self.processes = [make_object(s.input_data) for s in self.processes]

    # Experiment - basic rethods: rename, put, delete

    def rename(self, name):
        # TODO: Experiment.rename(name)
        pass

    def put(self):
        # TODO: Experiment.put()
        pass

    def delete(self, dry_run=False, delete_processes_and_samples=False):
        if dry_run:
            results = api.delete_experiment_dry_run(self.project.id, self.id)
        elif delete_processes_and_samples:
            results = api.delete_experiment_fully(self.project.id, self.id)
        else:
            results = api.delete_experiment(self.project.id, self.id)
        self.delete_tally = DeleteTally(data=results)
        return self

    # Experiment - Process-related methods - basic: create, get_by_id, get_all (in context)

    def create_process_from_template(self, template_id):
        project = self.project
        experiment = self
        results = api.create_process_from_template(project.id, experiment.id, template_id)
        process = make_object(results)
        process.project = project
        process.experiment = experiment
        return process

    def get_process_by_id(self, process_id):
        project = self.project
        experiment = self
        results = api.get_process_from_id(project.id, experiment.id, process_id)
        process = make_object(results)
        process.project = project
        process.experiment = experiment
        return process

    def get_all_processes(self):
        # TODO: Experiment.get_all_processes()
        pass

    # Experiment - additional rethod
    def decorate_with_samples(self):
        samples_list = api.fetch_experiment_samples(self.project.id, self.id)
        samples = map((lambda x: make_object(x)), samples_list)
        samples = map((lambda x: _decorate_object_with(x, 'project', self.project)), samples)
        samples = map((lambda x: _decorate_object_with(x, 'experiment', self)), samples)
        self.samples = samples
        return self

    def decorate_with_processes(self):
        process_list = api.fetch_experiment_processes(self.project.id, self.id)
        processes = map((lambda x: make_object(x)), process_list)
        processes = map((lambda x: _decorate_object_with(x, 'project', self.project)), processes)
        processes = map((lambda x: _decorate_object_with(x, 'experiment', self)), processes)
        self.processes = processes
        return self


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
        self.category = None

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
        if self.setup:
            for i in range(len(self.setup)):
                self.setup[i] = self._transform_setup(self.setup[i])
        if self.measurements:
            self.measurements = [make_measurement_object(m) for m in self.measurements]
        if self.input_samples:
            self.input_samples = [make_object(s.input_data) for s in self.input_samples]
        if self.output_samples:
            self.output_samples = [make_object(s.input_data) for s in self.output_samples]
        if self.input_files:
            self.input_files = [make_object(s.input_data) for s in self.input_files]
        if self.output_files:
            self.output_files = [make_object(s.input_data) for s in self.output_files]

    def _transform_setup(self, setup_element):
        setup_element.properties = [self._transform_property(prop) for prop in setup_element.properties]
        return setup_element

    def _transform_property(self, process_property):
        prop = make_property_object(process_property)
        return prop

    # Process - basic rethods: rename, put, delete

    def rename(self, process_name):
        results = api.push_name_for_process(self.project.id, self.id, process_name)
        process = make_object(results)
        process.project = self.project
        process.experiment = self.experiment
        return process

    def put(self):
        # TODO Process.put()
        pass

    # Process - Sample-related methods - create, get_by_id, get_all
    def create_samples(self, sample_names):
        process_ok = self.category == 'create_sample' or self.category == 'sectioning'
        if not process_ok:
            print "Process.category is not either " \
                  "'create_sample' or 'sectioning'; instead: " + \
                  self.category + " -- returning None"
            # throw exception?
            return None
        samples = self._create_samples(sample_names)
        self.decorate_with_output_samples()
        return samples

    def get_sample_by_id(self, process_id):
        # TODO: Process.get_sample_by_id(id)
        pass

    def get_all_samples(self):
        # TODO: Process.get_all_samples()
        pass

    def add_input_samples_to_process(self, samples):
        return _add_input_samples_to_process(self.project, self.experiment, self, samples)

    # Process - File-related methods - truncated?
    # TODO: should Process have File-related create, get_by_id, get_all?
    def add_files(self, files_list):
        return _add_files_to_process(self.project, self.experiment, self, files_list)

    # Process - SetupProperties-related methods - special methods
    def get_setup_properties_as_dictionary(self):
        if self.properties_dictionary:
            return self.properties_dictionary
        ret = {}
        for s in self.setup:
            props = s.properties
            for prop in props:
                prop.setup_attribute = s.attribute
                ret[prop.attribute] = prop
        self.properties_dictionary = ret
        return ret

    def set_value_of_setup_property(self, name, value):
        prop = self.get_setup_properties_as_dictionary()[name]
        if prop:
            prop.value = value

    def set_unit_of_setup_property(self, name, unit):
        prop = self.get_setup_properties_as_dictionary()[name]
        if prop and (unit in prop.units):
            prop.unit = unit

    def update_setup_properties(self, name_list):
        prop_dict = self.get_setup_properties_as_dictionary()
        prop_list = []
        for name in name_list:
            prop = prop_dict[name]
            if prop:
                prop_list.append(prop)
        return _update_process_setup_properties(self.project, self.experiment, self, prop_list)

    def make_list_of_samples_with_property_set_ids(self, samples):
        # Note: samples must be output samples of the process
        results = []
        if not self.output_samples:
            return results

        checked_sample_list = []
        for sample in self.output_samples:
            check_sample = None
            for s in samples:
                if s.id == sample.id:
                    check_sample = s
                    break
            if check_sample:
                checked_sample_list.append(check_sample)
        if not checked_sample_list:
            return results

        project = self.project
        for sample in checked_sample_list:
            s = project.fetch_sample_by_id(sample.id)
            processes = s.processes
            for process in processes:
                if process.id == self.id:
                    property_set_id = process.input_data['property_set_id']
                    results.append({
                        'property_set_id': property_set_id,
                        'sample': sample
                    })
        return results

    # Process - Measurement-related methods - special treatment

    def create_measurement(self, data):
        return make_measurement_object(data)

    def set_measurements_for_process_samples(self, measurement_property, measurements):
        return _set_measurement_for_process_samples(self.project,
                                                    self.experiment, self,
                                                    self.make_list_of_samples_with_property_set_ids(
                                                        self.output_samples),
                                                    measurement_property, measurements)

    # Process - additional methods
    def decorate_with_output_samples(self):
        detailed_process = self.experiment.get_process_by_id(self.id)
        self.output_samples = detailed_process.output_samples
        return self

    def decorate_with_input_samples(self):
        detailed_process = self.experiment.get_process_by_id(self.id)
        self.input_samples = detailed_process.input_samples
        return self

    # Process - internal (private method)

    def _create_samples(self, sample_names):
        project = self.project
        process = self
        samples_array_dict = api.create_samples_in_project(project.id, process.id, sample_names)
        samples_array = samples_array_dict['samples']
        # NOTE: in this case, for this version of API, for the call implemented, the
        # returned object is very sparse; hence the samples need to be refetched...
        # however, the fetched object is missing the property_set_id, to add it..
        lookup_table = {}
        for simple_sample in samples_array:
            lookup_table[simple_sample['id']] = simple_sample['property_set_id']
        samples = map((lambda x: project.fetch_sample_by_id(x['id'])), samples_array)
        samples = map((lambda x: _decorate_object_with(x, 'property_set_id', lookup_table[x.id])), samples)
        samples = map((lambda x: _decorate_object_with(x, 'project', project)), samples)
        samples = map((lambda x: _decorate_object_with(x, 'experiment', process.experiment)), samples)
        samples_id_list = []
        # NOTE: side effect to process.experiment
        for sample in samples:
            samples_id_list.append(sample.id)
            sample_in_experiment = None
            for s in process.experiment.samples:
                if sample.id == s.id:
                    sample_in_experiment = s
            if not sample_in_experiment:
                process.experiment.samples.append(sample)
        api.add_samples_to_experiment(project.id, process.experiment.id, samples_id_list)
        return samples


class Sample(MCObject):
    def __init__(self, name=None, data=None):
        self.id = None
        self.name = ""

        self.property_set_id = ''
        self.project = None
        self.experiment = None
        self.properties = []
        # to be filled in later
        self.processes = {}
        self.files = []

        if not data:
            data = {}

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        super(Sample, self).__init__(data)

        attr = ['property_set_id', 'properties']
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
        if self.properties:
            self.properties = [make_measured_property(p.input_data) for p in self.properties]

    # Sample - basic methods: rename, put, delete
    def rename(self, name):
        # TODO: Sample.rename(name)
        pass

    def put(self):
        # TODO: Sample.put()
        pass

    def delete(self):
        # TODO: Sample.rename(name)
        # NOTE: most likely, not a good idea - should be done by delete project?
        pass

    # Sample - additional methods
    def decorate_with_processes(self):
        filled_in_sample = make_object(api.fetch_sample_details(self.project.id, self.id))
        self.processes = filled_in_sample.processes
        return self


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
        self._parent_id = None

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

    def process_special_objects(self):
        data = self.input_data
        if not data:
            return
        if _has_key('parent', data):
            self._parent_id = data['parent']

    # directory - basic methods: rename, move, put, delete
    def rename(self, new_name):
        dir_data = api.directory_rename(self._project.id, self.id, new_name)
        updated_directory = make_object(dir_data)
        updated_directory._project = self._project
        return updated_directory

    def move(self, new_directory):
        project_id = self._project.id
        new_directory_id = new_directory.id
        results = api.directory_move(project_id, self.id, new_directory.id)
        updated_directory = make_object(results)
        updated_directory._project = self._project
        if not updated_directory._parent_id:
            updated_directory._parent_id = new_directory_id
        return updated_directory

    def put(self):
        # TODO Directory.put()
        pass

    def delete(self):
        # TODO Directory.delete() ?? only when empty
        pass

    def get_children(self):
        results = api.directory_by_id(self._project.id, self.id)
        ret = []
        for dir_or_file in results['children']:
            its_type = dir_or_file['otype']
            if its_type == 'file':
                obj = File(data=dir_or_file)
                obj._directory_id = self.id
            if its_type == 'directory':
                obj = Directory(data=dir_or_file)
                obj._parent_id = self.id
            obj._project = self._project
            ret.append(obj)
        return ret

    def create_descendant_list_by_path(self, path):
        results = api.create_fetch_all_directories_on_path(self._project.id, self.id, path)
        dir_list = []
        parent = self
        for dir_data in results['dirs']:
            directory = make_object(dir_data)
            directory._project = self._project
            if not directory._parent_id:
                directory._parent_id = parent.id
            parent = directory
            dir_list.append(directory)
        return dir_list

    def get_descendant_list_by_path(self, path):
        all_directories = self._project.get_all_directories()
        dir_list = []
        parent = self
        full_path = self._project.name + path
        for directory in all_directories:
            dir_path = directory.name
            if full_path.startswith(dir_path):
                directory = self._project.get_directory(directory.id)
                if not directory._parent_id:
                    directory._parent_id = parent.id
                parent = directory
                dir_list.append(directory)
        return dir_list

    def add_file(self, file_name, input_path, verbose=False):
        if verbose:
            print "uploading:", os_path.relpath(input_path, getcwd()), " as:", file_name
        result = self._project.add_file_using_directory(self, file_name, input_path)
        return result

    def add_directory_tree(self, dir_name, input_dir_path, verbose=False):
        if not os_path.isdir(input_dir_path):
            return None
        if verbose:
            name = self.path
            if self.shallow:
                name = self.name
            print "base directory: ", name
        dir_tree_table = make_dir_tree_table(input_dir_path, dir_name, dir_name, {})
        result = []
        for relative_dir_path in dir_tree_table.keys():
            file_dict = dir_tree_table[relative_dir_path]
            dirs = self.create_descendant_list_by_path(relative_dir_path)
            if verbose:
                print "relitive directory: ", relative_dir_path
            directory = dirs[-1]
            for file_name in file_dict.keys():
                input_path = file_dict[file_name]
                result.append(directory.add_file(file_name, input_path, verbose))
        return result


# -- helper function for Directory.add_directory_tree - above
def make_dir_tree_table(base_path, dir_name, relative_base, table_so_far):
    local_path = os_path.join(base_path, dir_name)
    file_dictionary = {}
    for data_file in listdir(local_path):
        path = os_path.join(local_path, data_file)
        if os_path.isfile(path):
            file_dictionary[data_file] = path
    table_so_far[relative_base] = file_dictionary
    for directory in listdir(local_path):
        path = os_path.join(local_path, directory)
        base = os_path.join(relative_base, directory)
        if os_path.isdir(path):
            table_so_far = make_dir_tree_table(local_path, directory, base, table_so_far)
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
        self._directory_id = None

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

    # File - basic methods: rename, move, put, delete

    def rename(self, new_file_name):
        project_id = self._project.id
        file_id = self.id
        results = api.file_rename(project_id, file_id, new_file_name)
        updated_file = make_object(results)
        updated_file._project = self._project
        return updated_file

    def move(self, new_directory):
        project_id = self._project.id
        old_directory_id = self._directory_id
        new_directory_id = new_directory.id
        results = api.file_move(project_id, old_directory_id, new_directory.id, self.id)
        updated_file = make_object(results)
        updated_file._project = self._project
        updated_file._directory_id = new_directory_id
        return updated_file

    def put(self):
        # TODO File.put()
        pass

    def detele(self):
        # TODO File.delete()
        pass

    # File - additional methods
    def download_file_content(self, local_download_file_path):
        project_id = self._project.id
        file_id = self.id
        output_file_path = api.file_download(project_id, file_id, local_download_file_path)
        return output_file_path


class Template(MCObject):
    # global static
    create = "global_Create Samples"
    compute = "global_Computation"
    primitive_crystal_structure = "global_Primitive Crystal Structure"

    def __init__(self, data=None):
        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        super(Template, self).__init__(data)

        # ---- NOTE
        # - Template is truncated, for now, as we only need the id to create
        # - processes from a Template
        # ----


class Measurement(MCObject):
    def __init__(self, data=None):
        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        super(Measurement, self).__init__(data)
        self.attribute = ''
        self.unit = ''
        self.value = ''
        self.is_best_measure = False
        attr = ['attribute', 'unit', 'value', 'is_best_measure']
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


class Property(MCObject):
    def __init__(self, data=None):
        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        super(Property, self).__init__(data)

        self.setup_id = ''
        self.required = False
        self.unit = ''
        self.attribute = ''
        self.value = ''

        self.units = []  # of string
        self.choices = []  # of string

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
        if self.best_measure:
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
            base_object = Directory(data=data)
            return base_object
        if object_type == 'directory':
            return Directory(data=data)
        if object_type == 'datafile':
            return File(data=data)
        if object_type == 'file':
            return File(data=data)
        if object_type == 'template':
            return Template(data=data)
        if object_type == 'experiment_task':
            # Experiment task not implemented
            return MCObject(data=data)
        else:
            return MCObject(data=data)
    else:
        if _has_key('fullname', data):
            return User(data=data)
        if _has_key('unit', data):
            return MCObject(data=data)
        if _has_key('starred', data):
            return MCObject(data=data)
        return MCObject(data=data)


def make_property_object(obj):
    data = obj
    if isinstance(obj, MCObject):
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
        if not holder:
            raise Exception("No Property Object, unrecognized otype = " + object_type, data)
        holder.process_special_objects()
        return holder
    else:
        raise Exception("No Property Object, otype not defined", data)


def make_datetime(data):
    timestamp = int(data['epoch_time'])
    return datetime.datetime.utcfromtimestamp(timestamp)


def make_measured_property(data):
    measurement_property = MeasuredProperty(data)
    measurement_property.process_special_objects()
    return measurement_property


def make_measurement_object(obj):
    data = obj
    if isinstance(obj, MCObject):
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
        if holder:
            holder.process_special_objects()
            return holder
        raise Exception("No Measurement Object, unrecognized otype = " + object_type, data)
    else:
        raise Exception("No Measurement Object, otype not defined", data)


class DeleteTally(object):
    def __init__(self, data=None):
        if data.get('project'):
            # for delete project
            attr = ['files', 'processes', 'datasets', 'project', 'experiments', 'samples']
            for a in attr:
                setattr(self, a, data.get(a, None))
        else:
            # for delete experiment
            attr = ['datasets', 'best_measure_history', 'processes', 'samples', 'experiment_notes',
                    'experiment_task_processes', 'experiment_tasks', 'notes', 'reviews', 'experiments']
            for a in attr:
                setattr(self, a, data.get(a, None))


# -- general support functions
def _decorate_object_with(obj, attr_name, attr_value):
    setattr(obj, attr_name, attr_value)
    return obj


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


# -- support functions for Process --


def _add_input_samples_to_process(project, experiment, process, samples):
    results = api.add_samples_to_process(project.id, experiment.id, process, samples)
    new_process = make_object(results)
    for sample in new_process.input_samples:
        sample.experiment = experiment
        sample.project = project
        found_sample = None
        for existing_sample in process.input_samples:
            if existing_sample.id == sample.id:
                found_sample = existing_sample
        if not found_sample:
            process.input_samples.append(sample)
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


def _set_measurement_for_process_samples(project, experiment, process,
                                         samples_with_property_set_ids, measurement_property, measurements):
    project_id = project.id
    experiment_id = experiment.id
    process_id = process.id
    samples_parameter = []
    for table in samples_with_property_set_ids:
        samples_parameter.append({
            'id': table['sample'].id,
            'property_set_id': table['property_set_id']
        })
    measurement_parameter = []
    for measurement in measurements:
        measurement_parameter.append({
            'name': measurement.name,
            'attribute': measurement.attribute,
            'otype': measurement.otype,
            'value': measurement.value,
            'unit': measurement.unit,
            'is_best_measure': measurement.is_best_measure
        })
    success_flag = api.set_measurement_for_process_samples(
        project_id, experiment_id, process_id,
        samples_parameter, measurement_property, measurement_parameter)
    if not success_flag:
        print "mcapi.mc._set_measurement_for_process_samples - unexpectedly failed"
        return None
    return experiment.get_process_by_id(process_id)
