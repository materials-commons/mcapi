from os import path as os_path
from os import walk
from random import randint
from mcapi import get_remote_config_url, create_project

BASE_DIRECTORY = "/tmp/a_thousand_files"

def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


def get_project(mode):
    project_name = fake_name(mode + "-Stress-Test-")
    project = create_project(project_name, "Project for parallel upload stress test")
    print "Project: " + project.name
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
        print "-------------"
        print exc
        raise


def upload_all_sequential(project, keys, table):
    for key in keys:
        upload_one(project, table[key])


def main():
    directory = BASE_DIRECTORY
    print("Using data at: " + directory)
    print("Connecting to host: " + get_remote_config_url())
    project = get_project("Repeat-Update")

    test_dir_path = os_path.abspath(directory)
    table, keys = make_file_tree_table(test_dir_path)

    project.local_path = test_dir_path
    keys = keys[0:10]

    print len(keys)

    for i in range(0,10):
        print "run %d" % i
        upload_all_sequential(project, keys, table)

if __name__ == '__main__':
    main()
