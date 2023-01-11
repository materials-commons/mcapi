import os

from .config import *
from .models import Project

def mc_project(project_id):
    client = make_client_and_login_if_necessary(prompt=False)
    project = client.get_project(project_id)
    project.client = client


class MCProject(Project):

    def __init__(self, project_id):
        self.project_id = project_id
        self.client = make_client_and_login_if_necessary(prompt=False)
        project = self.client.get_project(project_id)