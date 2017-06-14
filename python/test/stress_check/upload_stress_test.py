import time
import sys
from random import randint
from Queue import Queue
from threading import Thread
from os import path as os_path
from os import walk
from mcapi import set_remote_config_url, get_remote_config_url, create_project

SEQUENTIAL = 'sequential'
PARALLEL = 'parallel'

def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix+number

def get_project():
    project_name = fake_name("Parallel-Stress-Test")
    project = create_project(project_name, "Project for parallel upload stress test")
    return project

def get_top_dir(project):
    directory = project.get_top_directory()
    return directory

def make_file_tree():
    test_dir_path = os_path.abspath("./a_thousand_files")

    table = {}
    keys = []

    for (dirpath, dirnames, filenames) in walk(test_dir_path):
        for name in filenames:
            if name.endswith(".txt"):
                path = os_path.join(test_dir_path, name)
                table[name] = path
                keys.append(name)

    return table, keys


def upload_one(project, directory, file_name, input_path):
    project.add_file_using_directory(directory, file_name, input_path)

def upload_all_sequential(project, directory, keys, table):
    for key in keys:
        upload_one(project, directory, key, table[key])


def upload_one_parallel(q):
    packet = q.get()
    upload_one(packet['project'], packet['directory'], packet['file_name'], packet['path'])
    print packet['file_name']
    q.task_done()


def upload_all_parallel(project, directory, keys, table):
    q = Queue(maxsize=0)
    num_threads = 10

    for i in range(num_threads):
        worker = Thread(target=upload_one_parallel, args=(q,))
        worker.setDaemon(True)
        worker.start()

    for key in keys:
        packet = {}
        packet['project'] = project
        packet['directory'] = directory
        packet['file_name'] = key
        packet['path'] = table[key]
        q.put(packet)

    q.join()


def exec_all(flag):

    project = get_project()

    directory = get_top_dir(project)

    table, keys = make_file_tree()

    if flag == SEQUENTIAL:
        start = time.clock()
        upload_all_sequential(project, directory, keys, table)
        seconds = (time.clock() - start)
        print seconds

    else:
        start = time.clock()
        upload_all_parallel(project, directory, keys, table)
        seconds = (time.clock() - start)
        print seconds


def main():
    flag = SEQUENTIAL
    if len(sys.argv) < 1:
        flag = PARALLEL
    print flag
    exec_all(flag)


if __name__ == '__main__':
    main()
