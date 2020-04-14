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
        self.project_id = None
        self.headers = {"Authorization": "Bearer " + self.apikey}

    def set_base_project(self, project_id):
        self.project_id = project_id

    def get_projects(self, params=None):
        return self.get("/projects", params)

    def create_project(self, name, attrs={}):
        form = {"name": name}
        form = merge_dicts(form, attrs)
        data = self.post("/projects", form)
        self.set_base_project(data["data"]["id"])
        return data

    def get_project(self, project_id, params=None):
        data = self.get("/projects/" + str(project_id), params)
        self.set_base_project(project_id)
        return data

    def delete_project(self, project_id=None):
        project_id = self._get_project_id(project_id)
        self.delete("/projects/" + str(project_id))
        if project_id == self.project_id:
            self.set_base_project(None)

    def update_project(self, attrs, project_id=None):
        project_id = self._get_project_id(project_id)
        return self.put("/projects" + str(project_id), attrs)

    def get_directory(self, directory_id, params=None):
        return self.get("/directories/" + str(directory_id), params)

    def create_directory(self, name, parent_id, attrs):
        form = {"name": name, "directory_id": parent_id, "project_id": self.project_id}
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

    def _get_project_id(self, project_id):
        if project_id is None:
            return self.project_id
        return project_id

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
