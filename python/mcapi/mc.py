import api
import string
import hashlib
import copy
import sys
from os import path as os_path
from os import listdir
from os import getcwd
from base import MCObject, PrettyPrint
from base import _decorate_object_with, _is_object, _is_list, _has_key, _data_has_type
from base import _is_datetime, _make_datetime
from measurement import make_measurement_object
from pandas import DataFrame
from tabulate import tabulate
from StringIO import StringIO


# -- top level project functions --
def create_project(name, description):
    """
    Creates a new Project object in the database and return it.
    """
    #    Example:
    #    ``
    #        name = "A Project"
    #        description = "This is a project for me"
    #        project = mcapi.create_project(name,description)
    #        print project.name, project.description
    #    ``
    #
    results = api.create_project(name, description)
    project_id = results['id']
    project = get_project_by_id(project_id)
    return project


def get_project_by_id(project_id):
    """
    Fetch a project from the database and return it/
    """
    #    Example::
    #        project = get_project_by_id("e4fd5c88-2fb7-40af-b3fc-2711d786e5f6")
    results = api.get_project_by_id(project_id)
    return Project(data=results)


def get_all_projects():
    """
    Return a list of all the project to which the current user has access.
    """
    #    Example::
    #        project_list = get_all_projects()
    #        for project in project_list:
    #            print project.name
    results = api.projects()
    projects = []
    for r in results:
        projects.append(Project(data=r))
    return projects


# -- top level user function ---
def get_all_users():
    """
    Return the list of all users registerd on the server.
    """
    #    Example::
    #        user_list = get_all_users()
    #        for user in user_list:
    #            print user.fullname, user.email
    results = api.get_all_users()
    users = map(make_object, results)
    return users


# -- top level template function ---
def get_all_templates():
    """
    Return a list of all the templates known to the system.
    """
    #    Example::
    #        template_list = get_all_templates()
    #        for template in template_list:
    #            print template.name, template.id
    templates_array = api.get_all_templates()
    templates = map((lambda x: make_object(x)), templates_array)
    return templates


# -- supporting classes

# These print statements for debugging cases where special processing case is missed
# changed name of display function so that it will not interfere with searches
#        prrint "MCObject: called _process_special_objects - possible error?"
#        if _has_key('otype',data): prrint "otype = ",data['otype']
#        prrint "input_data = ", self.input_data

class User(MCObject):
    """
    Representing a registered user; normally set up by a call to get_all_users()
    """
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
        """
        Does this user have permission to access the indicated project.
        """
        #        Example:
        #        user_list = get_all_users()
        #        for user in user_list:
        #            if user.can_access(project):
        #                print user.fullname, user.email
        results = api.user_can_access_project(self.id, project.id, project.name)
        return results


