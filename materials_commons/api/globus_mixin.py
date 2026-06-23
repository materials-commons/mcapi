from .decoder import (
    decode_globus_upload,
    decode_globus_upload_list,
    decode_globus_download,
    decode_globus_download_list,
    decode_globus_transfer,
)


class GlobusMixin:
    def create_globus_upload_request(self, project_id, name):
        """
        Create a new globus upload request in the given project.

        :param int project_id: The project id for the upload
        :param str name: The name of the request
        :return: The globus upload request
        :rtype: GlobusUpload
        :raises MCAPIError:
        """
        form = {"project_id": project_id, "name": name}
        return self._post("/globus/uploads", form, decoder=decode_globus_upload)

    def delete_globus_upload_request(self, project_id, globus_upload_id):
        """
        Delete an existing globus upload request.

        :param int project_id:
        :param int globus_upload_id:
        :raises MCAPIError:
        """
        self._delete(f"/projects/{project_id}/globus/{globus_upload_id}/uploads")

    def finish_globus_upload_request(self, project_id, globus_upload_id):
        """
        Mark a globus upload request as finished.

        :param int project_id: The project id for the upload
        :param int globus_upload_id: The id of the globus upload
        :return: The globus upload
        :rtype: GlobusUpload
        :raises MCAPIError:
        """
        form = {"project_id": project_id}
        return self._put(f"/globus/{globus_upload_id}/uploads/complete", form, decoder=decode_globus_upload)

    def get_all_globus_upload_requests(self, project_id, params=None):
        """
        Get all globus uploads in a project.

        :param int project_id: The project id
        :param params:
        :return: List of globus uploads
        :rtype: GlobusUpload[]
        :raises MCAPIError:
        """
        return self._get(f"/projects/{project_id}/globus/uploads", params, decoder=decode_globus_upload_list)

    def create_globus_download_request(self, project_id, name):
        """
        Create a globus download request for a project.

        :param int project_id:
        :param str name: The name of the download request
        :return: The globus download
        :rtype: GlobusDownload
        :raises MCAPIError:
        """
        form = {"project_id": project_id, "name": name}
        return self._post("/globus/downloads", form, decoder=decode_globus_download)

    def delete_globus_download_request(self, project_id, globus_download_id):
        """
        Delete an existing globus download request.

        :param int project_id: The id of the project containing the download request
        :param int globus_download_id: The id of the globus download to delete
        :raises MCAPIError:
        """
        self._delete(f"/projects/{project_id}/globus/{globus_download_id}/downloads")

    def get_all_globus_download_requests(self, project_id, params=None):
        """
        Get all globus download requests for a project.

        :param int project_id: The project
        :param params:
        :return: List of all globus downloads
        :rtype: GlobusDownload[]
        :raises MCAPIError:
        """
        return self._get(f"/projects/{project_id}/globus/downloads", params, decoder=decode_globus_download_list)

    def get_globus_download_request(self, project_id, globus_download_id, params=None):
        """
        Get a globus download.

        :param int project_id: The id of the project containing the globus download
        :param int globus_download_id: The globus download id
        :param params:
        :return: The globus download
        :rtype: GlobusDownload
        :raises MCAPIError:
        """
        return self._get(
            f"/projects/{project_id}/globus/downloads/{globus_download_id}",
            params, decoder=decode_globus_download)

    def open_globus_transfer(self, project_id, params=None):
        """
        Open a globus transfer request for current user in project. If one is already
        active then it returns the already active request.

        :param int project_id: The id of the project associated with this globus transfer
        :param params:
        :return: The globus transfer
        :rtype: GlobusTransfer
        :raises MCAPIError:
        """
        return self._get(f"/projects/{project_id}/globus/open", params, decoder=decode_globus_transfer)

    def close_globus_transfer(self, project_id):
        """
        Closes an existing globus transfer.

        :param int project_id: The id of the project to close globus transfer for the current user
        :raises MCAPIError:
        """
        self._get_no_value(f"/projects/{project_id}/globus/close")
