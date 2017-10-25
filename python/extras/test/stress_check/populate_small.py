import os
from os import walk
from random import randint

BASE_DIR = "/tmp/a_thousand_files"
TOTAL_NUMBER_OF_FILE = 50
DIRECTORY_SIZE = 5


def random_tag_for_line(line):
    tag = randint(0, 9999999999)
    return line + " ::  random tag %010d" % tag


def clear_dir():
    create_dir_if_needed(BASE_DIR)
    test_dir_path = os.path.abspath(BASE_DIR)
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
    clear_dir()
    os.chdir(BASE_DIR)
    for i in range(TOTAL_NUMBER_OF_FILE):
        if i % DIRECTORY_SIZE == 0:
            os.chdir(BASE_DIR)
            name = 'sub-' + '%04d' % i
            create_dir_if_needed(name)
            os.chdir(name)
        filename = "testFile" + "%04d" % i + ".txt"
        f = open(filename, "w+")
        lines = randint(10, 3000)
        for j in range(0, lines):
            line = random_tag_for_line("This is line of text in file %s" % filename)
            f.write(line + "\n")
        f.close()


def main():
    populate()


if __name__ == '__main__':
    main()