class Project(MCObject):
    """
    A Materials Commons Project. Normally created by create_project().

    """
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

        # Reserved for use by CLI:

        # "local_path" to where Project files have been downloaded on local machine
        self.local_path = None
        # Remote instance, where Project is saved. Similar to source
        self.remote = None

    def pretty_print(self, shift=0, indent=2, out=sys.stdout):
        pp = PrettyPrint(shift=shift, indent=indent, out=out)
        pp.write("name: " + pp.str(self.name))
        pp.n_indent += 1
        pp.write("description: " + pp.str(self.description))
        pp.write("id: " + self.id)
        pp.write("owner: " + pp.str(self.owner))
        pp.write("mtime: " + pp.str(self.mtime.strftime("%b %Y %d %H:%M:%S")))

    def _process_special_objects(self):
        pass

    # Project - basic methods: rename, put, delete

    def rename(self, name, description=None):
        """
        Change the name and (optionally) description of a project.
        Returns the new project from the database.
        """
        if not description:
            description = self.description
        results = api.update_project(self.id, name, description)
        project_id = results['id']
        project = get_project_by_id(project_id)
        return project

    def put(self):
        """
        NOTE: Not currently implemented.
        """
        # TODO: Project.put()
        pass

    def delete(self, dry_run=False):
        """
        Delete this project from the database.
        If dry_run is True, only determines the oejcts to be deleted, bud does not actually delete them.

        Returns a DeleteTally instance, which lists the id's of the objects (to be or actually) deleted.

        """
        if dry_run:
            results = api.delete_project_dry_run(self.id)
        else:
            results = api.delete_project(self.id)
        self.delete_tally = DeleteTally(data=results)
        return self

    # Project - Experiment-related methods - basic: create, get_by_id, get_all (in context)

    def create_experiment(self, name, description):
        """
        Create and return an Experiemnt in this project.

        >>> experiment = project.create_experiment("Experiment 1", "Test Procedures")

        """
        experiment_json_dict = api.create_experiment(self.id, name, description)
        experiment = make_object(experiment_json_dict)
        experiment.project = self
        return experiment

    def get_experiment_by_id(self, experiment_id):
        """
        NOTE: currently not implemented
        """
        # TODO: Project.get_experiment_by_id(id)
        pass

    def get_all_experiments(self):
        """
        Get a list of all the experiments in this project.

        >>> experiment_list = project.get_all_experiments()
        >>> for experiment in experiment_list:
        >>>     print experiment.id, experiment.name

        """
        list_results = api.fetch_experiments(self.id)
        experiments = map((lambda x: make_object(x)), list_results)
        experiments = map((lambda x: _decorate_object_with(x, 'project', self)), experiments)
        return experiments

    # Project - Directory-related methods - basic: create, get_by_id, get_all (in context)

    def create_directory(self, name, path):
        """
        NOTE: currently not implemented
        """
        # TODO: Project.create_directory(name, path)
        pass

    def get_directory_by_id(self, directory_id):
        """ Gets the indicated directory.

        :param directory_id: The id of the directory to fetch.
        :type name: str.
        :returns: mcapi.Directory

        >>> directory = project.get_directory_by_id('876655a2-c31b-4895-8766-40a168ea1a87')
        >>> print directory.path

        """

        results = api.directory_by_id(self.id, directory_id)
        directory = make_object(results)
        directory._project = self
        directory.shallow = False
        return directory

    def get_all_directories(self):
        """
        Get a list of all the directories in this project.

        """

        # Example:
        #            directory_list = project.get_all_directories()
        #            for directory in directory_list:
        #                print directory_name, directory_path
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
        """
        Get the top leve directory.
        """
        if not self._top:
            results = api.directory_by_id(self.id, "top")
            directory = make_object(results)
            directory._project = self
            self._set_top_directory(directory)
        return self._top

    def get_directory_list(self, path):
        """
        Given a directory path, returns a list of all the directoreis on the path.
        Can fail if the path does not exist.

        """
        #        In this example, the list would consist of three directories, assuming that they exist:
        #            the Root directory (or 'top' directory)
        #            directory 'A'
        #            directory 'B'
        #
        #        Example:
        #            directory_list = project.get_directory_list("/A/B")
        #            print len(directory_list)
        #            for directory in directory_list:
        #                print directory.name, directory.path

        top_directory = self.get_top_directory()
        return top_directory.get_descendant_list_by_path(path)

    def get_directory(self, directory_id):
        """
        Get the indicated directory.
        """
        return self.get_directory_by_id(directory_id)

    def create_or_get_all_directories_on_path(self, path):
        """
        Given a directory path, returns a list of all the directories on the path.
        If a directory is missing, in the path, it is created and returned in the list.

        """

        directory = self.get_top_directory()
        if path == "/":
            return [directory]
        if path.endswith("/"):
            path = path[0:-1]
        return directory.create_descendant_list_by_path(path)

    def add_directory(self, path):
        """
        Given a directory path, creates all the directories on the path and returns the last one.
        If a directory is missing, in the path, it is created.

        """
        #        Example:
        #            directory = project.add_directory("/A/B")
        #            print directory.name, directory.path

        # TODO: Project.add_directory(path) - refactor this should check for and fail if path does not exist
        # TODO: Project.add_directory(path) - refactor add optional flag to create parent path if it does note exist
        directory = self.create_or_get_all_directories_on_path(path)[-1]
        directory._project = self
        return directory

    def add_file_using_directory(self, directory, file_name, local_path, verbose=False, limit=50):
        """
        Given a directory, a file_name, a local directory path to the file -
        uploads the file, creates a file descriptor in the database, and returns file descriptor.

        """
        #        Example:
        #            directory = directory = project.add_directory("/A/B")
        #            file = project.add_file_using_directory(directory,"Test-Results","/tmp/results.txt")
        #            print file.name
        file_size_MB = os_path.getsize(local_path) >> 20
        if file_size_MB > limit:
            msg = "File too large (>{0}MB), skipping. File size: {1}M".format(limit, file_size_MB)
            raise Exception(msg)
        if verbose:
            print "uploading:", os_path.relpath(local_path, getcwd()), " as:", file_name
        project_id = self.id
        directory_id = directory.id
        results = api.file_upload(project_id, directory_id, file_name, local_path)
        uploaded_file = make_object(results)
        uploaded_file._project = self
        uploaded_file._directory = directory
        uploaded_file._directory_id = directory.id
        return uploaded_file

    def add_file_by_local_path(self, local_path, verbose=False, limit=50):
        """
        Upload a file, specified by local_path, creating intermediate 
        directories as necessary
        
        """
        #        Example:
        #           self.local_path = "/path/to/Proj"
        #           local_path = "/path/to/Proj/test_dir/file_A.txt" -> upload file_A.txt
        dir_path = self._local_path_to_path(os_path.dirname(local_path))
        dir = self.create_or_get_all_directories_on_path(dir_path)[-1]
        return self.add_file_using_directory(dir, os_path.basename(local_path),
                                             local_path, verbose, limit)

    def add_directory_tree_by_local_path(self, local_path, verbose=False, limit=50):
        """
        Upload a directory, specified by local_path, and all its contents 
        creating intermediate directories as necessary
        
        """
        #        Example:
        #           self.local_path = "/path/to/Proj"
        #           local_path = "/path/to/Proj/test_dir/dir_A" -> upload dir_A and all contents
        path = self._local_path_to_path(os_path.dirname(local_path))
        dir = self.create_or_get_all_directories_on_path(path)[-1]
        return dir.add_directory_tree(os_path.basename(local_path),
                                      os_path.dirname(local_path), verbose, limit)

    # Project - File or Directory-related methods - basic: get_by_local_path

    def get_by_local_path(self, local_path):
        """
        Uses path on local machine to get a File or Directory
        
        Arguments:
            proj: mcapi.Project.

            local_path: file or directory local path equivalant.
        
        Returns:
            obj: mcapi.File, mcapi.Directory, or None.
        """
        if self.local_path is None:
            msg = "Error in Project.get_by_local_path: Project.local_path is None"
            raise Exception(msg)
        if os_path.abspath(local_path) == self.local_path:
            return self.get_top_directory()
        names = string.split(os_path.relpath(local_path, self.local_path), '/')
        curr = self.get_top_directory()
        for n in names:
            nextchild = filter(lambda x: x.name == n, curr.get_children())
            if len(nextchild) == 0:
                return None
            curr = nextchild[0]
        return curr

    def file_exists_by_local_path(self, local_path, checksum=False):
        """
        Check if files exists locally and remotely. Optionally compares md5 hash.
        
        Returns:
            file_exists [, checksum_equal]
            
            file_exists: bool
                True if file exists locally and remotely
            
            checksum_equal:
                Returns (local checksum == remote checksum), if 'checksum' == True,
        """
        if os_path.exists(local_path) and os_path.isfile(local_path):
            obj = self.get_by_local_path(local_path)
            if isinstance(obj, File):
                if checksum:
                    with open(local_path, 'r') as f:
                        l_checksum = hashlib.md5(f.read()).hexdigest()
                    return True, (obj.checksum == l_checksum)
                else:
                    return True
        return False

    def _local_path_to_path(self, local_path):
        local_path = os_path.abspath(local_path)
        if local_path == self.local_path:
            return "/"
        else:
            return os_path.relpath(local_path, self.local_path)

    # Project - Processes

    def get_all_processes(self):
        """
        Get a list of all processes in this project.

        """
        #        Example:
        #            process_list = project.get_all_processes()
        #            for process in process_list:
        #                print process.name
        process_list = api.get_project_processes(self.id, self.remote)
        processes = map((lambda x: make_object(x)), process_list)
        processes = map((lambda x: _decorate_object_with(x, 'project', self)), processes)
        return processes

    def get_process_by_id(self, process_id):
        """
        Get a project sample by process id.

        """
        #        Example:
        #            sample = project.get_process_by_id(process.id)
        results = api.get_process_by_id(self.id, process_id)
        process = make_object(results)
        process.project = self
        process._update_project_experiment()
        return process

    # Project - Samples

    def get_all_samples(self):
        """
        Get a list of all samples in this project.

        """
        #        Example:
        #            sample_list = project.get_all_samples()
        #            for process in process_list:
        #                print process.name
        samples_list = api.get_project_samples(self.id, self.remote)
        samples = map((lambda x: make_object(x)), samples_list)
        samples = map((lambda x: _decorate_object_with(x, 'project', self)), samples)
        return samples

    def fetch_sample_by_id(self, sample_id):
        """
        Get the sample in question.
        """
        sample_json_dict = api.get_project_sample_by_id(self.id, sample_id)
        sample = make_object(sample_json_dict)
        sample.project = self
        return sample

    def get_sample_by_id(self, sample_id):
        """
        Get the sample in question.
        """
        results = api.get_sample_by_id(self.id, sample_id)
        sample = make_object(results)
        sample.project = self
        return sample


