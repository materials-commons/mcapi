import sys
import time
from materials_commons.api import get_all_projects

TEST_PROJECT_NAME = "Test1"


def all_done(status_list):
    done = True
    for status in status_list:
        if status.status != 'done':
            done = False
    return done


def print_status_list(status_list):
    print("Status list")
    for status in status_list:
        print("birthtime = {}, status = {}, message = {}".format(status.birthtime, status.status, status.message))


if __name__ == "__main__":

    apikey = "totally-bogus"

    projects = get_all_projects(apikey=apikey)
    project = None

    for probe in projects:
        if probe.name == TEST_PROJECT_NAME:
            project = probe

    if not project:
        print("Failed to fine test project, {}, aborting".format(TEST_PROJECT_NAME))
        sys.exit(-1)

    request = project.init_globus_upload_request()
    print("Use this URL in the Globus web app:")
    print("    {}".format(request.get_url_transfer_target()))
    print("       OR ")
    print("Use this String in the Globus CLI as the destination target")
    print("    {}".format(request.get_cli_transfer_target()))
    time.sleep(20)

    status_list = project.get_globus_upload_status_list()

    while not all_done(status_list):
        print ("Waiting for the requested transfer to finish")
        print_status_list(status_list);
        time.sleep(5)

    print("Done.")

