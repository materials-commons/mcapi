from .decoder import (
    decode_dataset,
    decode_dataset_list,
    decode_file,
    decode_file_list,
    decode_entity_list,
    decode_activity_list,
    decode_searchable_list,
)


class PublishedDatasetMixin:
    """
    Mixin providing published dataset API methods.

    Note: _get_files_matching is provided by FileMixin via MRO.
    Note: _download is provided by ClientBase.
    """

    def get_all_published_datasets(self, params=None):
        """
        Get all published datasets.

        :param params:
        :return: The list of published datasets
        :rtype: Dataset[]
        :raises MCAPIError:
        """
        return self._get("/published/datasets", params, decoder=decode_dataset_list)

    def get_published_dataset(self, dataset_id, params=None):
        """
        Get published dataset.

        :param int dataset_id: The dataset id
        :param params:
        :return: The dataset
        :rtype: Dataset
        :raises MCAPIError:
        """
        return self._get(f"/published/datasets/{dataset_id}", params, decoder=decode_dataset)

    def get_published_dataset_files(self, dataset_id, params=None):
        """
        Get files for a published dataset.

        :param int dataset_id: The dataset id
        :param params:
        :return: The files
        :rtype: File[]
        :raises MCAPIError:
        """
        return self._get(f"/published/datasets/{dataset_id}/files", params, decoder=decode_file_list)

    def get_published_dataset_directory(self, dataset_id, directory_id, params=None):
        """
        Get a directory in a published dataset.

        :param int dataset_id: The id of the published dataset the directory is in
        :param int directory_id: The directory id
        :param params:
        :return: The directory
        :rtype: File
        :raises MCAPIError:
        """
        return self._get(
            f"/published/datasets/{dataset_id}/directories/{directory_id}",
            params, decoder=decode_file)

    def list_published_dataset_directory(self, dataset_id, directory_id, params=None):
        """
        Return a list of all the files and directories in a given published dataset directory.

        :param int dataset_id: The id of the dataset the directory is in
        :param int directory_id: The directory id
        :param params:
        :return: A list of the files and directories in the given directory
        :rtype: File[]
        :raises MCAPIError:
        """
        return self._get(
            f"/published/datasets/{dataset_id}/directories/{directory_id}/list",
            params, decoder=decode_file_list)

    def list_published_dataset_directory_by_path(self, dataset_id, path, params=None):
        """
        Return a list of all the files and directories at given path in a published dataset.

        :param int dataset_id: The id of the dataset the path is in
        :param str path:
        :param params:
        :return: A list of the files and directories in the given path
        :rtype: File[]
        :raises MCAPIError:
        """
        path_param = {"path": path.replace('\\', '/')}
        return self._get(
            f"/published/datasets/{dataset_id}/directories_by_path",
            params, path_param, decoder=decode_file_list)

    def get_published_dataset_entities(self, dataset_id, params=None):
        """
        Get entities for a published dataset.

        :param int dataset_id: The dataset id
        :param params:
        :return: The entities
        :rtype: Entity[]
        :raises MCAPIError:
        """
        return self._get(f"/published/datasets/{dataset_id}/entities", params, decoder=decode_entity_list)

    def get_published_dataset_activities(self, dataset_id, params=None):
        """
        Get activities for a published dataset.

        :param int dataset_id: The dataset id
        :param params:
        :return: The activities
        :rtype: Activity[]
        :raises MCAPIError:
        """
        return self._get(f"/published/datasets/{dataset_id}/activities", params, decoder=decode_activity_list)

    def get_all_published_dataset_files_matching(self, match, starting_page=None, page_size=None):
        return self._get_files_matching("/published/datasets/files/matching", match, starting_page, page_size)

    def get_published_dataset_files_matching(self, dataset_id, match, starting_page=None, page_size=None):
        return self._get_files_matching(
            f"/published/datasets/{dataset_id}/files/matching", match, starting_page, page_size)

    def download_published_dataset_zipfile(self, dataset_id, to):
        """
        Download the zipfile for a published dataset.

        :param int dataset_id: The id of the published dataset
        :param str to: The path including the file name to write the download to
        :raises MCAPIError:
        """
        self._download(f"/published/datasets/{dataset_id}/download_zipfile", to)

    def download_published_dataset_file(self, dataset_id, file_id, to):
        """
        Download file from a published dataset.

        :param int dataset_id: The id of the published dataset
        :param int file_id: The id of the file in the dataset
        :param str to: The path including the file name to write the download to
        :raises MCAPIError:
        """
        self._download(f"/published/datasets/{dataset_id}/files/{file_id}/download", to)

    def search_published_data(self, search_str):
        """
        Search published datasets for matching string.

        :param str search_str: string to search on
        :return: List of matches
        :rtype: Searchable[]
        :raises MCAPIError:
        """
        form = {"search": search_str}
        return self._post("/published/data/search", form, decoder=decode_searchable_list)