class Experiment(MCObject):
    """
    A Materials Commons Experiment. Normally created by project.create_experiment()
    """
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

    def _process_special_objects(self):
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
        process._update_project_experiment()
        return process

    def get_process_by_id(self, process_id):
        project = self.project
        experiment = self
        results = api.get_experiment_process_by_id(project.id, experiment.id, process_id)
        process = make_object(results)
        process.project = project
        process.experiment = experiment
        process._update_project_experiment()
        return process

    def get_all_processes(self):
        process_list = api.fetch_experiment_processes(self.project.id, self.id)
        processes = map((lambda x: make_object(x)), process_list)
        processes = map((lambda x: _decorate_object_with(x, 'project', self.project)), processes)
        processes = map((lambda x: _decorate_object_with(x, 'experiment', self)), processes)
        for process in processes:
            process._update_project_experiment()
        return processes

    # Experiment - Process-related methods - basic: create, get_by_id, get_all (in context)

    def get_sample_by_id(self, sample_id):
        project = self.project
        experiment = self
        results = api.get_experiment_sample_by_id(project.id, experiment.id, sample_id)
        sample = make_object(results)
        sample.project = project
        sample.experiment = experiment
        return sample

    def get_all_samples(self):
        samples_list = api.fetch_experiment_samples(self.project.id, self.id)
        samples = map((lambda x: make_object(x)), samples_list)
        samples = map((lambda x: _decorate_object_with(x, 'project', self.project)), samples)
        samples = map((lambda x: _decorate_object_with(x, 'experiment', self)), samples)
        return samples

    # Experiment - additional method
    def decorate_with_samples(self):
        self.samples = self.get_all_samples()
        return self

    def decorate_with_processes(self):
        self.processes = self.get_all_processes()
        return self


