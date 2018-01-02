import json
import time
from pprint import pprint

class Metadata:
    def __init__(self):
        self.time_stamp = time.ctime()
        self.excluded_keys = ["excluded_keys"]
        self.process_metadata = []

    def write(self, path):
        metadata_dict = self.format()
        with open(path, 'w') as out:
            out.write(json.dumps(metadata_dict, indent=2))
            out.close

    def read(self,path):
        with open(path) as json_data:
            d = json.load(json_data)
            json_data.close()
        attr = ["time_stamp", "process_metadata","project_id","experiment_id",
                "header_row_end","data_row_start", "data_col_start","data_col_end",
                "start_attribute_row", "sheet_headers"]
        for a in attr:
            # print(a, d.get(a, None))
            setattr(self, a, d.get(a, None))

    def format(self):
        return dict(
            (key, value)
            for (key, value) in self.__dict__.items()
            if key not in self.excluded_keys
            )

    def set_input_information(self,input, data_dir, json_path):
        self.input_excel_file_path = input
        self.input_data_dir_path = data_dir
        self.output_json_file_path = json_path

    def set_project_id(self,id):
        self.project_id = id

    def set_experiment_id(self,id):
        self.experiment_id = id

    def set_header_row_end(self, row):
        self.header_row_end = row

    def set_data_row_start(self, row):
        self.data_row_start = row

    def set_data_col_start(self,col):
        self.data_col_start = col

    def set_data_col_end(self, col):
        self.data_col_end = col

    def set_start_attribute_row(self, row):
        self.start_attribute_row = row

    def record_header(self,header):
        self.sheet_headers = header

    def set_process_metadata(self, row, col, template_id, process):
        self.process_metadata.append(
            {'id': process.id,
             'template': template_id,
             'row': row,
             'col': col,
             }
        )
