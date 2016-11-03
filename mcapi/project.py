import api
from mc import Project

def list_projects():
    results = api.projects()
    projects = []
    for r in results:
        projects.append(Project(r))
    return projects

def create_project(name,description):
    ids = api.create_project(name,description)
    project_id = ids['project_id']
    project = Project(name=name, description=description, id=project_id,data=ids)
    return project