class Process(MCObject):
    """
    A Materials Commons Process. Normally created by experiment.create_process_from_template()
    """
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
        self.experiment = None

        self.project = None
        self.properties_dictionary = {}

        # filled in when Process is in Sample.processes
        self.direction = ''
        self.process_id = ''
        self.sample_id = ''
        self.property_set_id = ''
        self.experiments = []

        # filled in when measurements are attached
        self.measurements = []

        if not data:
            data = {}

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        super(Process, self).__init__(data)

        attr = ['setup', 'category', 'process_type', 'does_transform', 'template_id', 'note',
                'template_name', 'direction', 'process_id', 'sample_id',
                'property_set_id']
        for a in attr:
            setattr(self, a, data.get(a, None))

        attr = ['files', 'measurements', 'output_samples', 'input_samples',
                'transformed_samples', 'input_files', 'output_files',
                'experiments']
        for a in attr:
            setattr(self, a, data.get(a, []))

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

    def pretty_print(self, shift=0, indent=2, out=sys.stdout):
        pp = PrettyPrint(shift=shift, indent=indent, out=out)
        pp.write("name: " + pp.str(self.name))
        pp.n_indent += 1
        # setup?
        # note?
        pp.write("description: " + pp.str(self.description))
        pp.write("id: " + pp.str(self.id))
        pp.write("owner: " + pp.str(self.owner))
        pp.write("template_id: " + pp.str(self.template_id))
        pp.write("template_name: " + pp.str(self.template_name))
        pp.write("does_transform: " + pp.str(self.does_transform))
        pp.write("process_type: " + pp.str(self.process_type))
        pp.write_objects("input_files: ", self.input_files)
        pp.write_objects("output_files: ", self.output_files)
        pp.write_objects("files: ", self.files)
        pp.write_pretty_print_objects("input_samples: ", self.input_samples)
        pp.write_pretty_print_objects("output_samples: ", self.output_samples)
        if len(self.transformed_samples):
            pp.write_objects("transformed_samples: ", self.transformed_samples)
        if self.direction:
            pp.write("direction: " + pp.str(self.direction))
            pp.write("process_id: " + pp.str(self.process_id))
            pp.write("sample_id: " + pp.str(self.sample_id))
            pp.write("property_set_id: " + pp.str(self.property_set_id))
        if len(self.experiments):
            pp.write_objects("experiments: ", self.experiments)
        if len(self.measurements):
            pp.write_measurements(self.measurements)

    def _process_special_objects(self):
        if self.setup:
            for i in range(len(self.setup)):
                self.setup[i] = self._transform_setup(self.setup[i])
        if self.measurements:
            self.measurements = [make_measurement_object(m) for m in self.measurements]
        if self.input_samples:
            self.input_samples = [make_object(s.input_data) for s in self.input_samples]
            for sample in self.input_samples:
                sample.project = self.project
                sample.experiment = self.experiment
        if self.output_samples:
            self.output_samples = [make_object(s.input_data) for s in self.output_samples]
            for sample in self.output_samples:
                sample.project = self.project
                sample.experiment = self.experiment
        if self.input_files:
            self.input_files = [make_object(s.input_data) for s in self.input_files]
        if self.output_files:
            self.output_files = [make_object(s.input_data) for s in self.output_files]

    def _update_project_experiment(self):
        for sample in self.input_samples:
            sample.project = self.project
            sample.experiment = self.experiment

        for sample in self.output_samples:
            sample.project = self.project
            sample.experiment = self.experiment

        for sample in self.transformed_samples:
            sample.project = self.project
            sample.experiment = self.experiment

        for file in self.input_files:
            file.project = self.project
            file.experiment = self.experiment

        for file in self.output_files:
            file.project = self.project
            file.experiment = self.experiment

    def _transform_setup(self, setup_element):
        setup_element.properties = [self._transform_property(prop) for prop in setup_element.properties]
        return setup_element

    def _transform_property(self, process_property):
        prop = make_property_object(process_property)
        return prop

    # Process - basic methods: rename, put, delete

    def rename(self, process_name):
        results = api.push_name_for_process(self.project.id, self.id, process_name)
        process = make_object(results)
        process.project = self.project
        process.experiment = self.experiment
        process._update_project_experiment()
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
        return self._add_input_samples_to_process(samples)

    # Process - File-related methods - truncated?
    # TODO: should Process have File-related create, get_by_id, get_all?
    def add_files(self, files_list):
        return self._add_files_to_process(files_list)

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
        return self._update_process_setup_properties(prop_list)

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
        return self._set_measurement_for_process_samples(
            self.make_list_of_samples_with_property_set_ids(self.output_samples),
            measurement_property,
            measurements
        )

    def set_measurement(self, attribute, measurement_data, name=None):
        if (not name):
            name = attribute

        if not "name" in measurement_data:
            measurement_data['name'] = name

        if not "attribute" in measurement_data:
            measurement_data['attribute'] = attribute

        if not "unit" in measurement_data:
            measurement_data['unit'] = ""

        measurement = self.create_measurement(data=measurement_data)

        measurement_property = {
            "name": name,
            "attribute": attribute
        }

        return self.set_measurements_for_process_samples(
            measurement_property, [measurement])

    def add_integer_measurement(self, attribute, value, name=None):
        if (not name):
            name = attribute

        measurement_data = {
            "name": name,
            "attribute": attribute,
            "otype": "integer",
            "value": value,
            "is_best_measure": True
        }
        return self.set_measurement(attribute, measurement_data, name)

    def add_number_measurement(self, attrname, value, name=None):
        measurement_data = {
            "attribute": attrname,
            "otype": "number",
            "value": value,
            "is_best_measure": True
        }
        return self.set_measurement(attrname, measurement_data, name)

    def add_boolean_measurement(self, attrname, value, name=None):
        measurement_data = {
            "attribute": attrname,
            "otype": "boolean",
            "value": value,
            "is_best_measure": True
        }
        return self.set_measurement(attrname, measurement_data, name)

    def add_string_measurement(self, attrname, value, name=None):
        measurement_data = {
            "attribute": attrname,
            "otype": "string",
            "value": value,
            "is_best_measure": True
        }
        return self.set_measurement(attrname, measurement_data, name)

    def add_file_measurement(self, attrname, file, name=None):
        measurement_data = {
            "attribute": attrname,
            "otype": "file",
            "value": {
                "file_id": file.id,
                "file_name": file.name
            },
            "is_best_measure": True
        }
        return self.set_measurement(attrname, measurement_data, name)

    # NOTE: no covering test or example for this function - probably works - Terry, Jan 20, 2016
    def add_sample_measurement(self, attrname, sample, name=None):
        measurement_data = {
            "attribute": attrname,
            "otype": "sample",
            "value": {
                "sample_id": sample.id,
                "sample_name": sample.name,
                "property_set_id": sample.property_set_id
            },
            "is_best_measure": True
        }
        return self.set_measurement(attrname, measurement_data, name)

    def add_list_measurement(self, attrname, value, value_type, name=None):
        measurement_data = {
            "attribute": attrname,
            "otype": "vector",
            "value": {
                "dimensions": len(value),
                "otype": value_type,
                "value": value
            },
            "is_best_measure": True
        }
        return self.set_measurement(attrname, measurement_data, name)

    def add_numpy_matrix_measurement(self, attrname, value, name=None):
        measurement_data = {
            "attribute": attrname,
            "otype": "matrix",
            "value": {
                "dimensions": list(value.shape),
                "otype": "float",
                "value": value.tolist()
            },
            "is_best_measure": True
        }
        return self.set_measurement(attrname, measurement_data, name)

    def add_selection_measurement(self, attrname, value, name=None):
        measurement_data = {
            "attribute": attrname,
            "otype": "selection",
            "value": value,
            "is_best_measure": True
        }
        return self.set_measurement(attrname, measurement_data, name)

    def add_vector_measurement(self, attrname, value, name=None):
        measurement_data = {
            "attribute": attrname,
            "otype": "vector",
            "value": {
                "dimensions": len(value),
                "otype": "float",
                "value": value
            },
            "is_best_measure": True
        }
        return self.set_measurement(attrname, measurement_data, name)

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
    def _set_measurement_for_process_samples(self, samples_with_property_set_ids, measurement_property, measurements):
        project_id = self.project.id
        experiment_id = self.experiment.id
        process_id = self.id
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
        return self.experiment.get_process_by_id(process_id)

    def _add_input_samples_to_process(self, samples):
        project = self.project
        experiment = self.experiment
        process = self
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
        process._update_project_experiment()
        return process

    def _add_files_to_process(self, file_list):
        project = self.project
        experiment = self.experiment
        process = self
        results = api.add_files_to_process(project.id, experiment.id, process, file_list)
        process = make_object(results)
        process.project = project
        process.experiment = experiment
        process._update_project_experiment()
        return process

    def _update_process_setup_properties(self, prop_list):
        project = self.project
        experiment = self.experiment
        process = self
        results = api.update_process_setup_properties(
            project.id, experiment.id, process, prop_list)
        process = make_object(results)
        process.project = project
        process.experiment = experiment
        process._update_project_experiment()
        return process

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
    """
    A Materials Commons Sample. Normally created by process.create_samples() using a
    'create sample' style process.
    """
    def __init__(self, name=None, data=None):
        self.id = None
        self.name = ""

        self.property_set_id = ''
        self.project = None
        self.experiment = None
        # filled in when measurements exist (?)
        self.properties = []
        self.experiments = []
        self.property_set_id = None
        self.direction = ''
        self.sample_id = None
        # to be filled in later
        self.processes = {}
        self.files = []
        self.is_grouped = False;
        self.has_group = False;
        self.group_size = 0;

        if not data:
            data = {}

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        super(Sample, self).__init__(data)

        attr = ['property_set_id', 'direction', 'sample_id',
                'process_id', 'is_grouped', 'has_group', 'group_size']
        for a in attr:
            setattr(self, a, data.get(a, None))

        attr = ['properties', 'files', 'experiments']
        for a in attr:
            setattr(self, a, data.get(a, []))

        if name:
            self.name = name

    def pretty_print(self, shift=0, indent=2, out=sys.stdout):
        pp = PrettyPrint(shift=shift, indent=indent, out=out)
        pp.write("name: " + pp.str(self.name))
        pp.n_indent += 1
        pp.write("description: " + pp.str(self.description))
        pp.write("id: " + pp.str(self.id))
        pp.write("owner: " + pp.str(self.owner))
        if (len(self.files) > 0):
            pp.write_objects("files: ", self.files)
        if (len(self.experiments) > 0):
            pp.write_objects("experiments: ", self.experiments)
        if (self.direction):
            pp.write("direction: " + pp.str(self.direction))
            pp.write("property_set_id: " + pp.str(self.property_set_id))
            pp.write("sample_id: " + pp.str(self.sample_id))
            pp.write_objects("experiments: ", self.experiments)
            pp.write_pretty_print_objects("properties: ", self.properties)
        if (len(self.processes) == 0):
            self.decorate_with_processes()
        pp.write("processes: ")
        pp.n_indent += 1
        for p in self.processes:
            pp.write(pp.str(p.name))
            pp.n_indent += 1
            pp.write("id: " + pp.str(p.id))
            pp.write_measurements(p.measurements)
            pp.n_indent -= 1

    def _process_special_objects(self):
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
        # TODO: Sample.delete(name)
        # NOTE: most likely, not a good idea - should be done by delete project?
        pass

    # Sample - additional methods
    def update_with_details(self):
        updated_sample = self.project.fetch_sample_by_id(self.id)
        updated_sample.project = self.project
        updated_sample.experiment = self.experiment
        return updated_sample

    def decorate_with_processes(self):
        filled_in_sample = make_object(api.fetch_sample_details(self.project.id, self.id))
        self.processes = filled_in_sample.processes
        return self


