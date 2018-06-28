import os

BASE_DIR = "/Volumes/Data2/lotsOfDirsOfFiles"
NAME_OF_SPREADSHEET_FILE = "huge_data_worflow.xlsx"

dir_list = [os.path.join(BASE_DIR,x) for x in os.listdir(BASE_DIR)]
dir_list = filter(os.path.isdir, dir_list)
dir_list = [os.path.basename(os.path.normpath(x)) for x in dir_list]

