import time
from random import randint
from materials_commons.api import create_project

BASE_DIRECTORY = "/tmp/a_thousand_files/"


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


def get_project():
    project_name = fake_name("Upload-Two-Test-")
    project = create_project(project_name, "Project for testing upload of file")
    return project


def main():
    project = get_project()
    project.local_path = BASE_DIRECTORY
    print("Project: " + project.name)
    print("Local Path: " + project.local_path)
    directory = "sub-0000/"
    for n in range(0, 10):
        filename = "testFile" + "%04d" % n + ".txt"
        path = BASE_DIRECTORY + directory + filename
        project.add_file_by_local_path(path)
        print("After upload: " + path)
        # time.sleep(10)
    directory = "sub-0010/"
    for n in range(10, 20):
        filename = "testFile" + "%04d" % n + ".txt"
        path = BASE_DIRECTORY + directory + filename
        project.add_file_by_local_path(path)
        print("After upload: " + path)
        # time.sleep(10)


if __name__ == '__main__':
    main()
