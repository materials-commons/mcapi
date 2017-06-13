import time
from os import path as os_path
from os import walk
from mcapi import set_remote_config_url, get_remote_config_url, create_project

def sequential_upload_run():
    project = create_project("Sequential Upload","Project for sequential upload stress test")
    directory = project.get_top_directory()

    test_dir_path = os_path.abspath("./a_thousand_files");

    table = {}
    keys = []

    for (dirpath, dirnames, filenames) in walk(test_dir_path):
        for name in filenames:
            if name.endswith(".txt"):
                path = os_path.join(test_dir_path,name)
                table[name] = path
                keys.append(name)

    start = time.clock()
    for key in keys:
        upload_one(project,directory,key,table[key])
    seconds = (time.clock() - start)
    print seconds


def upload_one(project,directory,file_name,input_path):
    project.add_file_using_directory(directory, file_name, input_path)


def main():
    sequential_upload_run()


if __name__=='__main__':
    main()