class Directory(MCObject):
    """
    A Materials Commons Directory. Normally created by
    project.add_directory() or any of the project methods that
    create directories on a given path.
    """
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

    def _process_special_objects(self):
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

    def add_file(self, file_name, input_path, verbose=False, limit=50):
        result = self._project.add_file_using_directory(self, file_name, input_path, verbose, limit)
        return result

    def add_directory_tree(self, dir_name, input_dir_path, verbose=False, limit=50):
        if not os_path.isdir(input_dir_path):
            return None
        if verbose:
            name = self.path
            if self.shallow:
                name = self.name
            print "base directory: ", name
        dir_tree_table = make_dir_tree_table(input_dir_path, dir_name, dir_name, {})
        result = []
        error = {}
        for relative_dir_path in dir_tree_table.keys():
            file_dict = dir_tree_table[relative_dir_path]
            dirs = self.create_descendant_list_by_path(relative_dir_path)
            if verbose:
                print "relative directory: ", relative_dir_path
            directory = dirs[-1]
            for file_name in file_dict.keys():
                input_path = file_dict[file_name]
                try:
                    result.append(directory.add_file(file_name, input_path, verbose, limit))
                except Exception as e:
                    error[input_path] = e
        return result, error


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
    """
    A Materials Commons File. Normally created by directory.add_file() when uploading a file.
    """
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

    def _process_special_objects(self):
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

    def parent(self):
        return self._project.get_directory_by_id(self._directory_id)

    def local_path(self):
        parent = self.parent()
        proj = parent._project
        proj_dirname = os_path.dirname(proj.local_path)
        return os_path.join(proj_dirname, os_path.join(parent.path, self.name))


