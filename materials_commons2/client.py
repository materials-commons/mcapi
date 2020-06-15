from collections import OrderedDict
import requests
import logging
from .models import Project, Experiment, Dataset, Entity, Activity, Workflow, User, File, GlobusUpload, GlobusDownload
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


def merge_dicts(dict1, dict2):
    merged = dict1.copy()
    merged.update(dict2)
    return merged


class Client(object):

    def __init__(self, apikey, base_url="https://materialscommons.org/api"):
        self.apikey = apikey
        self.base_url = base_url
        self.log = False
        self.headers = {"Authorization": "Bearer " + self.apikey}
        self.rate_limit = 0
        self.rate_limit_remaining = 0
        self.rate_limit_reset = None
        self.retry_after = None

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

    # Projects
    def get_all_projects(self, params=None):
        """
        Returns a list of all the projects a user has access to
        :param params:
        :return: List of projects
        :rtype Project[]
        """
        return Project.from_list(self.get("/projects", params))

    def create_project(self, name, attrs=None):
        """
        Creates a new project for the authenticated user. Project name must be unique
        :param str name: Name of project
        :param CreateProjectRequest attrs: (optional) Additional attributes for the create request
        :return: The create project
        :rtype Project
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
        """
        return Project(self.get("/projects/" + str(project_id), params))

    def delete_project(self, project_id):
        """
        Deletes a project
        :param int project_id: id of project to delete
        :return: success or failure
        """
        return self.delete("/projects/" + str(project_id))

    def update_project(self, project_id, attrs):
        """
        Updates the given project
        :param int project_id: Id of project to update
        :param UpdateProjectRequest attrs: The attributes to update on the project
        :return: The updated project
        :rtype Project
        """
        return Project(self.put("/projects/" + str(project_id), attrs.to_dict()))

    def add_user_to_project(self, project_id, user_id):
        return Project(self.put("/projects/" + str(project_id) + "/add-user/" + str(user_id), {}))

    def remove_user_from_project(self, project_id, user_id):
        self.delete("/projects/" + str(project_id) + "/remove-user/" + str(user_id))

    # Experiments
    def get_all_experiments(self, project_id, params=None):
        """
        Get all experiments for a given project
        :param int project_id: The project id
        :param params:
        :return: A list of experiments
        :rtype Experiment[]
        """
        return Experiment.from_list(self.get("/projects/" + str(project_id) + "/experiments", params))

    def get_experiment(self, experiment_id, params=None):
        """
        Get an experiment
        :param int experiment_id: The experiment id
        :param params:
        :return: The experiment
        :rtype Experiment
        """
        return Experiment(self.get("/experiments/" + str(experiment_id), params))

    def update_experiment(self, experiment_id, attrs):
        """
        Update attributes of an experiment
        :param int experiment_id: The experiment id
        :param UpdateExperimentRequest attrs: Attributes to update
        :return: The updated experiment
        :rtype Experiment
        """
        form = merge_dicts({"experiment_id": experiment_id}, attrs.to_dict())
        return Experiment(self.put("/experiments/" + str(experiment_id), form))

    def delete_experiment(self, project_id, experiment_id):
        """
        Delete experiment in project
        :param int project_id: The id of the project the experiment is in
        :param experiment_id: The experiment id
        :return: success or failure
        """
        return self.delete("/projects/" + str(project_id) + "/experiments/" + str(experiment_id))

    def create_experiment(self, project_id, name, attrs=None):
        """
        Create a new experiment in a project
        :param int project_id: The id of the project the experiment is in
        :param str name: Name of experiment
        :param CreateExperimentRequest attrs: Additional attributes on the experiment
        :return: The created experiment
        :rtype Experiment
        """
        if not attrs:
            attrs = CreateExperimentRequest()
        form = merge_dicts({"project_id": project_id, "name": name}, attrs.to_dict())
        return Experiment(self.post("/experiments", form))

    def update_experiment_workflows(self, project_id, experiment_id, workflow_id):
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
        """
        return File.from_list(
            self.get("/projects/" + str(project_id) + "/directories/" + str(directory_id) + "/list", params))

    def list_directory_by_path(self, project_id, path, params):
        """
        Return a list of all the files and directories at given path
        :param int project_id: The id of the project the path is in
        :param str path:
        :param params:
        :return: A list of th efiles and directories in the given path
        :rtype File[]
        """
        path_param = {"path": path}
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
        """
        form = {"name": name, "project_id": project_id}
        return File(self.post("/directories/" + str(directory_id) + "/rename", form))

    def delete_directory(self, project_id, directory_id):
        """
        Should not be used yet: Delete a directory only if the directory is empty
        :param int project_id: The project id containing the directory to delete
        :param int directory_id: The id of the directory to delete
        :return: success or failure
        """
        return self.delete("/projects/" + str(project_id) + "/directories/" + str(directory_id))

    def update_directory(self, project_id, directory_id, attrs):
        """
        Update attributes on a directory
        :param int project_id: The project id containing the directory
        :param int directory_id: The id of the directory to update
        :param attrs: Attributes to update
        :return: The updated directory
        :rtype File
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
        """
        return File(self.get("/projects/" + str(project_id) + "/files/" + str(file_id), params))

    def get_file_by_path(self, project_id, file_path):
        """
        Get file by path in project
        :param int project_id: The id of the project containing the file
        :param file_path: The path to the file
        :return: The file
        :rtype File
        """
        form = {"path": file_path, "project_id": project_id}
        return File(self.post("/files/by_path", form))

    def update_file(self, project_id, file_id, attrs):
        """
        Update attributes of a file
        :param project_id:
        :param file_id:
        :param UpdateFileRequest attrs: Attributes to update
        :return: The updated file
        :rtype File
        """
        form = merge_dicts({"project_id", project_id}, attrs.to_dict())
        return File(self.put("/files/" + str(file_id), form))

    def delete_file(self, project_id, file_id):
        """
        Delete a file in a project
        :param int project_id: The id of the project containing the file
        :param int file_id: The id of the file to delete
        :return: success or failure
        """
        return self.delete("/projects/" + str(project_id) + "/files/" + str(file_id))

    def move_file(self, project_id, file_id, to_directory_id):
        """
        Move file into a different directory
        :param int project_id: The project id of the file and the destination directory
        :param int file_id: The id of the file to move
        :param int to_directory_id: The id of the destination directory
        :return: The moved file
        :rtype File
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
        """
        form = {"name": name, "project_id": project_id}
        return File(self.post("/files/" + str(file_id) + "/rename", form))

    def download_file(self, project_id, file_id, to):
        """
        Download a file
        :param int project_id: The project id containing the file to download
        :param int file_id: The id of the file to download
        :param str to: path including file name to download file to
        """
        self.download("/projects/" + str(project_id) + "/files/" + str(file_id) + "/download", to)

    def download_file_by_path(self, project_id, path, to):
        """
        Download a file by path
        :param int project_id: The project id containing the file to download
        :param str path: The path in the project of the file
        :param str to: path including file name to download file to
        """
        file = self.get_file_by_path(project_id, path)
        self.download_file(project_id, file.id, to)

    def upload_file(self, project_id, directory_id, file_path):
        """
        Uploads a file to a project
        :param int project_id: The project to upload file to
        :param int directory_id: The directory in the project to upload the file into
        :param str file_path: path of file to upload
        """
        files = File.from_list(
            self.upload("/projects/" + str(project_id) + "/files/" + str(directory_id) + "/upload", file_path))
        return files[0]

    # Entities
    def get_all_entities(self, project_id, params=None):
        """
        Get all entities in a project
        :param int project_id: The id of the project
        :param params:
        :return: The list of entities
        :rtype Entity[]
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
        """
        return Entity(self.get("/projects/" + str(project_id) + "/entities/" + str(entity_id), params))

    def create_entity(self, project_id, name, attrs=None):
        """
        Creates a new entity in the project
        :param project_id: The id of the project to create entity in
        :param str name: The entity name
        :param CreateEntityRequest attrs: Attributes of the entity
        :return: The created entity
        :rtype Entity
        """
        if not attrs:
            attrs = CreateEntityRequest()
        form = merge_dicts({"name": name, "project_id": project_id}, attrs.to_dict())
        return Entity(self.post("/entities", form))

    def delete_entity(self, project_id, entity_id):
        """
        Delete an entity
        :param int project_id: The id of the project containing the entity
        :param int entity_id: The entity id
        :return: success or failure
        """
        return self.delete("/projects/" + str(project_id) + "/entities/" + str(entity_id))

    # Activities
    def get_all_activities(self, project_id, params=None):
        """
        Get all activities in a project
        :param int project_id: The id of the project
        :param params:
        :return: List of activities
        :rtype Activity[]
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
        """
        return Activity(self.get("/projects/" + str(project_id) + "/activies/" + str(activity_id), params))

    def create_activity(self, project_id, name, attrs=None):
        """
        Create a new activity in the project
        :param project_id: The project to create the activity int
        :param str name: Name of activity
        :param CreateActivityRequest attrs: Attributes on the activity
        :return: The activity to create
        :rtype Activity
        """
        if not attrs:
            attrs = CreateActivityRequest()
        form = merge_dicts({"project_id": project_id, "name": name}, attrs.to_dict())
        return Activity(self.post("/activies", form))

    def delete_activity(self, project_id, activity_id):
        """
        Deletes an activity
        :param project_id: The id of the project containing the activity
        :param activity_id: The id of the activity to delete
        :return: success or failure
        """
        return self.delete("/projects/" + str(project_id) + "/activies/" + str(activity_id))

    # Datasets
    def get_all_datasets(self, project_id, params=None):
        """
        Get all datasets in a project
        :param int project_id: The project id
        :param params:
        :return: The list of datasets
        :rtype Dataset[]
        """
        return Dataset.from_list(self.get("/projects/" + str(project_id) + "/datasets", params))

    def get_all_published_datasets(self, params=None):
        """
        Get all published datasets
        :param params:
        :return: The list of published datasets
        :rtype Dataset[]
        """
        return Dataset.from_list(self.get("/datasets/published", params))

    def get_dataset(self, project_id, dataset_id, params=None):
        """
        Get dataset in a project
        :param int project_id: The project id containing the dataset
        :param int dataset_id: The dataset id
        :param params:
        :return: The dataset
        :rtype Dataset
        """
        return Dataset(self.get("/projects/" + str(project_id) + "/datasets/" + str(dataset_id), params))

    def delete_dataset(self, project_id, dataset_id):
        """
        Delete an unpublished dataset
        :param int project_id: The project id containing the dataset
        :param int dataset_id: The id of the dataset
        :return: success or failure
        """
        return self.delete("/projects/" + str(project_id) + "/datasets/" + str(dataset_id))

    def update_dataset_file_selection(self, project_id, dataset_id, file_selection):
        form = {"project_id": project_id}
        form = merge_dicts(form, file_selection)
        return Dataset(self.put("/datasets/" + str(dataset_id) + "/selection", form))

    def update_dataset_activities(self, project_id, dataset_id, activity_id):
        form = {"project_id": project_id, "activity_id": activity_id}
        return Dataset(self.put("/datasets/" + str(dataset_id) + "/activities/selection", form))

    def update_dataset_entities(self, project_id, dataset_id, entity_id):
        form = {"project_id": project_id, "entity_id": entity_id}
        return Dataset(self.put("/datasets/" + str(dataset_id) + "/entities", form))

    def update_dataset_workflows(self, project_id, dataset_id, workflow_id):
        form = {"project_id": project_id, "workflow_id": workflow_id}
        return Dataset(self.put("/datasets/" + str(dataset_id) + "/workflows", form))

    def publish_dataset(self, project_id, dataset_id):
        """
        Publish a dataset
        :param int project_id: The id of the project containing the dataset
        :param int dataset_id: The dataset id
        :return: The dataset
        :rtype Dataset
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
        """
        if not attrs:
            attrs = UpdateDatasetRequest()
        form = merge_dicts({"name": name}, attrs.to_dict())
        return Dataset(self.put("/projects/" + str(project_id) + "/datasets/" + str(dataset_id), form))

    def download_dataset_zipfile(self, dataset_id, to):
        """
        Download the zipfile for a published dataset
        :param int dataset_id: The id of the published dataset
        :param str to: The path including the file name to write the download to
        """
        self.download("/datasets/" + str(dataset_id) + "/download_zipfile", to)

    def check_file_in_dataset(self, project_id, dataset_id, file_id):
        """
        Check if file is in the dataset selection
        :param int project_id: project dataset and file are in
        :param int dataset_id: dataset to check file_selection against
        :param int file_id: file to check
        :return: {'in_dataset': True} or {'in_dataset': False}
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
        """
        form = {"file_path": file_path}
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
        """
        form = {"project_id": project_id, name: name}
        return GlobusUpload(self.post("/globus/uploads", form))

    def delete_globus_upload_request(self, project_id, globus_upload_id):
        """
        Delete an existing globus upload request
        :param int project_id:
        :param int globus_upload_id:
        :return: success or failure
        """
        return self.delete("/projects/" + str(project_id) + "/globus/" + str(globus_upload_id) + "/uploads")

    def finish_globus_upload_request(self, project_id, globus_upload_id):
        """
        Mark a globus upload request as finished
        :param int project_id: The project id for the upload
        :param int globus_upload_id: The id of the globus upload
        :return: The globus upload
        :rtype GlobusUpload
        """
        form = {"project_id": project_id}
        return GlobusUpload(self.put("/globus/" + str(globus_upload_id) + "/uploads/complete", form))

    def get_all_globus_upload_requests(self, project_id):
        """
        Get all globus uploads in a project
        :param int project_id: The project id
        :return: List of globus uploads
        :rtype GlobusUpload[]
        """
        return GlobusUpload.from_list(self.get("/projects/" + str(project_id) + "/globus/uploads"))

    def create_globus_download_request(self, project_id, name):
        """
        Create a globus download request for a project
        :param int project_id:
        :param str name: The name of the download request
        :return: The globus download
        :rtype GlobusDownload
        """
        form = {"project_id": project_id, "name": name}
        return GlobusDownload(self.post("/globus/downloads", form))

    def delete_globus_download_request(self, project_id, globus_download_id):
        """
        Delete an existing globus download request
        :param int project_id: The id of the project containing the download request
        :param int globus_download_id: The id of the globus download to delete
        :return: success or failure
        """
        return self.delete("/projects/" + str(project_id) + "/globus/" + str(globus_download_id) + "/downloads")

    def get_all_globus_download_requests(self, project_id):
        """
        Get all globus download requests for a project
        :param int project_id: The project
        :return: List of all globus downloads
        :rtype GlobusDownload[]
        """
        return GlobusDownload.from_list(self.get("/projects/" + str(project_id) + "/globus/downloads"))

    def get_globus_download_request(self, project_id, globus_download_id):
        """
        Get a globus download
        :param int project_id: The id of the project containing the globus download
        :param int globus_download_id: The globus download id
        :return: The globus download
        :rtype GlobusDownload
        """
        return GlobusDownload(self.get("/projects/" + str(project_id) + "/globus/downloads/" + str(globus_download_id)))

    # Users
    def get_user_by_email(self, email):
        return User(self.get("/users/by-email/" + email))

    def list_users(self):
        return User.from_list(self.get("/users"))

    # request calls
    def download(self, urlpart, to):
        url = self.base_url + urlpart
        with requests.get(url, stream=True, verify=False, headers=self.headers) as r:
            self._update_rate_limits_from_request(r)
            r.raise_for_status()
            with open(to, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

    def upload(self, urlpart, file_path):
        url = self.base_url + urlpart
        with open(file_path, 'rb') as f:
            files = [('files[]', f)]
            r = requests.post(url, verify=False, headers=self.headers, files=files)
            self._update_rate_limits_from_request(r)
            r.raise_for_status()
            return r.json()["data"]

    def get(self, urlpart, params={}, other_params={}):
        url = self.base_url + urlpart
        if self.log:
            print("GET:", url)
        params_to_use = merge_dicts(QueryParams.to_query_args(params), other_params)
        r = requests.get(url, params=params_to_use, verify=False, headers=self.headers)
        self._update_rate_limits_from_request(r)
        r.raise_for_status()
        return r.json()["data"]

    def post(self, urlpart, data):
        url = self.base_url + urlpart
        if self.log:
            print("POST:", url)
        data = OrderedDict(data)
        r = requests.post(url, json=data, verify=False, headers=self.headers)
        self._update_rate_limits_from_request(r)
        r.raise_for_status()
        return r.json()["data"]

    def put(self, urlpart, data):
        url = self.base_url + urlpart
        if self.log:
            print("PUT:", url)
        data = OrderedDict(data)
        r = requests.put(url, json=data, verify=False, headers=self.headers)
        self._update_rate_limits_from_request(r)
        r.raise_for_status()
        return r.json()["data"]

    def delete(self, urlpart):
        url = self.base_url + urlpart
        if self.log:
            print("DELETE:", url)
        r = requests.delete(url, verify=False, headers=self.headers)
        self._update_rate_limits_from_request(r)
        r.raise_for_status()

    def delete_with_value(self, urlpart):
        url = self.base_url + urlpart
        if self.log:
            print("DELETE:", url)
        r = requests.delete(url, verify=False, headers=self.headers)
        self._update_rate_limits_from_request(r)
        r.raise_for_status()
        return r.json()["data"]

    def _update_rate_limits_from_request(self, r):
        self.rate_limit = int(r.headers.get('x-ratelimit-limit', self.rate_limit))
        self.rate_limit_remaining = int(r.headers.get('x-ratelimit-remaining', self.rate_limit_remaining))
        self.rate_limit_reset = r.headers.get('x-ratelimit-reset', None)
        self.retry_after = r.headers.get('retry-after', None)
