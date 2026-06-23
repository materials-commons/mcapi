from .client_base import merge_dicts, set_paging_params
from .decoder import decode_file, decode_file_list, decode_paged
from .requests import UpdateFileRequest


class FileMixin:
    """
    Mixin providing file and directory API methods.

    Note: ProjectMixin and PublishedDatasetMixin call self._get_files_matching(),
    which is defined here. FileMixin must appear before those mixins in the MRO,
    or Client2's inheritance list must include FileMixin.
    """

    def get_file(self, project_id, file_id, params=None):
        """
        Get file in project.

        :param int project_id: The id of the project containing the file
        :param int file_id: The id of the file
        :param params:
        :return: The file
        :rtype: File
        :raises MCAPIError:
        """
        return self._get(f"/projects/{project_id}/files/{file_id}", params, decoder=decode_file)

    def get_file_versions(self, project_id, file_id, params=None):
        """
        Get versions for file in project (does not include file given).

        :param int project_id: The id of the project containing the file
        :param int file_id: The id of the file
        :param params:
        :return: File versions
        :rtype: File[]
        :raises MCAPIError:
        """
        return self._get(f"/projects/{project_id}/files/{file_id}/versions", params, decoder=decode_file_list)

    def set_as_active_file(self, project_id, file_id):
        """
        Set file as active version, changing current active file version to inactive.

        :param int project_id: The id of the project containing the file
        :param int file_id: The id of the file
        :return: File
        :rtype: File
        :raises MCAPIError:
        """
        return self._put(f"/projects/{project_id}/files/{file_id}/make_active", {}, decoder=decode_file)

    def get_file_by_path(self, project_id, file_path):
        """
        Get file by path in project.

        :param int project_id: The id of the project containing the file
        :param str file_path: The path to the file
        :return: The file
        :rtype: File
        :raises MCAPIError:
        """
        form = {"path": file_path.replace('\\', '/'), "project_id": project_id}
        return self._post("/files/by_path", form, decoder=decode_file)

    def update_file(self, project_id, file_id, attrs):
        """
        Update attributes of a file.

        :param int project_id: The id of the project containing the file
        :param int file_id: The id of the file
        :param UpdateFileRequest attrs: Attributes to update
        :return: The updated file
        :rtype: File
        :raises MCAPIError:
        """
        form = merge_dicts({"project_id": project_id}, attrs.to_dict())
        return self._put(f"/files/{file_id}", form, decoder=decode_file)

    def delete_file(self, project_id, file_id, force=False):
        """
        Delete a file in a project.

        :param int project_id: The id of the project containing the file
        :param int file_id: The id of the file to delete
        :param bool force: Force deletion even if file is in datasets
        :raises MCAPIError:
        """
        params = {"force": True} if force else None
        self._delete(f"/projects/{project_id}/files/{file_id}", params=params)

    def move_file(self, project_id, file_id, to_directory_id):
        """
        Move file into a different directory.

        :param int project_id: The project id of the file and the destination directory
        :param int file_id: The id of the file to move
        :param int to_directory_id: The id of the destination directory
        :return: The moved file
        :rtype: File
        :raises MCAPIError:
        """
        form = {"directory_id": to_directory_id, "project_id": project_id}
        return self._post(f"/files/{file_id}/move", form, decoder=decode_file)

    def rename_file(self, project_id, file_id, name):
        """
        Rename a file.

        :param int project_id: The project id of the file to rename
        :param int file_id: The id of the file to rename
        :param str name: The files new name
        :return: The renamed file
        :rtype: File
        :raises MCAPIError:
        """
        form = {"name": name, "project_id": project_id}
        return self._post(f"/files/{file_id}/rename", form, decoder=decode_file)

    def download_file(self, project_id, file_id, to):
        """
        Download a file.

        :param int project_id: The project id containing the file to download
        :param int file_id: The id of the file to download
        :param str to: path including file name to download file to
        :raises MCAPIError:
        """
        self._download(f"/projects/{project_id}/files/{file_id}/download", to)

    def download_file_by_path(self, project_id, path, to):
        """
        Download a file by path.

        :param int project_id: The project id containing the file to download
        :param str path: The path in the project of the file
        :param str to: path including file name to download file to
        :raises MCAPIError:
        """
        file = self.get_file_by_path(project_id, path.replace('\\', '/'))
        self.download_file(project_id, file.id, to)

    def upload_file_to_path(self, project_id, file_path, dest_path):
        """
        Uploads a file to dest_path in project.

        :param int project_id: The project to upload file to
        :param str file_path: path of file to upload
        :param str dest_path: path to upload file to
        :return: The created file
        :rtype: File
        :raises MCAPIError:
        """
        data = self._upload_to_path(f"/projects/{project_id}/files/upload-to-path", file_path, dest_path)
        return decode_file(data) if data else None

    def upload_file(self, project_id, directory_id, file_path):
        """
        Uploads a file to a project.

        :param int project_id: The project to upload file to
        :param int directory_id: The directory in the project to upload the file into
        :param str file_path: path of file to upload
        :return: The created file
        :rtype: File
        :raises MCAPIError:
        """
        data = self._upload(f"/projects/{project_id}/files/{directory_id}/upload", file_path)
        files = decode_file_list(data or [])
        return files[0] if files else None

    def upload_bytes(self, project_id, directory_id, name, f):
        """
        Uploads raw bytes to a project as a named file.

        :param int project_id: The project to upload to
        :param int directory_id: The directory to upload into
        :param str name: The name for the uploaded file
        :param f: File-like object to upload
        :return: The created file
        :rtype: File
        :raises MCAPIError:
        """
        data = self._upload_raw(f"/projects/{project_id}/files/{directory_id}/upload/{name}", f)
        files = decode_file_list(data or [])
        return files[0] if files else None

    def list_files_changed_since(self, project_id, since, starting_page=None, page_size=None):
        """
        Lists files changed (uploaded) in project since datetime in since.

        :param int project_id: The id of the project
        :param str since: The datetime to get files changed since, form "YYYY-MM-DD HH:MM:SS"
        :param int starting_page: The starting page to retrieve
        :param int page_size: Number of entries per page
        :return: Generator yielding Paged results
        :rtype: Paged
        :raises MCAPIError:
        """
        params = {"since": since}
        if starting_page is not None:
            params["page[number]"] = starting_page
        if page_size is not None:
            params["page[size]"] = page_size

        url = f"/projects/{project_id}/file-changes-since"
        files = decode_file_list(self._get(url, params) or [])
        p = decode_paged(self.r.json(), files)
        first_page = p.current_page
        last_page = p.last_page
        yield p
        for page in range(first_page + 1, last_page + 1):
            params["page[number]"] = page
            files = decode_file_list(self._get(url, params) or [])
            yield decode_paged(self.r.json(), files)

    def _get_files_matching(self, url, match, starting_page, page_size):
        params = set_paging_params({}, starting_page, page_size)
        form = {"match": match if isinstance(match, list) else [match]}

        files = decode_file_list(self._post(url, form, params=params) or [])
        p = decode_paged(self.r.json(), files)
        first_page = p.current_page
        last_page = p.last_page
        yield p
        for page in range(first_page + 1, last_page + 1):
            params["page[number]"] = page
            files = decode_file_list(self._post(url, form, params=params) or [])
            yield decode_paged(self.r.json(), files)