class Template(MCObject):
    """
    A Materials Commons Sample. Only available through the top level function
    get_all_templates().
    """
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

    def pretty_print(self, shift=0, indent=2, out=sys.stdout):
        pp = PrettyPrint(shift=shift, indent=indent, out=out)
        _data = self.input_data
        pp.write("name: " + pp.str(self.name))
        pp.n_indent += 1
        value_list = ['description', 'id', 'category', 'process_type', 'destructive', 'does_transform']
        for k in value_list:
            pp.write(k + ": " + pp.str(_data[k]))

        # for 'create sample' processes
        measurements = _data['measurements']
        if len(measurements):
            pp.write("")
            pp.write("Create samples with attributes:\n")
            df = DataFrame.from_records(measurements, columns=['name', 'attribute', 'otype', 'units'])
            strout = StringIO()
            strout.write(tabulate(df, showindex=False, headers=['name', 'attribute', 'otype', 'units']))
            for line in strout.getvalue().splitlines():
                pp.write(line)

        # for process settings / attributes
        setup = _data['setup']

        # attributes are grouped, for each group print attributes
        for s in setup:
            properties = s['properties']
            if len(properties):
                pp.write("")
                pp.write("Process attributes: " + s['name'] + "\n")
                df = DataFrame.from_records(properties, columns=['name', 'attribute', 'otype', 'units'])
                strout = StringIO()
                strout.write(tabulate(df, showindex=False, headers=['name', 'attribute', 'otype', 'units']))
                for line in strout.getvalue().splitlines():
                    pp.write(line)


