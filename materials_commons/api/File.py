import os.path as os_path
from . import api
from .base import MCObject
from .mc_object_utility import make_object


class File(MCObject):
    """
    A Materials Commons File.

    .. note:: normally created from the database by a call to :func:`mcapi.Project.add_file_using_directory`
        or any of the other project functions that uploading a file.
    """

    def __init__(self, data=None):
        # normally, from the data base
        self.id = ""  #: file id - string
        self.name = ""  #: file name - string
        self.description = ""  #: file description - string
        self.owner = ""  #: file owner - string

        self.path = ""  #: file path - string
        self.size = 0  #: file size - long
        self.uploaded = 0
        self.checksum = ""  #: file checksum - string
        self.current = True  #: file version flag - boolean
        self.mediatype = {}  #: - directory
        self.tags = []  #: - array of string
        self.notes = []  #: - array of string

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

        attr = ['size', 'uploaded', 'checksum', 'current', 'owner', 'usesid', 'direction']
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
        """
        Rename this file.

        :param new_file_name: string
        :return: the updated file
        """
        project_id = self._project.id
        file_id = self.id
        results = api.file_rename(project_id, file_id, new_file_name, apikey=self._project._apikey)
        updated_file = make_object(results)
        updated_file._project = self._project
        return updated_file

    def move(self, new_directory):
        """
        Move this file to another directory.

        :param new_directory: the :class:`mcapi.Directory` instance of the new location
        :return: the updated file
        """
        project_id = self._project.id
        old_directory_id = self._directory_id
        new_directory_id = new_directory.id
        results = api.file_move(project_id, old_directory_id, new_directory.id, self.id, apikey=self._project._apikey)
        updated_file = make_object(results)
        updated_file._project = self._project
        updated_file._directory_id = new_directory_id
        return updated_file

    def put(self):
        """
        Copy local values to database.

        :return: this

        .. note:: Currently not implemented

        """
        # TODO File.put()
        raise NotImplementedError("File.put() is not implemented")
        pass

    def delete(self):
        """
        Delete this file from the database.

        :return: None

        .. note:: Currently not implemented

        """
        # TODO File.delete()
        raise NotImplementedError("File.delete() is not implemented")
        pass

    # File - additional methods
    def download_file_content(self, local_download_file_path):
        """
        Download a copy of the file from the database into a local file on a local path.
        Will overwrite any existing file with the same name.

        :param local_download_file_path: the local path ending in the intended file name.
        :return: the output file path
        """
        project_id = self._project.id
        file_id = self.id
        output_file_path = api.file_download(
            project_id, file_id, local_download_file_path, apikey=self._project._apikey)
        return output_file_path

    def get_parent(self):
        """

        :return: the parent :class:`mcapi.Directory` instance
        """
        # TODO File.get_parent()
        message = "File.get_parent() is not implemented - previous implemation was incorrect"
        raise NotImplementedError(message)
        # Note: this was discovered to be working incorrectly - Terry - March 2018
        # return self._project.get_directory_by_id(self._directory_id)

    def local_path(self):
        """
        In the context of the project for this file, assuming that project.local_path is set for that project,
        get the local_path indicated by this files database path and name.

        :return: the full local path of this file including the filename.
        """
        parent = self._project.get_directory_by_id(self._directory_id)
        # NOTE: there may be problems with the above - only works in the context of using local_path
        # -- that is self._directory_id is set when the file is created using local_path, but
        # -- not in other contexts
        proj = parent._project
        proj_dirname = os_path.dirname(proj.local_path)
        return os_path.join(proj_dirname, os_path.join(parent.path, self.name))
