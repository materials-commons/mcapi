from .client_base import merge_dicts
from .decoder import decode_file, decode_file_list
from .requests import CreateDirectoryRequest, UpdateDirectoryRequest


class DirectoryMixin:
    def get_directory(self, project_id, directory_id, params=None):
        """
        Get a directory in the project.

        :param int project_id: The id of the project the directory is in
        :param int directory_id: The directory id
        :param params:
        :return: The directory
        :rtype: File
        :raises MCAPIError:
        """
        return self._get(f"/projects/{project_id}/directories/{directory_id}", params, decoder=decode_file)

    def list_directory(self, project_id, directory_id, params=None):
        """
        Return a list of all the files and directories in a given directory.

        :param int project_id: The id of the project the directory is in
        :param int directory_id: The directory id
        :param params:
        :return: A list of the files and directories in the given directory
        :rtype: File[]
        :raises MCAPIError:
        """
        return self._get(f"/projects/{project_id}/directories/{directory_id}/list", params, decoder=decode_file_list)

    def list_directory_by_path(self, project_id, path, params=None):
        """
        Return a list of all the files and directories at given path.

        :param int project_id: The id of the project the path is in
        :param str path:
        :param params:
        :return: A list of the files and directories in the given path
        :rtype: File[]
        :raises MCAPIError:
        """
        path_param = {"path": path.replace('\\', '/')}
        return self._get(f"/projects/{project_id}/directories_by_path", params, path_param, decoder=decode_file_list)

    def create_directory(self, project_id, name, parent_id, attrs=None):
        """
        Create a new directory in project in the given directory.

        :param int project_id: The id of the project the directory will be created in
        :param str name: Name of directory
        :param int parent_id: Parent directory id
        :param CreateDirectoryRequest attrs: Additional attributes on the directory
        :return: The created directory
        :rtype: File
        :raises MCAPIError:
        """
        if not attrs:
            attrs = CreateDirectoryRequest()
        form = merge_dicts({"name": name, "directory_id": parent_id, "project_id": project_id}, attrs.to_dict())
        return self._post("/directories", form, decoder=decode_file)

    def move_directory(self, project_id, directory_id, to_directory_id):
        """
        Moves a directory into another directory.

        :param int project_id: The project id that target and destination directories are in
        :param int directory_id: Id of directory to move
        :param int to_directory_id: Id of the destination directory
        :return: The directory that was moved
        :rtype: File
        :raises MCAPIError:
        """
        form = {"to_directory_id": to_directory_id, "project_id": project_id}
        return self._post(f"/directories/{directory_id}/move", form, decoder=decode_file)

    def rename_directory(self, project_id, directory_id, name):
        """
        Rename a given directory.

        :param int project_id: The project id that the directory is in
        :param int directory_id: The id of the directory being renamed
        :param str name: The new name of the directory
        :return: The directory that was renamed
        :rtype: File
        :raises MCAPIError:
        """
        form = {"name": name, "project_id": project_id}
        return self._post(f"/directories/{directory_id}/rename", form, decoder=decode_file)

    def delete_directory(self, project_id, directory_id):
        """
        Delete a directory only if the directory is empty.

        :param int project_id: The project id containing the directory to delete
        :param int directory_id: The id of the directory to delete
        :raises MCAPIError:
        """
        self._delete(f"/projects/{project_id}/directories/{directory_id}")

    def update_directory(self, project_id, directory_id, attrs):
        """
        Update attributes on a directory.

        :param int project_id: The project id containing the directory
        :param int directory_id: The id of the directory to update
        :param UpdateDirectoryRequest attrs: Attributes to update
        :return: The updated directory
        :rtype: File
        :raises MCAPIError:
        """
        form = merge_dicts({"project_id": project_id}, attrs.to_dict())
        return self._put(f"/directories/{directory_id}", form, decoder=decode_file)
