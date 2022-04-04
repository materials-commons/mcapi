from collections import OrderedDict
import requests
import time
import logging
from .models import Project, Experiment, Dataset, Entity, Activity, Workflow, User, File, GlobusUpload, \
    GlobusDownload, Server, Community, Tag, Searchable, GlobusTransfer
from .query_params import QueryParams
from .requests import *

try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client

try:
    import urllib3

    urllib3.disable_warnings()
except ImportError:
    pass


class MCAPIError(Exception):
    def __init__(self, message, response):
        super(MCAPIError, self).__init__(message)
        self.response = response


def merge_dicts(dict1, dict2):
    merged = dict1.copy()
    merged.update(dict2)
    return merged


class Client(object):

    def __init__(self, apikey, base_url="https://materialscommons.org/api", raise_exception=True):
        self.apikey = apikey
        self.base_url = base_url
        self.log = False
        self.raise_exception = raise_exception
        self.headers = {
            "Authorization": "Bearer " + self.apikey,
            "Accept": "application/json"
        }
        self.rate_limit = 0
        self.rate_limit_remaining = 0
        self.rate_limit_reset = None
        self.retry_after = None
        self.r = None
        self._throttle_s = 0.0

    @staticmethod
    def get_apikey(email, password, base_url="https://materialscommons.org/api"):
        url = base_url + "/get_apitoken"
        form = {"email": email, "password": password}
        r = requests.post(url, json=form, verify=False)
        r.raise_for_status()
        return r.json()["data"]["api_token"]

    @staticmethod
    def login(email, password, base_url="https://materialscommons.org/api"):
        apikey = Client.get_apikey(email, password, base_url)
        return Client(apikey, base_url)

    @staticmethod
    def set_debug_on():
        http_client.HTTPConnection.debuglevel = 1
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    @staticmethod
    def set_debug_off():
        http_client.HTTPConnection.debuglevel = 0
        logging.disable()
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.disabled = True
        requests_log.propagate = False

    # Server
    def get_server_info(self):
        """
        Gets information about the materials commons server
        :return: server information
        :rtype Server
        """
        return Server(self.get("/server/info"))

    # Projects
    def get_all_projects(self, params=None):
        """
        Returns a list of all the projects a user has access to
        :param params:
        :return: List of projects
        :rtype Project[]
        :raises MCAPIError
        """
        return Project.from_list(self.get("/projects", params))

    def create_project(self, name, attrs=None):
        """
        Creates a new project for the authenticated user. Project name must be unique
        :param str name: Name of project
        :param CreateProjectRequest attrs: (optional) Additional attributes for the create request
        :return: The created project
        :rtype Project
        :raises MCAPIError
        """
        if not attrs:
            attrs = CreateProjectRequest()
        form = merge_dicts({"name": name}, attrs.to_dict())
        return Project(self.post("/projects", form))

    def get_project(self, project_id, params=None):
        """
        Get a project by its id
        :param int project_id: Project id for project
        :param params:
        :return: The project
        :rtype Project
        :raises MCAPIError
        """
        return Project(self.get("/projects/" + str(project_id), params))

    def delete_project(self, project_id):
        """
        Deletes a project
        :param int project_id: id of project to delete
        :raises MCAPIError
        """
        self.delete("/projects/" + str(project_id))

    def update_project(self, project_id, attrs):
        """
        Updates the given project
        :param int project_id: Id of project to update
        :param UpdateProjectRequest attrs: The attributes to update on the project
        :return: The updated project
        :rtype Project
        :raises MCAPIError
        """
        return Project(self.put("/projects/" + str(project_id), attrs.to_dict()))

    def add_user_to_project(self, project_id, user_id):
        """
        Adds user to project
        :param int project_id: Id of project to add user to
        :param int user_id: Id of user to add to project
        :return: The updated project
        :rtype Project
        :raises MCAPIError
        """
        return Project(self.put("/projects/" + str(project_id) + "/add-user/" + str(user_id), {}))

    def remove_user_from_project(self, project_id, user_id):
        """
        Remove user from project
        :param int project_id: Id of project to add user to
        :param int user_id: Id of user to add to project
        :return: The updated project
        :rtype Project
        :raises MCAPIError
        """
        return Project(self.put("/projects/" + str(project_id) + "/remove-user/" + str(user_id), {}))

    def add_admin_to_project(self, project_id, user_id):
        """
        Adds user as an admin to project
        :param int project_id: Id of project to add user to
        :param int user_id: Id of user to add to project
        :return: The updated project
        :rtype Project
        :raises MCAPIError
        """
        return Project(self.put("/projects/" + str(project_id) + "/add-admin/" + str(user_id), {}))

    def remove_admin_from_project(self, project_id, user_id):
        """
        Removes admin user from project
        :param int project_id: Id of project to add user to
        :param int user_id: Id of user to remove from project
        :return: The updated project
        :rtype Project
        :raises MCAPIError
        """
        return Project(self.put("/projects/" + str(project_id) + "/remove-admin/" + str(user_id), {}))

    # Experiments
    def get_all_experiments(self, project_id, params=None):
        """
        Get all experiments for a given project
        :param int project_id: The project id
        :param params:
        :return: A list of experiments
        :rtype Experiment[]
        :raises MCAPIError
        """
        return Experiment.from_list(self.get("/projects/" + str(project_id) + "/experiments", params))

    def get_experiment(self, experiment_id, params=None):
        """
        Get an experiment
        :param int experiment_id: The experiment id
        :param params:
        :return: The experiment
        :rtype Experiment
        :raises MCAPIError
        """
        return Experiment(self.get("/experiments/" + str(experiment_id), params))

    def update_experiment(self, experiment_id, attrs):
        """
        Update attributes of an experiment
        :param int experiment_id: The experiment id
        :param UpdateExperimentRequest attrs: Attributes to update
        :return: The updated experiment
        :rtype Experiment
        :raises MCAPIError
        """
        form = merge_dicts({"experiment_id": experiment_id}, attrs.to_dict())
        return Experiment(self.put("/experiments/" + str(experiment_id), form))

    def delete_experiment(self, project_id, experiment_id):
        """
        Delete experiment in project
        :param int project_id: The id of the project the experiment is in
        :param experiment_id: The experiment id
        :raises MCAPIError
        """
        self.delete("/projects/" + str(project_id) + "/experiments/" + str(experiment_id))

    def create_experiment(self, project_id, name, attrs=None):
        """
        Create a new experiment in a project
        :param int project_id: The id of the project the experiment is in
        :param str name: Name of experiment
        :param CreateExperimentRequest attrs: Additional attributes on the experiment
        :return: The created experiment
        :rtype Experiment
        :raises MCAPIError
        """
        if not attrs:
            attrs = CreateExperimentRequest()
        form = merge_dicts({"project_id": project_id, "name": name}, attrs.to_dict())
        return Experiment(self.post("/experiments", form))

    def update_experiment_workflows(self, project_id, experiment_id, workflow_id):
        """
        Toggle whether an workflow is in the experiment
        :param int project_id: Id of project containing the experiment and workflow
        :param experiment_id: Id of experiment
        :param workflow_id: Id of workflow
        :return: The updated experiment
        :rtype Experiment
        :raises MCAPIError
        """
        form = {"project_id": project_id, "workflow_id": workflow_id}
        return Experiment(self.put("/experiments/" + str(experiment_id) + "/workflows/selection", form))

    # Directories
    def get_directory(self, project_id, directory_id, params=None):
        """
        Get a directory in the project
        :param int project_id: The id of the project the directory is in
        :param int directory_id: The directory id
        :param params:
        :return: The directory
        :rtype File
        :raises MCAPIError
        """
        return File(self.get("/projects/" + str(project_id) + "/directories/" + str(directory_id), params))

    def list_directory(self, project_id, directory_id, params=None):
        """
        Return a list of all the files and directories in a given directory
        :param int project_id: The id of the project the directory is in
        :param int directory_id: The directory id
        :param params:
        :return: A list of the files and directories in the given directory
        :rtype File[]
        :raises MCAPIError
        """
        return File.from_list(
            self.get("/projects/" + str(project_id) + "/directories/" + str(directory_id) + "/list", params))

    def list_directory_by_path(self, project_id, path, params=None):
        """
        Return a list of all the files and directories at given path
        :param int project_id: The id of the project the path is in
        :param str path:
        :param params:
        :return: A list of the files and directories in the given path
        :rtype File[]
        :raises MCAPIError
        """
        path_param = {"path": path.replace('\\', '/')}
        return File.from_list(self.get("/projects/" + str(project_id) + "/directories_by_path", params, path_param))

    def create_directory(self, project_id, name, parent_id, attrs=None):
        """
        Create a new directory in project in the given directory
        :param int project_id: The id of the project the directory will be created in
        :param str name: Name of directory
        :param int parent_id: Parent directory id - The directory that this directory will be in
        :param CreateDirectoryRequest attrs: Additional attributes on the directory
        :return: The created directory
        :rtype File
        :raises MCAPIError
        """
        if not attrs:
            attrs = CreateDirectoryRequest()
        form = {"name": name, "directory_id": parent_id, "project_id": project_id}
        form = merge_dicts(form, attrs.to_dict())
        return File(self.post("/directories", form))

    def move_directory(self, project_id, directory_id, to_directory_id):
        """
        Moves a directory into another directory
        :param int project_id: The project id that target and destination directories are in
        :param int directory_id: Id of directory to move
        :param int to_directory_id: Id of the destination directory
        :return: The directory that was moved
        :rtype File
        :raises MCAPIError
        """
        form = {"to_directory_id": to_directory_id, "project_id": project_id}
        return File(self.post("/directories/" + str(directory_id) + "/move", form))

    def rename_directory(self, project_id, directory_id, name):
        """
        Rename a given directory
        :param int project_id: The project id that the directory is in
        :param int directory_id: The id of the directory being renamed
        :param name: The new name of the directory
        :return: The directory that was renamed
        :rtype File
        :raises MCAPIError
        """
        form = {"name": name, "project_id": project_id}
        return File(self.post("/directories/" + str(directory_id) + "/rename", form))

    def delete_directory(self, project_id, directory_id):
        """
        Should not be used yet: Delete a directory only if the directory is empty
        :param int project_id: The project id containing the directory to delete
        :param int directory_id: The id of the directory to delete
        :raises MCAPIError
        """
        self.delete("/projects/" + str(project_id) + "/directories/" + str(directory_id))

    def update_directory(self, project_id, directory_id, attrs):
        """
        Update attributes on a directory
        :param int project_id: The project id containing the directory
        :param int directory_id: The id of the directory to update
        :param attrs: Attributes to update
        :return: The updated directory
        :rtype File
        :raises MCAPIError
        """
        form = merge_dicts({"project_id": project_id}, attrs.to_dict())
        return File(self.put("/directories/" + str(directory_id), form))

    # Files
    def get_file(self, project_id, file_id, params=None):
        """
        Get file in project
        :param int project_id: The id of the project containing the file
        :param int file_id: The id of the file
        :param params:
        :return: The file
        :rtype File
        :raises MCAPIError
        """
        return File(self.get("/projects/" + str(project_id) + "/files/" + str(file_id), params))

    def get_file_versions(self, project_id, file_id, params=None):
        """
        Get versions for file in project (does not include file given)
        :param int project_id: The id of the project containing the file
        :param int file_id: The id of the file
        :param params:
        :return: File versions
        :rtype File[]
        :raises MCAPIError
        """
        return File.from_list(self.get("/projects/" + str(project_id) + "/files/" + str(file_id) + "/versions", params))

    def set_as_active_file(self, project_id, file_id):
        """
        Set file as active version, changing current active file version to inactive
        :param int project_id: The id of the project containing the file
        :param int file_id: The id of the file
        :return: File
        :rtype File
        :raises MCAPIError
        """
        return File(self.put("/projects/" + str(project_id) + "/files/" + str(file_id) + "/make_active", {}))

    def get_file_by_path(self, project_id, file_path):
        """
        Get file by path in project
        :param int project_id: The id of the project containing the file
        :param file_path: The path to the file
        :return: The file
        :rtype File
        :raises MCAPIError
        """
        form = {"path": file_path.replace('\\', '/'), "project_id": project_id}
        return File(self.post("/files/by_path", form))

    def update_file(self, project_id, file_id, attrs):
        """
        Update attributes of a file
        :param project_id:
        :param file_id:
        :param UpdateFileRequest attrs: Attributes to update
        :return: The updated file
        :rtype File
        :raises MCAPIError
        """
        form = merge_dicts({"project_id", project_id}, attrs.to_dict())
        return File(self.put("/files/" + str(file_id), form))

    def delete_file(self, project_id, file_id, force=False):
        """
        Delete a file in a project
        :param int project_id: The id of the project containing the file
        :param int file_id: The id of the file to delete
        :raises MCAPIError
        """
        params = None
        if force:
            params = {"force": True}
        self.delete("/projects/" + str(project_id) + "/files/" + str(file_id), params=params)

    def move_file(self, project_id, file_id, to_directory_id):
        """
        Move file into a different directory
        :param int project_id: The project id of the file and the destination directory
        :param int file_id: The id of the file to move
        :param int to_directory_id: The id of the destination directory
        :return: The moved file
        :rtype File
        :raises MCAPIError
        """
        form = {"directory_id": to_directory_id, "project_id": project_id}
        return File(self.post("/files/" + str(file_id) + "/move", form))

    def rename_file(self, project_id, file_id, name):
        """
        Rename a file
        :param int project_id: The project id of the file to rename
        :param int file_id: The id of the file to rename
        :param str name: The files new name
        :return: The rename file
        :rtype File
        :raises MCAPIError
        """
        form = {"name": name, "project_id": project_id}
        return File(self.post("/files/" + str(file_id) + "/rename", form))

    def download_file(self, project_id, file_id, to):
        """
        Download a file
        :param int project_id: The project id containing the file to download
        :param int file_id: The id of the file to download
        :param str to: path including file name to download file to
        :raises MCAPIError
        """
        self.download("/projects/" + str(project_id) + "/files/" + str(file_id) + "/download", to)

    def download_file_by_path(self, project_id, path, to):
        """
        Download a file by path
        :param int project_id: The project id containing the file to download
        :param str path: The path in the project of the file
        :param str to: path including file name to download file to
        :raises MCAPIError
        """
        file = self.get_file_by_path(project_id, path.replace('\\', '/'))
        self.download_file(project_id, file.id, to)

    def upload_file(self, project_id, directory_id, file_path):
        """
        Uploads a file to a project
        :param int project_id: The project to upload file to
        :param int directory_id: The directory in the project to upload the file into
        :param str file_path: path of file to upload
        :return: The created file
        :rtype File
        :raises MCAPIError
        """
        files = File.from_list(
            self.upload("/projects/" + str(project_id) + "/files/" + str(directory_id) + "/upload", file_path))
        return files[0]

    def upload_bytes(self, project_id, directory_id, name, f):
        files = File.from_list(
            self.upload_raw("/projects/" + str(project_id) + "/files/" + str(directory_id) + "/upload/" + str(name), f))
        return files[0]

    # Entities
    def get_all_entities(self, project_id, params=None):
        """
        Get all entities in a project
        :param int project_id: The id of the project
        :param params:
        :return: The list of entities
        :rtype Entity[]
        :raises MCAPIError
        """
        return Entity.from_list(self.get("/projects/" + str(project_id) + "/entities", params))

    def get_entity(self, project_id, entity_id, params=None):
        """
        Get an entity
        :param int project_id: The id of the project containing the entity
        :param int entity_id: The id of the entity
        :param params:
        :return: The entity
        :rtype Entity
        :raises MCAPIError
        """
        return Entity(self.get("/projects/" + str(project_id) + "/entities/" + str(entity_id), params))

    def create_entity(self, project_id, name, activity_id, request=None, attrs=None):
        """
        Creates a new entity in the project
        :param project_id: The id of the project to create entity in
        :param str name: The entity name
        :param activity_id: The activity to associated the samples as initially coming from
        :param CreateEntityRequest request: Attributes of the entity
        :param attrs: Array of dicts of the form {"name": "", "unit": "", value: dict | bool | int | float | str}
        :return: The created entity
        :rtype Entity
        :raises MCAPIError
        """
        if not request:
            request = CreateEntityRequest()
        if not attrs:
            attrs = []
        form = merge_dicts({
            "name": name,
            "project_id": project_id,
            "attributes": attrs,
            "activity_id": activity_id,
        }, request.to_dict())
        return Entity(self.post("/entities", form))

    def delete_entity(self, project_id, entity_id):
        """
        Delete an entity
        :param int project_id: The id of the project containing the entity
        :param int entity_id: The entity id
        :raises MCAPIError
        """
        self.delete("/projects/" + str(project_id) + "/entities/" + str(entity_id))

    def create_entity_state(self, project_id, entity_id, activity_id, current=True, attrs=None):
        """
        Adds a new state to an existing entity.
        :param int project_id: The id of the project containing the entity
        :param int entity_id: The id of the entity to associate the state with
        :param in activity_id: The id of the activity that created the state
        :param bool current: Whether to mark the state as the current state
        :param attrs: Array of dicts of the form {"name": "", "unit": "", value: dict | bool | int | float | str}
        :return: Entity
        :raises MCAPIError
        """
        if not attrs:
            attrs = []
        form = {"current": current, "attributes": attrs}
        return Entity(self.post("/projects/" + str(project_id) + "/entities/" + str(entity_id) + "/activities/" + str(
            activity_id) + "/create-entity-state", form))

    # Activities
    def get_all_activities(self, project_id, params=None):
        """
        Get all activities in a project
        :param int project_id: The id of the project
        :param params:
        :return: List of activities
        :rtype Activity[]
        :raises MCAPIError
        """
        return Activity.from_list(self.get("/projects/" + str(project_id) + "/activities", params))

    def get_activity(self, project_id, activity_id, params=None):
        """
        Get an activity
        :param int project_id: The id of the project containing the activity
        :param int activity_id: The id of the activity
        :param params:
        :return: The activity
        :rtype Activity
        :raises MCAPIError
        """
        return Activity(self.get("/projects/" + str(project_id) + "/activies/" + str(activity_id), params))

    def create_activity(self, project_id, name, request=None, attrs=None):
        """
        Create a new activity in the project
        :param project_id: The project to create the activity int
        :param str name: Name of activity
        :param CreateActivityRequest request: Attributes on the activity
        :param attrs: Array of dicts of the form {"name": "", "unit": "", value: dict | bool | int | float | str}
        :return: The activity to create
        :rtype Activity
        :raises MCAPIError
        """
        if not request:
            request = CreateActivityRequest()
        if not attrs:
            attrs = []
        form = merge_dicts({"project_id": project_id, "name": name, "attributes": attrs}, request.to_dict())
        return Activity(self.post("/activies", form))

    def delete_activity(self, project_id, activity_id):
        """
        Deletes an activity
        :param project_id: The id of the project containing the activity
        :param activity_id: The id of the activity to delete
        :raises MCAPIError
        """
        self.delete("/projects/" + str(project_id) + "/activies/" + str(activity_id))

    # Datasets
    def get_all_datasets(self, project_id, params=None):
        """
        Get all datasets in a project
        :param int project_id: The project id
        :param params:
        :return: The list of datasets
        :rtype Dataset[]
        :raises MCAPIError
        """
        return Dataset.from_list(self.get("/projects/" + str(project_id) + "/datasets", params))

    def get_all_published_datasets(self, params=None):
        """
        Get all published datasets
        :param params:
        :return: The list of published datasets
        :rtype Dataset[]
        :raises MCAPIError
        """
        return Dataset.from_list(self.get("/published/datasets", params))

    def get_published_dataset(self, dataset_id, params=None):
        """
        Get published dataset
        :param int dataset_id: The dataset id
        :param params:
        :return: The dataset
        :rtype Dataset
        :raises MCAPIError
        """
        return Dataset(self.get("/published/datasets/" + str(dataset_id), params))

    def get_published_dataset_files(self, dataset_id, params=None):
        """
        Get files for a published dataset
        :param int dataset_id: The dataset id
        :param params:
        :rtype: File[]
        :return: The files
        :raises MCAPIError
        """
        return File.from_list(
            self.get("/published/datasets/" + str(dataset_id) + "/files", params))

    def get_published_dataset_directory(self, dataset_id, directory_id, params=None):
        """
        Get a directory in a published dataset
        :param int dataset_id: The id of the published dataset the directory is in
        :param int directory_id: The directory id
        :param params:
        :return: The directory
        :rtype File
        :raises MCAPIError
        """
        return File(self.get("/published/datasets/" + str(dataset_id) + "/directories/" + str(directory_id), params))

    def list_published_dataset_directory(self, dataset_id, directory_id, params=None):
        """
        Return a list of all the files and directories in a given published dataset directory
        :param int dataset_id: The id of the dataset the directory is in
        :param int directory_id: The directory id
        :param params:
        :return: A list of the files and directories in the given directory
        :rtype File[]
        :raises MCAPIError
        """
        return File.from_list(
            self.get("/published/datasets/" + str(dataset_id) + "/directories/" + str(directory_id) + "/list", params))

    def list_published_dataset_directory_by_path(self, dataset_id, path, params=None):
        """
        Return a list of all the files and directories at given path
        :param int dataset_id: The id of the dataset the path is in
        :param str path:
        :param params:
        :return: A list of the files and directories in the given path
        :rtype File[]
        :raises MCAPIError
        """
        path_param = {"path": path.replace('\\', '/')}
        return File.from_list(self.get("/published/datasets/" + str(dataset_id) + "/directories_by_path", params, path_param))

    def get_published_dataset_entities(self, dataset_id, params=None):
        """
        Get entities for a published dataset
        :param int dataset_id: The dataset id
        :param params:
        :rtype: Entity[]
        :return: The entities
        :raises MCAPIError
        """
        return Entity.from_list(
            self.get("/published/datasets/" + str(dataset_id) + "/entities", params))

    def get_published_dataset_activities(self, dataset_id, params=None):
        """
        Get activities for a published dataset
        :param int dataset_id: The dataset id
        :param params:
        :rtype: Activity[]
        :return: The activities
        :raises MCAPIError
        """
        return Activity.from_list(
            self.get("/published/datasets/" + str(dataset_id) + "/activities", params))

    def search_published_data(self, search_str):
        """
        Search published datasets for matching string
        :param str search_str: string to search on
        :return: List of matches
        :rtype: Searchable[]
        :raises MCAPIError
        """
        form = {"search": search_str}
        return Searchable.from_list(self.post("/published/data/search", form))

    def import_dataset(self, dataset_id, project_id, directory_name):
        """
        Launches a job to import a dataset into a project. The import will complete at some
        point in the future. There isn't currently a way to query the import status.
        :param int dataset_id: The dataset id to import
        :param int project_id: A project id the user has access to
        :param string directory_name: The top level directory to import the dataset into (will be created)
        :raises MCAPIError
        """
        form = {"directory": directory_name}
        self.post("/projects/" + str(project_id) + "/datasets/" + str(dataset_id) + "/import", form)

    def get_dataset(self, project_id, dataset_id, params=None):
        """
        Get dataset in a project
        :param int project_id: The project id containing the dataset
        :param int dataset_id: The dataset id
        :param params:
        :return: The dataset
        :rtype Dataset
        :raises MCAPIError
        """
        return Dataset(self.get("/projects/" + str(project_id) + "/datasets/" + str(dataset_id), params))

    def get_dataset_files(self, project_id, dataset_id, params=None):
        """
        Get files for a dataset
        :param int project_id: The project id containing the dataset
        :param int dataset_id: The dataset id
        :param params:
        :rtype: File[]
        :return: The files
        :raises MCAPIError
        """
        return File.from_list(
            self.get("/projects/" + str(project_id) + "/datasets/" + str(dataset_id) + "/files", params))

    def get_dataset_entities(self, project_id, dataset_id, params=None):
        """
        Get entities for a dataset
        :param int project_id: The project id containing the dataset
        :param int dataset_id: The dataset id
        :param params:
        :rtype: Entity[]
        :return: The entities
        :raises MCAPIError
        """
        return Entity.from_list(
            self.get("/projects/" + str(project_id) + "/datasets/" + str(dataset_id) + "/entities", params))

    def get_dataset_activities(self, project_id, dataset_id, params=None):
        """
        Get activities for a dataset
        :param int project_id: The project id containing the dataset
        :param int dataset_id: The dataset id
        :param params:
        :rtype: Activity[]
        :return: The activities
        :raises MCAPIError
        """
        return Activity.from_list(
            self.get("/projects/" + str(project_id) + "/datasets/" + str(dataset_id) + "/activities", params))

    def delete_dataset(self, project_id, dataset_id):
        """
        Delete an unpublished dataset
        :param int project_id: The project id containing the dataset
        :param int dataset_id: The id of the dataset
        :raises MCAPIError
        """
        self.delete("/projects/" + str(project_id) + "/datasets/" + str(dataset_id))

    def update_dataset_file_selection(self, project_id, dataset_id, file_selection):
        """
        Update the file selection for a dataset
        :param int project_id: Project id containing dataset
        :param int dataset_id: Id of dataset
        :param file_selection: {
            "include_file": str,
            "remove_include_file": str,
            "exclude_file": str,
            "remove_exclude_file": str,
            "include_dir": str,
            "remove_include_dir": str,
            "exclude_dir": str,
            "remove_exclude_dir": str
        }
        :return: The updated dataset
        :rtype Dataset
        :raises MCAPIError
        """
        form = {"project_id": project_id}
        form = merge_dicts(form, file_selection)
        return Dataset(self.put("/datasets/" + str(dataset_id) + "/selection", form))

    def change_dataset_file_selection(self, project_id, dataset_id, file_selection):
        """
        Change the file selection for a dataset to match the passed in dataset
        :param int project_id: Project id containing dataset
        :param int dataset_id: Id of dataset
        :param file_selection: {
            "include_files": array,
            "exclude_files": array,
            "include_dirs": array,
            "exclude_dirs": array,
        }
        :return: The updated dataset
        :rtype Dataset
        :raises MCAPIError
        :param project_id:
        :param dataset_id:
        :param file_selection:
        :return:
        """
        return Dataset(
            self.put("/projects/" + str(project_id) + "/datasets/" + str(dataset_id) + "/change_file_selection",
                     file_selection))

    def update_dataset_activities(self, project_id, dataset_id, activity_id):
        """
        Toggle whether an activity is in a dataset
        :param int project_id: Project id containing dataset and activity
        :param int dataset_id: Id of dataset
        :param int activity_id: Id of activity
        :return: The updated dataset
        :rtype Dataset
        :raises MCAPIError
        """
        form = {"project_id": project_id, "activity_id": activity_id}
        return Dataset(self.put("/datasets/" + str(dataset_id) + "/activities/selection", form))

    def update_dataset_entities(self, project_id, dataset_id, entity_id):
        """
        Toggle whether an entity is in a dataset
        :param int project_id: Project id containing dataset and entity
        :param int dataset_id: Id of dataset
        :param int entity_id: Id of entity
        :return: The updated dataset
        :rtype Dataset
        :raises MCAPIError
        """
        form = {"project_id": project_id, "entity_id": entity_id}
        return Dataset(self.put("/datasets/" + str(dataset_id) + "/entities", form))

    def update_dataset_workflows(self, project_id, dataset_id, workflow_id):
        """
        Toggle whether an workflow is in a dataset
        :param int project_id: Project id containing dataset and workflow
        :param int dataset_id: Id of dataset
        :param int workflow_id: Id of workflow
        :return: The updated dataset
        :rtype Dataset
        :raises MCAPIError
        """
        form = {"project_id": project_id, "workflow_id": workflow_id}
        return Dataset(self.put("/datasets/" + str(dataset_id) + "/workflows", form))

    def publish_dataset(self, project_id, dataset_id):
        """
        Publish a dataset
        :param int project_id: The id of the project containing the dataset
        :param int dataset_id: The dataset id
        :return: The dataset
        :rtype Dataset
        :raises MCAPIError
        """
        form = {"project_id": project_id}
        return Dataset(self.put("/datasets/" + str(dataset_id) + "/publish", form))

    def unpublish_dataset(self, project_id, dataset_id):
        """
        Unpublish an published dataset
        :param int project_id: The id of the project containing the dataset
        :param int dataset_id: The dataset id
        :return: The dataset
        :rtype Dataset
        :raises MCAPIError
        """
        form = {"project_id": project_id}
        return Dataset(self.put("/datasets/" + str(dataset_id) + "/unpublish", form))

    def create_dataset(self, project_id, name, attrs=None):
        """
        Create a new dataset in a project
        :param int project_id: The project to create the dataset in
        :param string name: The name of the dataset
        :param CreateDatasetRequest attrs: Attributes of the dataset
        :return: The created dataset
        :rtype Dataset
        :raises MCAPIError
        """
        if not attrs:
            attrs = CreateDatasetRequest()
        form = merge_dicts({"name": name}, attrs.to_dict())
        return Dataset(self.post("/projects/" + str(project_id) + "/datasets", form))

    def update_dataset(self, project_id, dataset_id, name, attrs=None):
        """
        Update an existing dataset
        :param int project_id: The project to create the dataset in
        :param int dataset_id: The id of the dataset
        :param str name: The name of the dataset (doesn't need to be different)
        :param UpdateDatasetRequest attrs: The attributes to update
        :return: The updated dataset
        :rtype Dataset
        :raises MCAPIError
        """
        if not attrs:
            attrs = UpdateDatasetRequest()
        form = merge_dicts({"name": name}, attrs.to_dict())
        return Dataset(self.put("/projects/" + str(project_id) + "/datasets/" + str(dataset_id), form))

    def assign_doi_to_dataset(self, project_id, dataset_id):
        """
        Assign DOI to existing dataset
        :param int project_id: The project to create the dataset in
        :param int dataset_id: The id of the dataset
        :return: The updated dataset with DOI
        :rtype Dataset
        :raises MCAPIError
        """
        return Dataset(self.put("/projects/" + str(project_id) + "/datasets/" + str(dataset_id) + "/assign_doi", {}))

    def download_published_dataset_zipfile(self, dataset_id, to):
        """
        Download the zipfile for a published dataset
        :param int dataset_id: The id of the published dataset
        :param str to: The path including the file name to write the download to
        :raises MCAPIError
        """
        self.download("/published/datasets/" + str(dataset_id) + "/download_zipfile", to)

    def download_published_dataset_file(self, dataset_id, file_id, to):
        """
        Download file from a published dataset
        :param int dataset_id: The id of the published dataset
        :param int file_id: The id of the file in the dataset
        :param str to: The path including the file name to write the download to
        :raises MCAPIError
        """
        self.download("/published/datasets/" + str(dataset_id) + "/files/" + str(file_id) + "/download", to)

    def check_file_in_dataset(self, project_id, dataset_id, file_id):
        """
        Check if file is in the dataset selection
        :param int project_id: project dataset and file are in
        :param int dataset_id: dataset to check file_selection against
        :param int file_id: file to check
        :return: {'in_dataset': True} or {'in_dataset': False}
        :raises MCAPIError
        """
        return self.get("/projects/" + str(project_id) + "/datasets/" + str(dataset_id) + "/files/" + str(
            file_id) + "/check_selection")

    def check_file_by_path_in_dataset(self, project_id, dataset_id, file_path):
        """
        Check if file path is in the dataset selection. Throws an error if the file_path isn't in the project.
        :param int project_id: project dataset and file_path are in
        :param int dataset_id: data to check file_selection against
        :param str file_path: file_path to check against dataset file_selection
        :return: {'in_dataset': True} or {'in_dataset': False}
        :exception if file_path doesn't exist in project
        :raises MCAPIError
        """
        form = {"file_path": file_path.replace('\\', '/')}
        return self.post("/projects/" + str(project_id) + "/datasets/" + str(dataset_id) + "/check_select_by_path",
                         form)

    # Globus
    def create_globus_upload_request(self, project_id, name):
        """
        Create a new globus request in the given project
        :param int project_id: The project id for the upload
        :param name: The name of the request
        :return: The globus request
        :rtype GlobusUpload
        :raises MCAPIError
        """
        form = {"project_id": project_id, "name": name}
        return GlobusUpload(self.post("/globus/uploads", form))

    def delete_globus_upload_request(self, project_id, globus_upload_id):
        """
        Delete an existing globus upload request
        :param int project_id:
        :param int globus_upload_id:
        :raises MCAPIError
        """
        self.delete("/projects/" + str(project_id) + "/globus/" + str(globus_upload_id) + "/uploads")

    def finish_globus_upload_request(self, project_id, globus_upload_id):
        """
        Mark a globus upload request as finished
        :param int project_id: The project id for the upload
        :param int globus_upload_id: The id of the globus upload
        :return: The globus upload
        :rtype GlobusUpload
        :raises MCAPIError
        """
        form = {"project_id": project_id}
        return GlobusUpload(self.put("/globus/" + str(globus_upload_id) + "/uploads/complete", form))

    def get_all_globus_upload_requests(self, project_id, params=None):
        """
        Get all globus uploads in a project
        :param int project_id: The project id
        :return: List of globus uploads
        :rtype GlobusUpload[]
        :raises MCAPIError
        """
        return GlobusUpload.from_list(self.get("/projects/" + str(project_id) + "/globus/uploads", params))

    def create_globus_download_request(self, project_id, name):
        """
        Create a globus download request for a project
        :param int project_id:
        :param str name: The name of the download request
        :return: The globus download
        :rtype GlobusDownload
        :raises MCAPIError
        """
        form = {"project_id": project_id, "name": name}
        return GlobusDownload(self.post("/globus/downloads", form))

    def delete_globus_download_request(self, project_id, globus_download_id):
        """
        Delete an existing globus download request
        :param int project_id: The id of the project containing the download request
        :param int globus_download_id: The id of the globus download to delete
        :raises MCAPIError
        """
        self.delete("/projects/" + str(project_id) + "/globus/" + str(globus_download_id) + "/downloads")

    def get_all_globus_download_requests(self, project_id, params=None):
        """
        Get all globus download requests for a project
        :param int project_id: The project
        :return: List of all globus downloads
        :rtype GlobusDownload[]
        :raises MCAPIError
        """
        return GlobusDownload.from_list(self.get("/projects/" + str(project_id) + "/globus/downloads", params))

    def get_globus_download_request(self, project_id, globus_download_id, params=None):
        """
        Get a globus download
        :param int project_id: The id of the project containing the globus download
        :param int globus_download_id: The globus download id
        :return: The globus download
        :rtype GlobusDownload
        :raises MCAPIError
        """
        return GlobusDownload(
            self.get("/projects/" + str(project_id) + "/globus/downloads/" + str(globus_download_id), params))

    def open_globus_transfer(self, project_id, params=None):
        """
        Open a globus transfer request for current user in project. If one is already
        active then it returns the already active request.
        :param int project_id: The id of the project associated with this globus transfer
        :return: The globus transfer
        :rtype GlobusTransfer
        :raises MCAPIError
        """
        return GlobusTransfer(self.get("/projects/" + str(project_id) + "/globus/open", params))

    def close_globus_transfer(self, project_id):
        """
        Closes an existing globus transfer. If there isn't an open transfer for the user in project then
        does nothing and returns success
        :param int project_id: The id of the project to close globus transfer for the current user
        :return: None
        :raises MCAPIError
        """
        self.get_no_value("/projects/" + str(project_id) + "/globus/close")

    # Users
    def get_user_by_email(self, email, params=None):
        """
        Get a user by their email
        :param string email: email address of user to lookup
        :return: The user
        :rtype User
        :raises MCAPIError
        """
        return User(self.get("/users/by-email/" + email, params))

    def list_users(self, params=None):
        """
        List users of Materials Commons
        :return: List of users
        :rtype User[]
        :raises MCAPIError
        """
        return User.from_list(self.get("/users", params))

    # Communities
    def create_community(self, name, attrs={}):
        """
        Creates a new community owned by the user.
        :param str name: Name of community
        :param CreateCommunityRequest attrs: (optional) Additional attributes for the create request
        :return: The created community
        :rtype Community
        :raises MCAPIError
        """
        if not attrs:
            attrs = CreateCommunityRequest()
        form = merge_dicts({"name": name}, attrs.to_dict())
        return Community(self.post("/communities", form))

    def get_all_public_communities(self, params=None):
        """
        Get all public communities
        :rtype Community[]
        :return: List of public communities
        :raises MCAPIError
        """
        return Community.from_list(self.get('/communities/public', params))

    def get_all_my_communities(self, params=None):
        """
        Get all communities owned by user
        :rtype Community[]
        :return: List of communities
        :raises MCAPIError
        """
        return Community.from_list(self.get('/communities', params))

    def get_community(self, community_id, params=None):
        """
        Get a commmunity
        :param int community_id: The id of the community to get
        :param params: Query specific parameters
        :rtype Community
        :return: The Community
        :raises MCAPIError
        """
        return Community(self.get("/communities/" + str(community_id), params))

    def add_dataset_to_community(self, dataset_id, community_id):
        """
        Add a dataset to a community. The dataset must have been published.
        :param int dataset_id:
        :param int community_id:
        :rtype Community
        :return: The community with the dataset
        :raises MCAPIError
        """
        return Community(self.post("/communities/" + str(community_id) + "/datasets/" + str(dataset_id) + "/add"))

    def remove_dataset_from_community(self, dataset_id, community_id):
        """
        Remove a dataset from a community.
        :param int dataset_id:
        :param int community_id:
        :raises MCAPIError
        """
        self.delete("/communities/" + str(community_id) + "/datasets/" + str(dataset_id))

    def upload_file_to_community(self, file_path, community_id):
        """
        TODO: A file has other attributes such as description and summary
        Uploads a file to a community
        :param str file_path: path of file to upload
        :param int community_id: The community to upload the file to
        :return: The community
        :rtype Community
        :raises MCAPIError
        """
        return Community(self.upload("/communities/" + str(community_id) + "/upload", file_path))

    def delete_file_from_community(self, file_id, community_id):
        """
        Deletes file from the community and deletes the file on the system.
        :param int file_id: The file to delete
        :param int community_id: The community to delete it from
        :raises MCAPIError
        """
        self.delete("/communities/" + str(community_id) + "/files/" + str(file_id))

    def create_link_in_community(self, community_id, name, url, attrs=None):
        """
        Adds a link to a community
        :param int community_id: The community to add the link to
        :param str name: name to show for url
        :param str url: url to add
        :param CreateLinkRequest attrs: additional attrs
        :return: The community
        :rtype Community
        :raises MCAPIError
        """
        if not attrs:
            attrs = CreateLinkRequest()
        form = merge_dicts({"url": url, "name": name}, attrs.to_dict())
        return Community(self.post("/communities/" + str(community_id) + "/links", form))

    def delete_link_from_community(self, link_id, community_id):
        """
        Delete a link from a community and remove it from the system.
        :param int link_id: The link to remove
        :param int community_id: The community to delete the link from
        :raises MCAPIError
        """
        self.delete("/communities/" + str(community_id) + "/links/" + str(link_id))

    def list_tags_in_community(self, community_id):
        """
        List all the unique tags across all the published datasets in a community
        :param int community_id: The community to list the tags for
        :return: The list of tags
        :rtype Tag[]
        :raises MCAPIError
        """
        return self.get("/communities/" + str(community_id) + "/tags")

    def get_published_datasets_for_author(self, author):
        """
        Get all published datasets for an author
        :param str author: Author name string
        :return: List of datasets author is on
        :rtype Dataset[]
        :raises MCAPIError
        """
        form = {"author": author}
        return Dataset.from_list(self.post("/published/authors/search", form))

    def get_published_datasets_for_tag(self, tag):
        """
        Get all published datasets tagged with tag
        :param str tag: tag to use
        :return: List of datasets tagged with tag
        :rtype Dataset[]
        :raises MCAPIError
        """
        form = {"tag": tag}
        return Dataset.from_list(self.post("/published/tags/search", form))

    def list_authors_in_community(self, community_id):
        """
        List all unique authors across all the published datasets in a community
        :param int community_id: The community to list the authors for
        :return: The list of authors
        :rtype string[]
        :raises MCAPIError
        """
        return self.get("/communities/" + str(community_id) + "/authors")

    # Tags
    def list_tags_for_published_datasets(self):
        """
        List all tags used in published datasets
        :return: List of tags
        :rtype Tag[]
        :raises MCAPIError
        """
        return Tag.from_list(self.get("/published/tags"))

    # Authors
    def list_published_authors(self):
        """
        List all published authors
        :return: List of authors
        :rtype User[]
        :raises MCAPIError
        """
        return self.get("/published/authors")

    # MQL
    def mql_load_project(self, project_id):
        self.post("/queries/" + str(project_id) + "/load-project", {})

    def mql_reload_project(self, project_id):
        self.post("/queries/" + str(project_id) + "/load-project", {})

    def mql_execute_query(self, project_id, statement, select_processes=True, select_samples=True):
        self.mql_load_project(project_id)
        form = {
            "statement": statement,
            "select_processes": select_processes,
            "select_samples": select_samples
        }
        return self.post("/queries/" + str(project_id) + "/execute-query", form)

    # Internal

    def _throttle(self):
        if self._throttle_s < 0:
            self._throttle_s = 0.0
        if self._throttle_s:
            time.sleep(self._throttle_s)

    # request calls
    def download(self, urlpart, to):
        self._throttle()
        url = self.base_url + urlpart
        with requests.get(url, stream=True, verify=False, headers=self.headers) as r:
            self._handle(r)
            with open(to, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

    def upload(self, urlpart, file_path):
        self._throttle()
        url = self.base_url + urlpart
        with open(file_path, 'rb') as f:
            files = [('files[]', f)]
            r = requests.post(url, verify=False, headers=self.headers, files=files)
            return self._handle_with_json(r)

    def upload_raw(self, urlpart, f):
        self._throttle()
        url = self.base_url + urlpart
        files = [('files[]', f)]
        r = requests.post(url, verify=False, headers=self.headers, files=files)
        return self._handle_with_json(r)

    def get(self, urlpart, params={}, other_params={}):
        self._throttle()
        url = self.base_url + urlpart
        if self.log:
            print("GET:", url)
        params_to_use = merge_dicts(QueryParams.to_query_args(params), other_params)
        r = requests.get(url, params=params_to_use, verify=False, headers=self.headers)
        return self._handle_with_json(r)

    def get_no_value(self, urlpart):
        self._throttle()
        url = self.base_url + urlpart
        if self.log:
            print("GET:", url)
        r = requests.get(url, verify=False, headers=self.headers)
        return self._handle(r)

    def post(self, urlpart, data):
        self._throttle()
        url = self.base_url + urlpart
        if self.log:
            print("POST:", url)
        data = OrderedDict(data)
        r = requests.post(url, json=data, verify=False, headers=self.headers)
        return self._handle_with_json(r)

    def put(self, urlpart, data):
        self._throttle()
        url = self.base_url + urlpart
        if self.log:
            print("PUT:", url)
        data = OrderedDict(data)
        r = requests.put(url, json=data, verify=False, headers=self.headers)
        return self._handle_with_json(r)

    def delete(self, urlpart, params=None):
        self._throttle()
        url = self.base_url + urlpart
        if self.log:
            print("DELETE:", url)
        r = requests.delete(url, verify=False, params=params, headers=self.headers)
        self._handle(r)

    def delete_with_value(self, urlpart):
        self._throttle()
        url = self.base_url + urlpart
        if self.log:
            print("DELETE:", url)
        r = requests.delete(url, verify=False, headers=self.headers)
        return self._handle_with_json(r)

    def _handle(self, r):
        # try:
        #     import json
        #     print("-----------------------------")
        #     print(json.dumps(r.json(), indent=2))
        #     print("-----------------------------")
        # except:
        #     print("no json")
        self.r = r
        self._update_rate_limits_from_request(r)
        try:
            r.raise_for_status()
            return True
        except requests.HTTPError as e:
            if not self.raise_exception:
                return False
            raise MCAPIError(str(e), e.response)

    def _handle_with_json(self, r):
        if not self._handle(r):
            return None
        if r.headers.get('content-type') == 'application/json':
            result = r.json()
            if "data" in result:
                return result["data"]
            else:
                return result
        return None

    def _update_rate_limits_from_request(self, r):
        self.rate_limit = int(r.headers.get('x-ratelimit-limit', self.rate_limit))
        self.rate_limit_remaining = int(r.headers.get('x-ratelimit-remaining', self.rate_limit_remaining))
        self.rate_limit_reset = r.headers.get('x-ratelimit-reset', None)
        self.retry_after = r.headers.get('retry-after', None)

        if self.rate_limit_remaining < 10:
            self._throttle_s = 60. / (self.rate_limit_remaining - 1.)
        else:
            self._throttle_s = 0.0
