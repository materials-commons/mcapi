import time
import sys
from random import randint
from multiprocessing import Queue
from threading import Thread
from os import path as os_path
from os import walk
from materials_commons.api import get_remote_config_url, create_project

# from populate import populate

SEQUENTIAL = 'Sequential'
PARALLEL = 'Parallel'
PARTITIONED = "Partitioned"
BASE_DIRECTORY = "/tmp/a_thousand_files"


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


def get_project(mode):
    project_name = fake_name(mode + "-Stress-Test-")
    project = create_project(project_name, "Project for parallel upload stress test")
    print("Project: " + project.name)
    return project


def make_file_tree_table(tree_dir_path):
    table = {}
    keys = []

    for (dirpath, dirnames, filenames) in walk(tree_dir_path):
        for name in filenames:
            if name.endswith(".txt"):
                path = os_path.join(dirpath, name)
                table[name] = path
                keys.append(name)

    return table, keys


def upload_one(project, input_path):
    try:
        project.add_file_by_local_path(input_path)
    except Exception as exc:
        print("-------------")
        print(exc)
        raise


def upload_all_sequential(project, keys, table):
    for key in keys:
        upload_one(project, table[key])


def upload_one_parallel(q):
    while True:
        packet = q.get()
        try:
            upload_one(packet['project'], packet['path'])
        except BaseException:
            print("Requeueing: " + packet['path'])
            q.put(packet)
        finally:
            q.task_done()


def upload_all_parallel(project, keys, table):
    q = Queue(maxsize=0)
    num_threads = 10

    for i in range(num_threads):
        worker = Thread(target=upload_one_parallel, args=(q,))
        worker.setDaemon(True)
        worker.start()

    for key in keys:
        packet = {}
        packet['project'] = project
        packet['path'] = table[key]
        q.put(packet)

    q.join()


def exec_all(flag, subdir):
    directory = BASE_DIRECTORY
    if subdir:
        directory = BASE_DIRECTORY + "/" + subdir
    print("Starting test: " + flag)
    print("Using data at: " + directory)
    print("Connecting to host: " + get_remote_config_url())
    project = get_project(flag)

    test_dir_path = os_path.abspath(directory)
    table, keys = make_file_tree_table(test_dir_path)

    project.local_path = test_dir_path

    if flag == SEQUENTIAL:
        start = time.clock()
        upload_all_sequential(project, keys, table)
        seconds = (time.clock() - start)
        print(seconds)

    else:
        start = time.clock()
        upload_all_parallel(project, keys, table)
        seconds = (time.clock() - start)
        print(seconds)

    print(project.name)


def main():
    # populate()
    flag = SEQUENTIAL
    subdir = None
    if len(sys.argv) > 1:
        if sys.argv[1] == 'p':
            flag = PARALLEL
        if sys.argv[1] == 'x':
            flag = PARTITIONED
            subdir = sys.argv[2]
    exec_all(flag, subdir)
    print(flag)


if __name__ == '__main__':
    main()
