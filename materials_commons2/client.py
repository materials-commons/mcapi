from collections import OrderedDict
import requests
from .models import Project, Experiment, Dataset, Entity, Activity, Workflow, User, File, GlobusUpload, GlobusDownload
from .query_params import QueryParams


def merge_dicts(dict1, dict2):
    merged = dict1.copy()
    merged.update(dict2)
    return merged


class Client(object):

    def __init__(self, apikey, base_url="https://materialscommons.org/api"):
        self.apikey = apikey
        self.base_url = base_url
        self.headers = {"Authorization": "Bearer " + self.apikey}

    @staticmethod
    def get_apikey(email, password, base_url="https://materialscommons.org/api"):
        url = base_url + "/get_apitoken"
        form = {"email": email, "password": password}
        r = requests.post(url, json=form, verify=False)
        r.raise_for_status()
        return r.json()["data"]

    @staticmethod
    def login(email, password, base_url="https://materialscommons.org/api"):
        apikey = Client.get_apikey(email, password, base_url)
        return Client(apikey, base_url)

    # Projects
    def get_all_projects(self, params=None):
        return Project.from_list(self.get("/projects", params))

    def create_project(self, name, attrs={}):
        form = {"name": name}
        form = merge_dicts(form, attrs)
        return Project(self.post("/projects", form))

    def get_project(self, project_id, params=None):
        return Project(self.get("/projects/" + str(project_id), params))

    def delete_project(self, project_id):
        return self.delete("/projects/" + str(project_id))

    def update_project(self, project_id, attrs):
        return Project(self.put("/projects" + str(project_id), attrs))

    # Experiments
    def get_all_experiments(self, project_id, params=None):
        return Experiment.from_list(self.get("/projects/" + str(project_id) + "/experiments", params))

    def get_experiment(self, project_id, experiment_id, params=None):
        return Experiment(self.get("/projects/" + str(project_id) + "/experiments/" + str(experiment_id), params))

    def update_experiment(self, project_id, experiment_id, attrs):
        form = merge_dicts({"project_id": project_id}, attrs)
        return Experiment(self.put("/experiments/" + str(experiment_id), form))

    def delete_experiment(self, project_id, experiment_id):
        return self.delete("/projects/" + str(project_id) + "/experiments/" + str(experiment_id))

    def create_experiment(self, project_id, attrs):
        form = merge_dicts({"project_id": project_id}, attrs)
        return Experiment(self.post("/experiments", form))

    def update_experiment_workflows(self, project_id, experiment_id, workflow_id):
        form = {"project_id": project_id, "workflow_id": workflow_id}
        return Experiment(self.put("/experiments/" + str(experiment_id) + "/workflows/selection", form))

    # Directories
    def get_directory(self, project_id, directory_id, params=None):
        return File(self.get("/projects/" + str(project_id) + "/directories/" + str(directory_id), params))

    def list_directory(self, project_id, directory_id, params=None):
        return File.from_list(
            self.get("/projects/" + str(project_id) + "/directories/" + str(directory_id) + "/list", params))

    def list_directory_by_path(self, project_id, path, params):
        path_param = {"path": path}
        return File.from_list(self.get("/projects/" + str(project_id) + "/directories_by_path", params, path_param))

    def create_directory(self, project_id, name, parent_id, attrs):
        form = {"name": name, "directory_id": parent_id, "project_id": project_id}
        form = merge_dicts(form, attrs)
        return File(self.post("/directories", form))

    def move_directory(self, project_id, directory_id, to_directory_id):
        form = {"to_directory_id": to_directory_id, "project_id": project_id}
        return File(self.post("/directories/" + str(directory_id) + "/move", form))

    def rename_directory(self, project_id, directory_id, name):
        form = {"name": name, "project_id": project_id}
        return File(self.post("/directories/" + str(directory_id) + "/rename", form))

    def delete_directory(self, project_id, directory_id):
        return self.delete("/projects/" + str(project_id) + "/directories/" + str(directory_id))

    def update_directory(self, project_id, directory_id, attrs):
        form = merge_dicts({"project_id": project_id}, attrs)
        return File(self.put("/directories/" + str(directory_id), form))

    # Files
    def get_file(self, file_id, params=None):
        return File(self.get("/files/" + str(file_id), params))

    def update_file(self, file_id, attrs):
        return File(self.put("/files/" + str(file_id), attrs))

    def delete_file(self, file_id):
        return self.delete("/files/" + str(file_id))

    def move_file(self, file_id, to_directory_id):
        form = {"directory_id": to_directory_id}
        return File(self.post("/files/" + str(file_id) + "/move", form))

    def rename_file(self, file_id, name):
        form = {"name": name}
        return File(self.post("/files/" + str(file_id) + "/rename", form))

    # Entities
    def get_all_entities(self, project_id, params=None):
        return Entity.from_list(self.get("/projects/" + str(project_id) + "/entities", params))

    def get_entity(self, project_id, entity_id, params=None):
        return Entity(self.get("/projects/" + str(project_id) + "/entities/" + str(entity_id), params))

    def create_entity(self, project_id, attrs):
        form = merge_dicts({"project_id": project_id}, attrs)
        return Entity(self.post("/entities", form))

    def delete_entity(self, project_id, entity_id):
        return self.delete("/projects/" + str(project_id) + "/entities/" + str(entity_id))

    # Activities
    def get_all_activities(self, project_id, params=None):
        return Activity.from_list(self.get("/projects/" + str(project_id) + "/activities", params))
    
    def get_activity(self, project_id, activity_id, params=None):
        return Activity(self.get("/projects/" + str(project_id) + "/activies/" + str(activity_id), params))

    def create_activity(self, project_id, attrs):
        form = merge_dicts({"project_id": project_id}, attrs)
        return Activity(self.post("/activies", form))

    def delete_activity(self, project_id, activity_id):
        return self.delete("/projects/" + str(project_id) + "/activies/" + str(activity_id))

    # Datasets
    def get_all_datasets(self, project_id, params=None):
        return Dataset.from_list(self.get("/projects/" + str(project_id) + "/datasets", params))

    def get_dataset(self, project_id, dataset_id, params=None):
        return Dataset(self.get("/projects/" + str(project_id) + "/datasets/" + str(dataset_id), params))

    def delete_dataset(self, project_id, dataset_id):
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
        form = {"project_id": project_id}
        return Dataset(self.put("/datasets/" + str(dataset_id) + "/publish", form))

    def unpublish_dataset(self, project_id, dataset_id):
        form = {"project_id": project_id}
        return Dataset(self.put("/datasets/" + str(dataset_id) + "/unpublish", form))

    def create_dataset(self, project_id, name, attrs):
        form = merge_dicts({"name": name, "project_id": project_id, "action": "ignore"}, attrs)
        return Dataset(self.post("/datasets", form))

    def update_dataset(self, project_id, dataset_id, name, attrs):
        form = merge_dicts({"name": name, "project_id": project_id, "action": "ignore"}, attrs)
        return Dataset(self.put("/datasets/" + str(dataset_id), form))

    # Activities
    def get_all_activities(self, project_id):
        pass

    # Entities

    # Globus
    def create_globus_upload_request(self, project_id, name):
        form = {"project_id": project_id, name: name}
        return self.post("/globus/uploads", form)

    def delete_globus_upload_request(self, project_id, globus_upload_id):
        return self.delete("/projects/" + str(project_id) + "/globus/" + str(globus_upload_id) + "/uploads")

    def finish_globus_upload_request(self, project_id, globus_upload_id):
        form = {"project_id": project_id}
        return GlobusUpload(self.put("/globus/" + str(globus_upload_id) + "/uploads/complete", form))

    def get_all_globus_upload_requests(self, project_id):
        return GlobusUpload.from_list(self.get("/projects/" + str(project_id) + "/globus/uploads"))

    def create_globus_download_request(self, project_id, name):
        form = {"project_id": project_id, "name": name}
        return GlobusDownload(self.post("/globus/downloads", form))

    def delete_globus_download_request(self, project_id, globus_download_id):
        return self.delete("/projects/" + str(project_id) + "/globus/" + str(globus_download_id) + "/downloads")

    def get_all_globus_download_requests(self, project_id):
        return GlobusDownload.from_list(self.get("/projects/" + str(project_id) + "/globus/downloads"))

    def get_globus_download_request(self, project_id, globus_download_id):
        return GlobusDownload(self.get("/projects/" + str(project_id) + "/globus/downloads/" + str(globus_download_id)))

    # request calls

    def get(self, urlpart, params, other_params={}):
        url = self.base_url + urlpart
        params_to_use = merge_dicts(QueryParams.to_query_args(params), other_params)
        r = requests.get(url, params=params_to_use, headers=self.headers)
        r.raise_for_status()
        return r.json()["data"]

    def post(self, urlpart, data):
        url = self.base_url + urlpart
        data = OrderedDict(data)
        r = requests.post(url, json=data, verify=False, headers=self.headers)
        r.raise_for_status()
        return r.json()["data"]

    def put(self, urlpart, data):
        url = self.base_url + urlpart
        data = OrderedDict(data)
        r = requests.put(url, json=data, verify=False, headers=self.headers)
        r.raise_for_status()
        return r.json()["data"]

    def delete(self, urlpart):
        url = self.base_url + urlpart
        r = requests.delete(url, verify=False, headers=self.headers)
        r.raise_for_status()
