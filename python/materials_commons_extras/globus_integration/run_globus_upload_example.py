import time
from random import randint
from materials_commons.api import create_project


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


if __name__ == "__main__":

    apikey = "totally-bogus"

    name = fake_name("TestProject-")
    description = "Test project - for testing Globus upload request"
    project = create_project(name, description, apikey=apikey)

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