class Property(MCObject):
    """
    A Materials Commons Property. Normally created by
    """
    def __init__(self, data=None):
        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        super(Property, self).__init__(data)

        self.setup_id = ''
        self.property_set_id = ''
        self.parent_id = ''
        self.property_id = ''
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

    def abbrev_print(self, shift=0, indent=2, out=sys.stdout):
        self.pretty_print(shift=shift, indent=indent, out=out)

    def pretty_print(self, shift=0, indent=2, out=sys.stdout):
        pp = PrettyPrint(shift=shift, indent=indent, out=out)
        pp.write("attribute: " + pp.str(self.attribute))
        pp.n_indent += 1
        pp.write("id: " + pp.str(self.id))
        if self.best_measure is not None:
            pp.write("best_measure_id: " + pp.str(self.best_measure_id))
            pp.write_pretty_print_objects("best_measure: ", self.best_measure)
        strout = StringIO()
        strout.write(self.value)
        lines = strout.getvalue().splitlines()
        if self.value is None:
            pp.write("value: " + pp.str(self.value))
        else:
            if hasattr(self, 'unit'):
                pp.write("unit: " + pp.str(self.unit))
            elif hasattr(self, 'units'):
                pp.write("units: " + pp.str(self.units))
            if len(lines) == 1:
                pp.write("value: " + pp.str(self.value))
            else:
                pp.write("value: ")
                pp.n_indent += 1
                for line in lines:
                    pp.write(line)
                pp.n_indent -= 1


