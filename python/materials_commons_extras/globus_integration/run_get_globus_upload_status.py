import time
from materials_commons.api import get_all_projects

TEST_PROJECT_NAME = "Test1"

if __name__ == "__main__":

    apikey = "totally-bogus"

    projects = get_all_projects(apikey=apikey)
    project = None

    for probe in projects:
        if probe.name == TEST_PROJECT_NAME:
            project = probe

    if not project:
        print("Failed to fine test project, {}, aborting".format(TEST_PROJECT_NAME))

    status_list = project.get_globus_upload_status_list("all")

    print("Done")