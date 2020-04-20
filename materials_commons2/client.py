from collections import OrderedDict
import requests
from .models import Project, Experiment, Dataset, Entity, Activity, Workflow, User, File
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

    def update_project(self, attrs, project_id):
        return Project(self.put("/projects" + str(project_id), attrs))

    # Directories

    def get_directory(self, directory_id, params=None):
        return File(self.get("/directories/" + str(directory_id), params))

    def create_directory(self, project_id, name, parent_id, attrs):
        form = {"name": name, "directory_id": parent_id, "project_id": project_id}
        form = merge_dicts(form, attrs)
        return File(self.post("/directories", form))

    def move_directory(self, directory_id, to_directory_id):
        form = {"to_directory_id": to_directory_id}
        return File(self.post("/directories/" + str(directory_id) + "/move", form))

    def rename_directory(self, directory_id, name):
        form = {"name": name}
        return File(self.post("/directories/" + str(directory_id) + "/rename", form))

    def delete_directory(self, directory_id):
        return self.delete("/directories/" + str(directory_id))

    def update_directory(self, directory_id, attrs):
        return File(self.put("/directories/" + str(directory_id), attrs))

    # Files

    def get_file(self, file_id, params):
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

    def get_all_experiments(self, project_id, params=None):
        return Experiment.from_list(self.get("/projects/" + str(project_id) + "/experiments", params))

    def get(self, urlpart, params):
        url = self.base_url + urlpart
        r = requests.get(url, params=QueryParams.to_query_args(params), headers=self.headers)
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
