import sys
import time
from materials_commons.api import get_all_projects

TEST_PROJECT_NAME = "Test1"

USER_API_KEY = "totally-bogus"
# USER_API_KEY = <your key here>  # for other

# to change remote host, configure base URL in $HOME/.materialscommons/config.json
# for example (for Materials Commons test host):
# {
#   "mcurl": "https://test.materialscommons.org/api"
# }


def all_done(status_list_in):
    done = True
    for status in status_list_in:
        if status.status != 'done':
            done = False
    return done


def print_status_list(status_list_in):
    print("Status list")
    for status in status_list_in:
        if not status.status == 'done':
            print(
                "id = {}, birthtime = {}, status = {}, upload id = {}\n  message = {}"
                .format(status.id, status.birthtime, status.status, status.background_task_id, status.message))


if __name__ == "__main__":

    apikey = USER_API_KEY

    projects = get_all_projects(apikey=apikey)
    project = None

    for probe in projects:
        if probe.name == TEST_PROJECT_NAME:
            project = probe

    if not project:
        print("Failed to find test project, {}, aborting".format(TEST_PROJECT_NAME))
        sys.exit(-1)

    request = project.create_globus_upload_request()
    print("Use this URL in the Globus web app:")
    print("    {}".format(request.get_url_transfer_target()))
    print("       OR ")
    print("Use this String in the Globus CLI as the destination target")
    print("    {}".format(request.get_cli_transfer_target()))
    time.sleep(20)

    status_list = project.get_globus_upload_status_list()

    while not all_done(status_list):
        print("Waiting for the requested transfer to finish")
        print_status_list(status_list)
        time.sleep(5)
        status_list = project.get_globus_upload_status_list()

    print("Done.")
