import time
import sys
from random import randint
from materials_commons.api import get_remote_config_url, create_project
from materials_commons.api import BulkFileUploader

# from populate import populate

SEQUENTIAL = 'Sequential'
PARALLEL = 'Parallel'
BASE_DIRECTORY = "/tmp/a_thousand_files"


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


def get_project(mode):
    project_name = fake_name(mode + "-Stress-Test-")
    project = create_project(project_name, "Project for parallel upload stress test")
    print("Project: " + project.name)
    return project


def exec_all(flag, subdir):
    directory = BASE_DIRECTORY
    if subdir:
        directory = BASE_DIRECTORY + "/" + subdir
    print("Starting test: " + flag)
    print("Using data at: " + directory)
    print("Connecting to host: " + get_remote_config_url())
    project = get_project(flag)

    parallel = True

    if flag == SEQUENTIAL:
        parallel = False

    project.local_path = directory

    loader = BulkFileUploader(parallel=parallel)
    start = time.clock()
    loader.bulk_upload(project, directory)
    seconds = (time.clock() - start)
    print(seconds)

    print(project.name)


def main():
    flag = SEQUENTIAL
    subdir = None
    if len(sys.argv) > 1:
        if sys.argv[1] == 'p':
            flag = PARALLEL
    exec_all(flag, subdir)
    print(flag)


if __name__ == '__main__':
    main()
