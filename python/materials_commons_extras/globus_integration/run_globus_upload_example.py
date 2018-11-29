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

    request = project.init_globus_upload_request()
    print("Use this URL in the Globus web app:")
    print("    {}".format(request.get_url_transfer_target()))
    print("       OR ")
    print("Use this String in the Globus CLI as the destination target")
    print("    {}".format(request.get_cli_transfer_target()))
    time.sleep(20)

    while not request.is_done():
        print ("Waiting for the requested transfer to finish")
        time.sleep(5)

    print("Done.")
