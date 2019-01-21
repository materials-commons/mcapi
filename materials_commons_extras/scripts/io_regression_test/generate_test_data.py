import os

names = [
    "file1.txt",
    "file2.txt",
    "file3.txt",
    "file4.txt",
    "file5.txt",
    "not_upload_file.txt",
]

paths = [
    'test_data/data/',
    'test_data/data/NotUpload/',
    'test_data/data/Otherdir/',
    'test_data/data/results/',
    'test_data/data/Subdir/'
]

for path in paths:
    os.makedirs(path)

sets = [[0, 5], [4], [3], [], [1,2]]

for p in range(0, len(sets)):
    path = paths[p]
    set = sets[p]
    for n in range(0, len(set)):
        name = names[set[n]]
        with open(path + name, 'w') as file:
            file.write("This is a test data file, " + name + "\n")
            file.close()

for i in range(1,20):
    tag = str(i)
    if i < 10:
        tag = "0" + tag
    name = "DataFile" + tag + ".txt"
    with open(paths[3] + name,'w') as file:
        file.write("This is a test data file, " + name + "\n")
        file.close()

print("done.")