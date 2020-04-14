from collections import OrderedDict

import requests


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

    def create_project(self, name, summary=None, description=None):
        form = {"name": name}
        if summary is not None:
            form["summary"] = summary
        if description is not None:
            form["description"] = description
        data = self.post("/projects", form)
        self.set_base_project(data["data"]["id"])
        return data

    def get_project(self, project_id, params=None):
        data = self.get("/projects/" + str(project_id), params)
        self.set_base_project(project_id)
        return data

    def delete_project(self, project_id=None):
        if project_id is None:
            project_id = self.project_id
        self.delete("/projects/" + str(project_id))
        if project_id == self.project_id:
            self.set_base_project(None)

    def get_experiments(self):
        if self.project_id is None:
            return None
        return self.get("/projects/" + self.project_id + "/experiments")

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
