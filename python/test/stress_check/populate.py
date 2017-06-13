import os

def populate():
    os.chdir("a_thousand_files")
    for i in range(1000):
        padding = ""
        if (i < 1000): padding += "0"
        if (i < 100):  padding += "0"
        if (i < 10):   padding += "0"
        filename = "testFile" + padding + "%d" % i + ".txt"
        f = open(filename, "w+")
        f.write("This is line of text in file %s\n" % filename)
        f.close()


def main():
    populate()


if __name__ == '__main__':
    main()
