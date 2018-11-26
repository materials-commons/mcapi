from os import listdir
import os.path as os_path

from . import api
from .base import MCObject
from .base import _has_key
from .mc_object_utility import make_object


class Directory(MCObject):
    """
    A Materials Commons Directory.

    .. note:: normally created from the database by call to :func:`mcapi.Project.add_directory` or
        any of the other project methods that create or fetch directories on a given path

    """

    def __init__(self, name="", path="", data=None):
        # normally, from the data base
        self.id = ""  #: directory id
        self.name = ""  #: directory name
        self.checksum = ""
        self.path = ""  #: directory path within project
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
        """
        Rename this directory. Top level directory, can not be renamed, rename project instead.
        :param new_name: string
        :return: updated directory
        """
        dir_data = api.directory_rename(self._project.id, self.id, new_name, apikey=self._project._apikey)
        updated_directory = make_object(dir_data)
        updated_directory._project = self._project
        return updated_directory

    def move(self, new_parent_directory):
        """
        Move this directory into another directory. Changes the path of this
        directory and the contents of the new parent directory.

        :param new_parent_directory: an instance of :class:`mcapi.Directory`
        :return:
        """
        project_id = self._project.id
        new_directory_id = new_parent_directory.id
        results = api.directory_move(project_id, self.id, new_parent_directory.id, apikey=self._project._apikey)
        updated_directory = make_object(results)
        updated_directory._project = self._project
        if not updated_directory._parent_id:
            updated_directory._parent_id = new_directory_id
        return updated_directory

    def put(self):
        """
        Copy local values to database.

        :return: this

        .. note:: Currently not implemented

        """
        # TODO Directory.put()
        raise NotImplementedError("Directory.put() is not implemented")
        pass

    def delete(self):
        """
        Delete this directory.

        :return: None

        .. note:: Currently not implemented

        """
        # TODO Directory.delete() ?? only when empty
        raise NotImplementedError("Directory.delete() is not implemented")
        pass

    def get_children(self):
        """
        Get the contents of this directory.

        :return: a list of :class:`mcapi.Directory` and/or :class:`mcapi.File` instances

        """
        from .File import File
        results = api.directory_by_id(self._project.id, self.id, apikey=self._project._apikey)
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
        """
        Create any directories missing on the given path, relative to this directory, and return all the
        directories on the path, the base directory first, the leaf directory last.

        :param path: string
        :return: a list of :class:`mcapi.Directory` instances
        """
        results = api.create_fetch_all_directories_on_path(
            self._project.id, self.id, path, apikey=self._project._apikey)
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
        """
        Return all the directories on the given path, relative to this directory; if any are missing
        an error is generated. See also :func:`mcapi.Directory.create_descendant_list_by_path`

        :param path: string
        :return: a list of :class:`mcapi.Directory` instances
        """
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

    def add_file(self, file_name, local_input_path, verbose=False, limit=50):
        """
        Upload local file, and attach it this directory as a new file in this directory.

        :param file_name: name of the new file - string
        :param local_input_path: path to the local file - string
        :param verbose: (optional) flag to print()trace of all actions - True or False
        :param limit: (optional) the limit in MB of the size of the file to upload
        :return: an instance of :class:`mcapi.File` - the new file
        """
        result = self._project.add_file_using_directory(self, file_name, local_input_path, verbose, limit)
        return result

    def add_directory_tree(self, dir_name, input_dir_path, verbose=False, limit=50):
        """
        Given the path to a local directory, create that directory path in the database,
        loading all the files in the tree.

        :param dir_name:
        :param input_dir_path:
        :param verbose:
        :param limit:
        :return:
        """
        if not os_path.isdir(input_dir_path):
            return None
        if verbose:
            name = self.path
            if self.shallow:
                name = self.name
            print("base directory: ", name)
        dir_tree_table = _make_dir_tree_table(input_dir_path, dir_name, dir_name, {})
        result = []
        error = {}
        for relative_dir_path in dir_tree_table.keys():
            file_dict = dir_tree_table[relative_dir_path]
            dirs = self.create_descendant_list_by_path(relative_dir_path)
            if verbose:
                print("relative directory: ", relative_dir_path)
            directory = dirs[-1]
            for file_name in file_dict.keys():
                input_path = file_dict[file_name]
                try:
                    result.append(directory.add_file(file_name, input_path, verbose, limit))
                except Exception as e:
                    error[input_path] = e
        return result, error


# -- helper function for Directory.add_directory_tree - above
def _make_dir_tree_table(base_path, dir_name, relative_base, table_so_far):
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
            table_so_far = _make_dir_tree_table(local_path, directory, base, table_so_far)
    return table_so_far
