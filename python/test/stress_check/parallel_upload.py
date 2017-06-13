import time
import sys
from Queue import Queue
from threading import Thread
from os import path as os_path
from os import walk
from mcapi import set_remote_config_url, get_remote_config_url, create_project


def parallel_upload_run():
    project = create_project("Sequential Upload", "Project for sequential upload stress test")
    directory = project.get_top_directory()

    test_dir_path = os_path.abspath("./a_thousand_files");

    table = {}
    keys = []

    for (dirpath, dirnames, filenames) in walk(test_dir_path):
        for name in filenames:
            if name.endswith(".txt"):
                path = os_path.join(test_dir_path, name)
                table[name] = path
                keys.append(name)

    start = time.clock()
    q = Queue(maxsize=0)
    num_threads = 10

    for key in keys:
        packet = {}
        packet['project'] = project
        packet['directory'] = directory
        packet['file_name'] = key
        packet['path'] = table[key]
        q.put(packet)

    for i in range(num_threads):
        worker = Thread(target=do_stuff, args=(q,))
        worker.setDaemon(True)
        worker.start()

    q.join()

    seconds = (time.clock() - start)
    print seconds


def do_stuff(q):
    try:
        packet = q.get()
        upload_one(packet['project'], packet['directory'], packet['file_name'], packet['path'])
        print packet['file_name']
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os_path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
    q.task_done()


def upload_one(project, directory, file_name, input_path):
    project.add_file_using_directory(directory, file_name, input_path)


def main():
    parallel_upload_run()


if __name__ == '__main__':
    main()