class MeasuredProperty(Property):
    def __init__(self, data=None):
        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner',
        # 'setup_id', 'required', 'unit', 'attribute', 'value', 'units', 'choices']
        super(MeasuredProperty, self).__init__(data)

        self.best_measure = []  # of Measurement
        self.best_measure_id = ''

        attr = ['best_measure_id']
        for a in attr:
            setattr(self, a, data.get(a, ''))

        attr = ['best_measure']
        for a in attr:
            setattr(self, a, data.get(a, []))

    def _process_special_objects(self):
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
        return _make_datetime(data)
    if _is_object(data):
        holder = make_base_object_for_type(data)
        for key in data.keys():
            value = copy.deepcopy(data[key])
            if _is_object(value):
                value = make_object(value)
            elif _is_list(value):
                value = map(make_object, value)
            setattr(holder, key, value)
        holder._process_special_objects()
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
        holder._process_special_objects()
        return holder
    else:
        raise Exception("No Property Object, otype not defined", data)


def make_measured_property(data):
    measurement_property = MeasuredProperty(data)
    measurement_property._process_special_objects()
    return measurement_property


class DeleteTally(object):
    """
    A Helper Class for the delete methods of Property and Experiment.
    Returned by those methods to report the id values of all objects deleted.
    Or, in the case of dry_run==True, that would be deleted.
    """
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
