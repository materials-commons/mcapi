import time
import sys
from random import randint
from Queue import Queue
from threading import Thread
from os import path as os_path
from os import walk
from mcapi import set_remote_config_url, get_remote_config_url, create_project

SEQUENTIAL = 'Sequential'
PARALLEL = 'Parallel'


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


def get_project(mode):
    project_name = fake_name(mode + "-Stress-Test-")
    project = create_project(project_name, "Project for parallel upload stress test")
    return project


def get_top_dir(project):
    directory = project.get_top_directory()
    return directory


def make_dir_list(tree_dir_path):
    dirs = []
    for (dirpath, dirnames, filenames) in walk(tree_dir_path):
        dirs.append(dirpath)
    return dirs


def make_file_tree(tree_dir_path):
    table = {}
    keys = []

    for (dirpath, dirnames, filenames) in walk(tree_dir_path):
        for name in filenames:
            if name.endswith(".txt"):
                path = os_path.join(dirpath, name)
                table[name] = path
                keys.append(name)

    return table, keys


def make_all_dirs(project, dirs):
    for path in dirs:
        project.add_directory_tree_by_local_path(path)


def upload_one(project, input_path):
    project.add_file_by_local_path(input_path)


def upload_all_sequential(project, keys, table):
    for key in keys:
        upload_one(project, table[key])


def upload_one_parallel(q):
    while (True):
        packet = q.get()
        upload_one(packet['project'], packet['path'])
        q.task_done()


def upload_all_parallel(project, keys, table):
    q = Queue(maxsize=0)
    num_threads = 20

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


def exec_all(flag):
    project = get_project(flag)

    test_dir_path = os_path.abspath("./a_thousand_files")
    dirs = make_dir_list(test_dir_path)
    table, keys = make_file_tree(test_dir_path)

    project.local_path = test_dir_path

    if flag == SEQUENTIAL:
        start = time.clock()
        make_all_dirs(project, dirs)
        seconds = (time.clock() - start)
        print seconds

        start = time.clock()
        upload_all_sequential(project, keys, table)
        seconds = (time.clock() - start)
        print seconds

    else:
        start = time.clock()
        make_all_dirs(project, dirs)
        seconds = (time.clock() - start)
        print seconds

        start = time.clock()
        upload_all_parallel(project, keys, table)
        seconds = (time.clock() - start)
        print seconds

    print project.name


def main():
    flag = SEQUENTIAL
    if len(sys.argv) > 1:
        flag = PARALLEL
    exec_all(flag)
    print flag


if __name__ == '__main__':
    main()
