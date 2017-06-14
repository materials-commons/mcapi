import os

def populate():
    os.chdir("a_thousand_files")
    for i in range(1000):
        filename = "testFile" + "%04d" % i + ".txt"
        f = open(filename, "w+")
        f.write("This is line of text in file %s\n" % filename)
        f.close()


def main():
    populate()


if __name__ == '__main__':
    main()
