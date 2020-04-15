from collections import OrderedDict

import requests


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

    def list_projects(self, params=None):
        return self.get("/projects", params)

    def create_project(self, name, attrs={}):
        form = {"name": name}
        form = merge_dicts(form, attrs)
        return self.post("/projects", form)

    def get_project(self, project_id, params=None):
        return self.get("/projects/" + str(project_id), params)

    def delete_project(self, project_id):
        return self.delete("/projects/" + str(project_id))

    def update_project(self, attrs, project_id):
        return self.put("/projects" + str(project_id), attrs)

    # Directories

    def get_directory(self, directory_id, params=None):
        return self.get("/directories/" + str(directory_id), params)

    def create_directory(self, project_id, name, parent_id, attrs):
        form = {"name": name, "directory_id": parent_id, "project_id": project_id}
        form = merge_dicts(form, attrs)
        return self.post("/directories", form)

    def move_directory(self, directory_id, to_directory_id):
        form = {"to_directory_id": to_directory_id}
        return self.post("/directories/" + str(directory_id) + "/move", form)

    def rename_directory(self, directory_id, name):
        form = {"name": name}
        return self.post("/directories/" + str(directory_id) + "/rename", form)

    def delete_directory(self, directory_id):
        return self.delete("/directories/" + str(directory_id))

    def update_directory(self, directory_id, attrs):
        return self.put("/directories/" + str(directory_id), attrs)

    # Files

    def get_file(self, file_id, params):
        return self.get("/files/" + str(file_id), params)

    def update_file(self, file_id, attrs):
        return self.put("/files/" + str(file_id), attrs)

    def delete_file(self, file_id):
        return self.delete("/files/" + str(file_id))

    def move_file(self, file_id, to_directory_id):
        form = {"directory_id": to_directory_id}
        return self.post("/files/" + str(file_id) + "/move", form)

    def rename_file(self, file_id, name):
        form = {"name": name}
        return self.post("/files/" + str(file_id) + "/rename", form)

    # Datasets

    def list_datasets(self, project_id, params=None):
        return self.get("/projects/" + str(project_id) + "/datasets", params)

    def get_dataset(self, project_id, dataset_id, params=None):
        return self.get("/projects/" + str(project_id) + "/datasets/" + str(dataset_id), params)

    def delete_dataset(self, project_id, dataset_id):
        return self.delete("/projects/" + str(project_id) + "/datasets/" + str(dataset_id))

    def update_dataset_file_selection(self, project_id, dataset_id, file_selection):
        form = {"project_id": project_id}
        form = merge_dicts(form, file_selection)
        return self.put("/datasets/" + str(dataset_id) + "/selection", form)

    def update_dataset_activities(self, project_id, dataset_id, activity_id):
        form = {"project_id": project_id, "activity_id": activity_id}
        return self.put("/datasets/" + str(dataset_id) + "/activities/selection", form)

    def update_dataset_entities(self, project_id, dataset_id, entity_id):
        form = {"project_id": project_id, "entity_id": entity_id}
        return self.put("/datasets/" + str(dataset_id) + "/entities", form)

    def update_dataset_workflows(self, project_id, dataset_id, workflow_id):
        form = {"project_id": project_id, "workflow_id": workflow_id}
        return self.put("/datasets/" + str(dataset_id) + "/workflows", form)

    def publish_dataset(self, project_id, dataset_id):
        form = {"project_id": project_id}
        return self.put("/datasets/" + str(dataset_id) + "/publish", form)

    def unpublish_dataset(self, project_id, dataset_id):
        form = {"project_id": project_id}
        return self.put("/datasets/" + str(dataset_id) + "/unpublish", form)

    def create_dataset(self, project_id, name, attrs):
        form = merge_dicts({"name": name, "project_id": project_id, "action": "ignore"}, attrs)
        return self.post("/datasets", form)

    def update_dataset(self, project_id, dataset_id, name, attrs):
        form = merge_dicts({"name": name, "project_id": project_id, "action": "ignore"}, attrs)
        return self.put("/datasets/" + str(dataset_id), form)

    # def get_experiments(self):
    #     if self.project_id is None:
    #         return None
    #     return self.get("/projects/" + self.project_id + "/experiments")

    def get(self, urlpart, params):
        url = self.base_url + urlpart
        r = requests.get(url, params=params, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def post(self, urlpart, data):
        url = self.base_url + urlpart
        data = OrderedDict(data)
        r = requests.post(url, json=data, verify=False, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def put(self, urlpart, data):
        url = self.base_url + urlpart
        data = OrderedDict(data)
        r = requests.put(url, json=data, verify=False, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def delete(self, urlpart):
        url = self.base_url + urlpart
        r = requests.delete(url, verify=False, headers=self.headers)
        r.raise_for_status()
