import sys

import hashlib
import os.path as os_path
from os import getcwd

from . import api
from .File import File
from .base import MCObject, PrettyPrint, _decorate_object_with, MCGenericException
from .mc_object_utility import make_object
from .GlobusUploadRequest import GlobusUploadRequest
from .GlobusUploadStatus import GlobusUploadStatus
from .GlobusDownloadRequest import GlobusDownloadRequest


class Project(MCObject):
    """
    A Materials Commons Project.

    .. note:: normally created from the database by call to the top level function :func:`mcapi.create_project`.

    """

    def __init__(self, name="", description="", remote_url="", data=None, apikey=None):
        # normally, from the data base
        self.id = ""  #: project id - string (from database)
        self.name = ""  #: project name - string (from database)
        self.description = ""  #: project description - string (from database)
        self.size = 0
        self.mediatypes = {}

        self.__all_db_Fields__ = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner',
                                  'size', 'mediatypes']

        # additional fields
        self._top = None
        self._apikey = apikey
        self.source = remote_url  #: remote URL for this project - string (local only - not in database)

        if not data:
            data = {}

        # holds Datafile, using id for key;  initially empty, additional calls needed to fill
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
        """
        Prints a nice layout of the object and all of it's values.

        :param shift: the offset from the start of the line, in increments of indent
        :param indent: the indent used for layout, in characters
        :param out: the stream to which the object in printed
        :return: None
        """
        pp = PrettyPrint(shift=shift, indent=indent, out=out)
        pp.write("name: " + pp.str(self.name))
        pp.n_indent += 1
        pp.write("description: " + pp.str(self.description))
        pp.write("id: " + self.id)
        pp.write("owner: " + pp.str(self.owner))
        # todo: print()time rep; see issue #1131
        # pp.write("mtime: " + pp.str(self.mtime.strftime("%b %Y %d %H:%M:%S")))

    def _process_special_objects(self):
        pass

    # Project - basic methods: rename, put, delete

    def rename(self, name, description=None):
        """
        Change the name and (optionally) description of a project.
        Default description is the current description.
        Returns the new project from the database.

        :param name: new name for project
        :param description: (optional) new description for project; if not given, descriptions is unchanged,
        :return: an instance of :class: `mcapi.Project`

        """
        if not description:
            description = self.description
        results = api.update_project(self.id, name, description, apikey=self._apikey)
        project_id = results['id']
        from .top_level_api_functions import get_project_by_id
        project = get_project_by_id(project_id, apikey=self._apikey)
        return project

    def put(self):
        """
        Copy local values to database.

        .. note:: Not currently implemented. All functions that change the object also update
            the object in the database; for example, :func:`mcapi.Project.rename`

        """
        # TODO: Project.put()
        raise NotImplementedError("Project.put() is not implemented")
        pass

    def delete(self):
        """
        Delete this project from the database.

        :return: a the id the deleted project or None if the delete failed.

        """
        results = None
        try:
            results = api.delete_project(self.id, apikey=self._apikey)
            results = results['project_id']
        except MCGenericException:
            print("Delete of project failed: ", self.name, "(" + self.id + ")")

        return results

    # Project - Experiment-related methods - basic: create, get_by_id, get_all (in context)

    def create_experiment(self, name, description):
        """
        Create and return an Experiment in this project.

        :param name: name for the Experiment
        :param description: description for the Experiment
        :return: a :class:`mcapi.Experiment` instance

        >>> from materials_commons.api import get_project_by_id
        >>> project_id = "somthing here"
        >>> project = get_project_by_id(project_id)
        >>> experiment = project.create_experiment("Experiment 1", "Test Procedures")

        """
        experiment_json_dict = api.create_experiment(self.id, name, description, apikey=self._apikey)
        experiment = make_object(experiment_json_dict)
        experiment.project = self
        return experiment

    def get_experiment_by_id(self, *args):  # , experiment_id):
        """

        .. note:: Currently not implemented. Instead use :func:`get_all_experiments` to get
            the experiments and from that list, compare id values to find the experiment required.

        """
        # TODO: Project.get_experiment_by_id(id)
        raise NotImplementedError("Project.get_experiment_by_id(id) not implemented: " + str(len(args)))
        pass

    def get_all_experiments(self):
        """
        Get a list of all the experiments in this project.

        :return: a list of :class:`mcapi.Experiment` instances

        >>> from materials_commons.api import get_project_by_id
        >>> project_id = "somthing here"
        >>> project = get_project_by_id(project_id)
        >>> experiment_list = project.get_all_experiments()
        >>> for experiment in experiment_list:
        >>>     print(experiment.id, experiment.name)

        """
        list_results = api.fetch_experiments(self.id, apikey=self._apikey)
        experiments = [make_object(o) for o in list_results]
        experiments = [_decorate_object_with(x, 'project', self) for x in experiments]
        return experiments

    # Project - Directory-related methods - basic: create, get_by_id, get_all (in context)

    def create_directory(self):  # , name, path):
        """

        .. note:: Currently not implemented; use :func:`mcapi.Project.add_directory`

        """
        # TODO: Project.create_directory(name, path)
        raise NotImplementedError("Project.create_directory(name, path) not implemented")
        pass

    def get_directory_by_id(self, directory_id):
        """ Gets the indicated directory.

        :param directory_id: The id of the directory to fetch.
        :type directory_id: str.
        :return: a :class:`mcapi.Directory` instance

        >>> from materials_commons.api import get_project_by_id
        >>> project_id = "somthing here"
        >>> project = get_project_by_id(project_id)
        >>> directory = project.get_directory_by_id('876655a2-c31b-4895-8766-40a168ea1a87')
        >>> print(directory.path)

        """

        results = api.directory_by_id(self.id, directory_id, apikey=self._apikey)
        directory = make_object(results)
        directory._project = self
        directory.shallow = False
        return directory

    def get_all_directories(self):
        """
        Get a list of all the directories in this project.

        :return: a list :class:`mcapi.Directory` instances

        >>> from materials_commons.api import get_project_by_id
        >>> project_id = "somthing here"
        >>> project = get_project_by_id(project_id)
        >>> directory_list = project.get_all_directories()
        >>> for directory in directory_list:
        >>>     print(directory.name, directory.path)

        """

        results = api.directory_by_id(self.id, "all", apikey=self._apikey)
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
        Get the top level directory.

        :return: a :class:`mcapi.Directory` instance

        >>> from materials_commons.api import get_project_by_id
        >>> project_id = "somthing here"
        >>> project = get_project_by_id(project_id)
        >>> directory = project.get_top_directory()

        """
        if not self._top:
            results = api.directory_by_id(self.id, "top", apikey=self._apikey)
            directory = make_object(results)
            directory._project = self
            self._set_top_directory(directory)
        return self._top

    def get_directory_list(self, path):
        """
        Given a directory path, returns a list of all the directories on the path.
        Can fail if the path does not exist.

        :param path: the path, within the project, of the directory - string
        :return: a list of :class:`mcapi.Directory` instances

        >>> # In this example, the list would consist of three directories, assuming that they exist:
        >>> #   the Root directory (or 'top' directory)
        >>> #   directory 'A'
        >>> #   directory 'B'
        >>>
        >>> from materials_commons.api import get_project_by_id
        >>> project_id = "somthing here"
        >>> project = get_project_by_id(project_id)
        >>> directory_list = project.get_directory_list("/A/B")
        >>> print(len(directory_list))
        >>> for directory in directory_list:
        >>>     print(directory.name, directory.path)

        """

        top_directory = self.get_top_directory()
        return top_directory.get_descendant_list_by_path(path)

    def get_directory(self, directory_id):
        """
        Get the indicated directory.

        :param directory_id: - the id of the intended directory - string
        :return: a :class:`mcapi.Directory` instance

        >>> from materials_commons.api import get_project_by_id
        >>> project_id = "somthing here"
        >>> project = get_project_by_id(project_id)
        >>> directory = project.get_directory("352eb9b1-8553-4be5-8c08-cbb496ef60ea")
        >>> print(directory.path)

        """
        return self.get_directory_by_id(directory_id)

    def create_or_get_all_directories_on_path(self, path):
        """
        Given a directory path, returns a list of all the directories on the path.
        If a directory is missing, in the path, it is created and returned in the list.

        :param path: the path, within the project, of the directory - string
        :return: a list of :class:`mcapi.Directory` instances

        >>> # In this example, the list would consist of three directories, where
        >>> # any missing directory would be have been created:
        >>> #   the Root directory (or 'top' directory)
        >>> #   directory 'A'
        >>> #   directory 'B'
        >>>
        >>> from materials_commons.api import get_project_by_id
        >>> project_id = "somthing here"
        >>> project = get_project_by_id(project_id)
        >>> directory_list = project.get_directory_list("/A/B")
        >>> print(len(directory_list))
        >>> for directory in directory_list:
        >>>     print(directory.name, directory.path)

        """

        directory = self.get_top_directory()
        if path == "/":
            return [directory]
        if path.endswith("/"):
            path = path[0:-1]
        return directory.create_descendant_list_by_path(path)

    def add_directory(self, path):
        """
        Given a directory path, returns the last directory on the path.
        If a directory is missing, in the path, it is created.

        :param path: the path, within the project, of the directory - string
        :return: a :class:`mcapi.Directory` instance

        >>> from materials_commons.api import get_project_by_id
        >>> project_id = "somthing here"
        >>> project = get_project_by_id(project_id)
        >>> directory = project.add_directory("/A/B")
        >>> print(directory.name, directory.path)

        """

        # TODO: Project.add_directory(path) - refactor this should check for and fail if path does not exist
        # TODO: Project.add_directory(path) - refactor add optional flag to create parent path if it does not exist
        directory = self.create_or_get_all_directories_on_path(path)[-1]
        directory._project = self
        return directory

    def add_directory_list(self, path_list, top=None):
        """
        Given a list of directory paths, create all the directories in the path; this is be most efficient
        if the paths in the list are all leaf directories in the desired tree. The intent of this
        method is to support rapid upload of multiple files by pre-creating the needed directories.

        :param path_list: a list of project directory paths, limit 100;
            see :func:`mcapi.Project.add_directory` for more information
        :param top: (optional) an instance of :class:`materials_commons.api.Directory` - if given will be use
            as the top level directory for the request; otherwise the project's root directory
            is used
        :return: a dictionary, indexed by path of the ids of the created directories,
            see :func:`mcapi.Project.get_directory` to get a directory by it's id.

        >>> from materials_commons.api import get_project_by_id
        >>> project_id = "somthing here"
        >>> project = get_project_by_id(project_id)
        >>> directory_path_list = ['/a/b/c', '/a/b/e', '/a/f/g']
        >>> directory_id_table = project.add_directory_list(directory_path_list)
        >>> for path in directory_path_list:
        >>>     directory_id = directory_id_table[path]
        >>>     directory = project.get_directory(directory_id)
        >>>     print(path, directory.path()

        """
        if len(path_list) > 100:
            raise ValueError('list of directory paths is limited to 100 in length')
        base_directory = top
        if not base_directory:
            base_directory = self.get_top_directory()
        new_path_list = []
        for path in path_list:
            if not path.startswith('/'):
                path = "/" + path
            new_path_list.append(path)
        results = api.directory_create_subdirectories_from_path_list(
            self.id, base_directory.id, new_path_list, apikey=self._apikey)
        data = results['val']
        table = {}
        project_name = self.name
        for key in data:
            relative_path = key[len(project_name):]
            table[relative_path] = make_object(data[key])
        return table

    def add_file_using_directory(self, directory, file_name, local_path, verbose=False, limit=50):
        """
        Given a directory, a file_name, a local directory path to the file -
        uploads the file, creates a file descriptor in the database, and returns file descriptor.

        :param directory: a class:`mcapi.Directory` instance, a directory in the project
        :param file_name: the name that file is to take within the project directory
        :param local_path: the local path to the file
        :param verbose: (optional) a Flag; if true print()out a trace of the actions
        :param limit: (optional) the maximum number of MB to be uploaded
        :return: the :class:`mcapi.File` instance representing the uploaded file

        >>> from materials_commons.api import get_project_by_id
        >>> project_id = "somthing here"
        >>> project = get_project_by_id(project_id)
        >>> directory = project.add_directory("/A/B")
        >>> file = project.add_file_using_directory(directory,"Test-Results","/tmp/results.txt")
        >>> print(file.name)

        """
        file_size_mb = os_path.getsize(local_path) >> 20
        if file_size_mb > limit:
            msg = "File too large (>{0}MB), skipping. File size: {1}M".format(limit, file_size_mb)
            raise MCGenericException(msg)
        if verbose:
            print("uploading:", os_path.relpath(local_path, getcwd()), " as:", file_name)
        project_id = self.id
        directory_id = directory.id
        results = api.file_upload(project_id, directory_id, file_name, local_path, apikey=self._apikey)
        uploaded_file = make_object(results)
        uploaded_file._project = self
        uploaded_file._directory = directory
        uploaded_file._directory_id = directory.id
        return uploaded_file

    def add_file_by_local_path(self, local_path, verbose=False, limit=50):
        """
        Upload a file, specified by local_path, creating intermediate
        directories as necessary; the file name on the directory of the project (remote) is the
        file name from the local path. See :func:`mcapi.Project.add_file_using_directory`.

        .. note This functions assumes the setting on setting of local_path on the project, see example

        :param local_path: the local path to the file
        :param verbose: (optional) a Flag; if true print()out a trace of the actions
        :param limit: (optional) the maximum number of MB to be uploaded
        :return: the :class:`mcapi.File` instance representing the uploaded file

        >>> from materials_commons.api import get_project_by_id
        >>> project_id = "somthing here"
        >>> project = get_project_by_id(project_id)
        >>> # uploads file_A.txt from the local path /path/to/Proj/test_dir/file_A.txt
        >>> # returns File object representing file_A.txt at project directory /test_dir
        >>> project.local_path = "/path/to/Proj"
        >>> local_path = project.local_path + "/test_dir/file_A.txt"
        >>> file = project.add_file_by_local_path(local_path)

        """
        dir_path = self._local_path_to_path(os_path.dirname(local_path))
        directory = self.create_or_get_all_directories_on_path(dir_path)[-1]
        return self.add_file_using_directory(directory, os_path.basename(local_path),
                                             local_path, verbose, limit)

    def add_directory_tree_by_local_path(self, local_path, verbose=False, limit=50):
        """
        Upload a directory, specified by local_path, and all its contents
        creating intermediate directories as necessary; the directory name,
        in project (remote), is the same as the local directory name.

        .. note This functions assumes the setting on setting of local_path on the project, see example

        :param local_path: the local path to the directory
        :param verbose: (optional) a Flag; if true print()out a trace of the actions
        :param limit: (optional) the maximum number of MB to be uploaded for any file in the path
        :return: the :class:`mcapi.Directory` instance representing the uploaded directory

        >>> from materials_commons.api import get_project_by_id
        >>> project_id = "somthing here"
        >>> project = get_project_by_id(project_id)
        >>> # uploads dir_A and all of it's contents
        >>> # returns Directory object representing project directory /test_dir/dir_a
        >>> project.local_path = "/path/to/Proj"
        >>> local_path = project.local_path + "/test_dir/dir_A" # a local directory
        >>> file = project.add_directory_tree_by_local_path(local_path)

        """
        path = self._local_path_to_path(os_path.dirname(local_path))
        directory = self.create_or_get_all_directories_on_path(path)[-1]
        return directory. \
            add_directory_tree(os_path.basename(local_path),
                               os_path.dirname(local_path), verbose, limit)

    # Project - File or Directory-related methods - basic: get_by_local_path
    def get_by_local_path(self, local_path):
        """
        Uses path on local machine to get a the matching File or Directory in the project.
        Return None if the local file or directory does not match one in the project.

        :param local_path: file or directory local path equivalent.
        :return: one of :class:`mcapi.File`, :class:'mcapi.Directory`, or None.

        >>> from materials_commons.api import get_project_by_id
        >>> project_id = "somthing here"
        >>> project = get_project_by_id(project_id)
        >>> project.local_path = "/path/to/Proj"
        >>> local_path = project.local_path + "/test_dir/dir_A" # a local directory
        >>> directory = project.get_by_local_path(local_path)
        >>> if directory:
        >>>     print(directory.path)

        """
        if self.local_path is None:
            msg = "Error in Project.get_by_local_path: Project.local_path is None"
            raise MCGenericException(msg)
        if os_path.abspath(local_path) == self.local_path:
            return self.get_top_directory()
        names = os_path.relpath(local_path, self.local_path).split('/')
        curr = self.get_top_directory()
        for n in names:
            nextchild = list(filter(lambda x: x.name == n, curr.get_children()))
            if len(nextchild) == 0:
                return None
            curr = nextchild[0]
        return curr

    def file_exists_by_local_path(self, local_path, checksum=False):
        """
        Check if files exists locally and remotely. Optionally compares md5 hash.

        :param local_path: file or directory local path equivalent.
        :param checksum: (optional) a flag (True) to compare local and remote checksums
        :return: file_exists [, checksums_are_equal] - both Boolean

        Return Values::

            **file_exists** is True file exists locally and remotely
            **checksums_are_equal** (when requested by checksum=True)
                is True when both files exist and have the same checksum value

        >>> from materials_commons.api import get_project_by_id
        >>> project_id = "somthing here"
        >>> project = get_project_by_id(project_id)
        >>> project.local_path = "/path/to/Proj"
        >>> local_path = project.local_path + "/test_dir/dir_A" # a local directory
        >>> files_ok, checksums_ok = project.file_exists_by_local_path(local_path, checksum = True)
        >>> if files_ok and checksums_ok:
        >>>     print(local_path + " found on on remote site.")

        """
        if os_path.exists(local_path) and os_path.isfile(local_path):
            obj = self.get_by_local_path(local_path)
            if isinstance(obj, File):
                if checksum:
                    with open(local_path, 'rb') as f:
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

        :return: a list of :class:`mcapi.Process` - the processes for the Project

        >>> from materials_commons.api import get_project_by_id
        >>> project_id = "somthing here"
        >>> project = get_project_by_id(project_id)
        >>> process_list = project.get_all_processes()
        >>> for process in process_list:
        >>>     print(process.name)

        """
        process_list = api.get_project_processes(self.id, self.remote, apikey=self._apikey)
        processes = [make_object(x) for x in process_list]
        processes = [_decorate_object_with(x, 'project', self) for x in processes]
        return processes

    def get_process_by_id(self, process_id):
        """
        Get a project sample by process id.

        :param process_id: the process id value - string
        :return: a class:`mcapi.Process`  - the intended process

        >>> from materials_commons.api import get_project_by_id
        >>> project_id = "somthing here"
        >>> project = get_project_by_id(project_id)
        >>> process = project.get_process_by_id(process.id)

        """
        results = api.get_process_by_id(self.id, process_id, apikey=self._apikey)
        process = make_object(results)
        process.project = self
        process._update_project_experiment()
        return process

    # Project - Samples

    def get_all_samples(self):
        """
        Get a list of all samples in this project.

        :return: a list of :class:`mcapi.Sample` - the samples for the Project

        >>> from materials_commons.api import get_project_by_id
        >>> project_id = "somthing here"
        >>> project = get_project_by_id(project_id)
        >>> sample_list = project.get_all_samples()
        >>> for sample in sample_list:
        >>>     print(sample.name)

        """
        samples_list = api.get_project_samples(self.id, self.remote, apikey=self._apikey)
        samples = [make_object(x) for x in samples_list]
        samples = [_decorate_object_with(x, 'project', self) for x in samples]
        return samples

    def fetch_sample_by_id(self, sample_id):
        # TODO: determine and document the difference between mcapi.fetch_sample_by_id and mcapi.get_sample_by_id
        """
        Get the sample in question.

        :param sample_id: the sample id value - string
        :return: a class:`mcapi.Sample` - the intended sample

        >>> from materials_commons.api import get_project_by_id
        >>> project_id = "somthing here"
        >>> project = get_project_by_id(project_id)
        >>> sample = project.fetch_sample_by_id(sample.id)

        ..todo:: determine and document the difference between mcapi.fetch_sample_by_id and mcapi.get_sample_by_id

        """
        sample_json_dict = api.get_project_sample_by_id(self.id, sample_id, apikey=self._apikey)
        sample = make_object(sample_json_dict)
        sample.project = self
        return sample

    def get_sample_by_id(self, sample_id):
        # TODO: determine and document the difference between mcapi.fetch_sample_by_id and mcapi.get_sample_by_id
        """
        Get the sample in question.

        :param sample_id: the sample id value - string
        :return: a class:`mcapi.Sample` - the intended sample

        >>> from materials_commons.api import get_project_by_id
        >>> project_id = "somthing here"
        >>> project = get_project_by_id(project_id)
        >>> sample = project.get_sample_by_id(sample.id)

        ..todo:: determine and document the difference between mcapi.fetch_sample_by_id and mcapi.get_sample_by_id

        """
        results = api.get_sample_by_id(self.id, sample_id, apikey=self._apikey)
        sample = make_object(results)
        sample.project = self
        return sample

    # Project - users with access to project
    def get_access_list(self):
        """
        Get the list of users with access to this project (actually their id's; which are their e-mail addresses)

        :return: a list of string - the id/email of each user with access

        >>> from materials_commons.api import get_project_by_id
        >>> project_id = "somthing here"
        >>> project = get_project_by_id(project_id)
        >>> user_id_list = project.get_access_list()

        """
        results = api.users_with_access_to_project(self.id, apikey=self._apikey)
        user_list = []
        if results['val']:
            for record in results['val']:
                user_list.append(record['user_id'])
        return user_list

    def add_user_to_access_list(self, new_user):
        """

        Add a user, by user id, to the access list of this project.

        :param new_user: the user_id of the user to add
        :return: string - the user_id, if added; otherwise error message
        """
        results = api.add_user_access_to_project(self.id, new_user, apikey=self._apikey)
        if 'error' in results:
            return results['error']
        return results['val']

    def remove_user_from_access_list(self, user_to_remote):
        """

        Remove a user, by user id, form the access list of this project.

        :param user_to_remote: the user_id of the user to the user to remove
        :return: string - the user_id (in any case)
        """
        results = api.remove_user_access_to_project(self.id, user_to_remote, apikey=self._apikey)
        if 'error' in results:
            return results['error']
        return results['val']

    # Project - globus
    def create_globus_upload_request(self):
        results = api.create_globus_upload_request(self.id, apikey=self._apikey)
        ret = GlobusUploadRequest(results)
        return ret

    def get_globus_upload_status_list(self):
        results = api.get_globus_upload_status_list(self.id, apikey=self._apikey)
        status_list = []
        if results['value']:
            status_list = [GlobusUploadStatus(x) for x in results["value"] ]
        return status_list

    def create_globus_download_request(self):
        results = api.create_globus_download_request(self.id, apikey=self._apikey)
        ret = GlobusDownloadRequest(results)
        return ret
