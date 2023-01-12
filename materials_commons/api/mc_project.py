from .config import *


def mc_project(project_id):
    config = Config()
    if not config.default_remote.mcurl or not config.default_remote.mcapikey:
        raise Exception("Default remote not set")
    client = config.default_remote.make_client()
    project = client.get_project(project_id)
    project.client = client
    return project
