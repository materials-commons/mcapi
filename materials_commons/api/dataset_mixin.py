from .client_base import merge_dicts
from .decoder import (
    decode_dataset,
    decode_dataset_list,
    decode_file_list,
    decode_entity_list,
    decode_activity_list,
)
from .requests import CreateDatasetRequest, UpdateDatasetRequest


class DatasetMixin:
    def get_all_datasets(self, project_id, params=None):
        """
        Get all datasets in a project.

        :param int project_id: The project id
        :param params:
        :return: The list of datasets
        :rtype: Dataset[]
        :raises MCAPIError:
        """
        return self._get(f"/projects/{project_id}/datasets", params, decoder=decode_dataset_list)

    def create_dataset(self, project_id, name, attrs=None):
        """
        Create a new dataset in a project.

        :param int project_id: The project to create the dataset in
        :param str name: The name of the dataset
        :param CreateDatasetRequest attrs: Attributes of the dataset
        :return: The created dataset
        :rtype: Dataset
        :raises MCAPIError:
        """
        if not attrs:
            attrs = CreateDatasetRequest()
        form = merge_dicts({"name": name}, attrs.to_dict())
        return self._post(f"/projects/{project_id}/datasets", form, decoder=decode_dataset)

    def get_dataset(self, project_id, dataset_id, params=None):
        """
        Get dataset in a project.

        :param int project_id: The project id containing the dataset
        :param int dataset_id: The dataset id
        :param params:
        :return: The dataset
        :rtype: Dataset
        :raises MCAPIError:
        """
        return self._get(f"/projects/{project_id}/datasets/{dataset_id}", params, decoder=decode_dataset)

    def update_dataset(self, project_id, dataset_id, name, attrs=None):
        """
        Update an existing dataset.

        :param int project_id: The project containing the dataset
        :param int dataset_id: The id of the dataset
        :param str name: The name of the dataset
        :param UpdateDatasetRequest attrs: The attributes to update
        :return: The updated dataset
        :rtype: Dataset
        :raises MCAPIError:
        """
        if not attrs:
            attrs = UpdateDatasetRequest()
        form = merge_dicts({"name": name}, attrs.to_dict())
        return self._put(f"/projects/{project_id}/datasets/{dataset_id}", form, decoder=decode_dataset)

    def delete_dataset(self, project_id, dataset_id):
        """
        Delete an unpublished dataset.

        :param int project_id: The project id containing the dataset
        :param int dataset_id: The id of the dataset
        :raises MCAPIError:
        """
        self._delete(f"/projects/{project_id}/datasets/{dataset_id}")

    def get_dataset_files(self, project_id, dataset_id, params=None):
        """
        Get files for a dataset.

        :param int project_id: The project id containing the dataset
        :param int dataset_id: The dataset id
        :param params:
        :return: The files
        :rtype: File[]
        :raises MCAPIError:
        """
        return self._get(f"/projects/{project_id}/datasets/{dataset_id}/files", params, decoder=decode_file_list)

    def get_dataset_entities(self, project_id, dataset_id, params=None):
        """
        Get entities for a dataset.

        :param int project_id: The project id containing the dataset
        :param int dataset_id: The dataset id
        :param params:
        :return: The entities
        :rtype: Entity[]
        :raises MCAPIError:
        """
        return self._get(f"/projects/{project_id}/datasets/{dataset_id}/entities", params, decoder=decode_entity_list)

    def get_dataset_activities(self, project_id, dataset_id, params=None):
        """
        Get activities for a dataset.

        :param int project_id: The project id containing the dataset
        :param int dataset_id: The dataset id
        :param params:
        :return: The activities
        :rtype: Activity[]
        :raises MCAPIError:
        """
        return self._get(f"/projects/{project_id}/datasets/{dataset_id}/activities", params, decoder=decode_activity_list)

    def update_dataset_file_selection(self, project_id, dataset_id, file_selection):
        """
        Update the file selection for a dataset.

        :param int project_id: Project id containing dataset
        :param int dataset_id: Id of dataset
        :param dict file_selection: Keys: include_file, remove_include_file, exclude_file,
            remove_exclude_file, include_dir, remove_include_dir, exclude_dir, remove_exclude_dir
        :return: The updated dataset
        :rtype: Dataset
        :raises MCAPIError:
        """
        form = merge_dicts({"project_id": project_id}, file_selection)
        return self._put(f"/datasets/{dataset_id}/selection", form, decoder=decode_dataset)

    def change_dataset_file_selection(self, project_id, dataset_id, file_selection):
        """
        Change the file selection for a dataset to match the passed in selection.

        :param int project_id: Project id containing dataset
        :param int dataset_id: Id of dataset
        :param dict file_selection: Keys: include_files, exclude_files, include_dirs, exclude_dirs
        :return: The updated dataset
        :rtype: Dataset
        :raises MCAPIError:
        """
        return self._put(
            f"/projects/{project_id}/datasets/{dataset_id}/change_file_selection",
            file_selection, decoder=decode_dataset)

    def update_dataset_activities(self, project_id, dataset_id, activity_id):
        """
        Toggle whether an activity is in a dataset.

        :param int project_id: Project id containing dataset and activity
        :param int dataset_id: Id of dataset
        :param int activity_id: Id of activity
        :return: The updated dataset
        :rtype: Dataset
        :raises MCAPIError:
        """
        form = {"project_id": project_id, "activity_id": activity_id}
        return self._put(f"/datasets/{dataset_id}/activities/selection", form, decoder=decode_dataset)

    def update_dataset_entities(self, project_id, dataset_id, entity_id):
        """
        Toggle whether an entity is in a dataset.

        :param int project_id: Project id containing dataset and entity
        :param int dataset_id: Id of dataset
        :param int entity_id: Id of entity
        :return: The updated dataset
        :rtype: Dataset
        :raises MCAPIError:
        """
        form = {"project_id": project_id, "entity_id": entity_id}
        return self._put(f"/datasets/{dataset_id}/entities", form, decoder=decode_dataset)

    def update_dataset_workflows(self, project_id, dataset_id, workflow_id):
        """
        Toggle whether a workflow is in a dataset.

        :param int project_id: Project id containing dataset and workflow
        :param int dataset_id: Id of dataset
        :param int workflow_id: Id of workflow
        :return: The updated dataset
        :rtype: Dataset
        :raises MCAPIError:
        """
        form = {"project_id": project_id, "workflow_id": workflow_id}
        return self._put(f"/datasets/{dataset_id}/workflows", form, decoder=decode_dataset)

    def publish_dataset(self, project_id, dataset_id):
        """
        Publish a dataset.

        :param int project_id: The id of the project containing the dataset
        :param int dataset_id: The dataset id
        :return: The dataset
        :rtype: Dataset
        :raises MCAPIError:
        """
        form = {"project_id": project_id}
        return self._put(f"/datasets/{dataset_id}/publish", form, decoder=decode_dataset)

    def unpublish_dataset(self, project_id, dataset_id):
        """
        Unpublish a published dataset.

        :param int project_id: The id of the project containing the dataset
        :param int dataset_id: The dataset id
        :return: The dataset
        :rtype: Dataset
        :raises MCAPIError:
        """
        form = {"project_id": project_id}
        return self._put(f"/datasets/{dataset_id}/unpublish", form, decoder=decode_dataset)

    def assign_doi_to_dataset(self, project_id, dataset_id):
        """
        Assign DOI to existing dataset.

        :param int project_id: The project containing the dataset
        :param int dataset_id: The id of the dataset
        :return: The updated dataset with DOI
        :rtype: Dataset
        :raises MCAPIError:
        """
        return self._put(f"/projects/{project_id}/datasets/{dataset_id}/assign_doi", {}, decoder=decode_dataset)

    def check_file_in_dataset(self, project_id, dataset_id, file_id):
        """
        Check if file is in the dataset selection.

        :param int project_id: project dataset and file are in
        :param int dataset_id: dataset to check file_selection against
        :param int file_id: file to check
        :return: {'in_dataset': True} or {'in_dataset': False}
        :raises MCAPIError:
        """
        return self._get(f"/projects/{project_id}/datasets/{dataset_id}/files/{file_id}/check_selection")

    def check_file_by_path_in_dataset(self, project_id, dataset_id, file_path):
        """
        Check if file path is in the dataset selection.

        :param int project_id: project dataset and file_path are in
        :param int dataset_id: dataset to check file_selection against
        :param str file_path: file_path to check against dataset file_selection
        :return: {'in_dataset': True} or {'in_dataset': False}
        :raises MCAPIError:
        """
        form = {"file_path": file_path.replace('\\', '/')}
        return self._post(f"/projects/{project_id}/datasets/{dataset_id}/check_select_by_path", form)

    def import_dataset(self, dataset_id, project_id, directory_name):
        """
        Launches a job to import a dataset into a project.

        :param int dataset_id: The dataset id to import
        :param int project_id: A project id the user has access to
        :param str directory_name: The top level directory to import the dataset into
        :raises MCAPIError:
        """
        form = {"directory": directory_name}
        self._post(f"/projects/{project_id}/datasets/{dataset_id}/import", form)
