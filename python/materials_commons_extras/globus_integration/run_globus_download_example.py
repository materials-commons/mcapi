import sys
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
        print("Failed to find test project, {}, aborting".format(TEST_PROJECT_NAME))
        sys.exit(-1)

    request = project.init_globus_download_request()

    print("Use this URL in the Globus web app:")
    print("    {}".format(request.get_url_transfer_source()))
    print("       OR ")
    print("Use this String in the Globus CLI as the destination source")
    print("    {}".format(request.get_cli_transfer_source()))
