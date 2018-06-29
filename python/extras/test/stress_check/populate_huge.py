import os
from os import walk

BASE_DIR = "/Volumes/Data2/lotsOfDirsOfFiles"
TOTAL_NUMBER_OF_FILES = 1000000
DIRECTORY_SIZE = 1000

def clear_dir(dir):
    create_dir_if_needed(dir)
    test_dir_path = os.path.abspath(dir)
    for (dirpath, dirnames, filenames) in walk(test_dir_path):
        for name in filenames:
            if name.endswith(".txt"):
                path = os.path.join(dirpath, name)
                os.remove(path)


def create_dir_if_needed(name):
    try:
        os.makedirs(name)
    except BaseException:
        pass


def populate():
    clear_dir(BASE_DIR)
    os.chdir(BASE_DIR)
    for i in range(TOTAL_NUMBER_OF_FILES):
        if i % DIRECTORY_SIZE == 0:
            os.chdir(BASE_DIR)
            name = 'sub-' + '%06d' % i
            create_dir_if_needed(name)
            os.chdir(name)
        filename = "testFile" + "%06d" % i + ".txt"
        f = open(filename, "w+")
        line = "This is line of text in file %s \n" % filename
        f.close()


def main():
    populate()


if __name__ == '__main__':
    main()
