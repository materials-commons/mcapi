import os
from materials_commons.etl.common.worksheet_data import ExcelIO

BASE_DIR = "/Volumes/Data2/lotsOfDirsOfFiles"
NAME_OF_SPREADSHEET_FILE = "huge_data_worflow.xlsx"

dir_list = [os.path.join(BASE_DIR,x) for x in os.listdir(BASE_DIR)]
dir_list = filter(os.path.isdir, dir_list)
dir_list = [os.path.basename(os.path.normpath(x)) for x in dir_list]

data = []
data.append(["", "PROC: Create Sample", ""])
data.append(["", "SAMPLES", "FILES"])

for i in range(0, len(dir_list)):
    sample_name = "Sample" + '%03d' % i
    data.append(["", sample_name,dir_list[i]])

data[2][0] = "BEGIN_DATA"

interface = ExcelIO()
interface.write_data(os.path.join(BASE_DIR,NAME_OF_SPREADSHEET_FILE), data)
