import os
from random import randint

def populate():
    os.chdir("a_thousand_files")
    os.makedirs('sub-0')
    os.chdir('sub-0')
    for i in range(10000):
        if (i + 1)%400 == 0:
            os.chdir('..')
            name = 'sub-' + '%04d' % i
            os.makedirs(name)
            os.chdir(name)
        filename = "testFile" + "%04d" % i + ".txt"
        f = open(filename, "w+")
        lines = randint(10,3000)
        for i in range(0,lines):
            f.write("This is line of text in file %s\n" % filename)
        f.close()


def main():
    populate()


if __name__ == '__main__':
    main()
