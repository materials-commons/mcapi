import openpyxl

from materials_commons.etl.input.metadata import Metadata
from materials_commons.etl.common.worksheet_data import read_entire_sheet


path1 = "/Users/weymouth/Desktop/input.xlsx"
path2 = "/Users/weymouth/Desktop/workflow.xlsx"
# sheet1 = 'EPMA Results (Original)'
sheet1 = 'Initiation Data'
sheet2 = 'Sheet'
metadata_path = "/Users/weymouth/Desktop/metadata.json"


class Compare:

    def compare(self):
        print('---', path1)
        wb1 = openpyxl.load_workbook(filename=path1)
        sheets = wb1.get_sheet_names()
        print("Selecting: ", sheets[0], "(from", sheets, ")")
        ws1 = wb1[sheets[0]]
        data1 = read_entire_sheet(ws1)
        print("data1 size:", len(data1), len(data1[0]))

        print('---', path2)
        wb2 = openpyxl.load_workbook(filename=path2)
        sheets = wb2.get_sheet_names()
        print("Selecting: ", sheets[0], "(from", sheets, ")")
        ws2 = wb2[sheets[0]]
        data2 = read_entire_sheet(ws2)
        print("data2 size:", len(data2), len(data2[0]))

        metadata = Metadata()
        metadata.read(metadata_path)

        print('---')
        if self.comare_data_shape(data1, data2):
            self.compare_headers(metadata, data1, data2)
            self.compare_first_col(metadata, data1, data2)
            self.compare_data_area(metadata, data1, data2)

    @staticmethod
    def comare_data_shape(data1, data2):
        if len(data1) == 0 or len(data1) == 0:
            if len(data1) == 0 and len(data1):
                print("No data in either spreadsheet (zero length)")
            if len(data1) == 0:
                print("No data in spreadsheet 1 (zero length)")
            print("No data in spreadsheet 2 (zero length)")
            return False
        else:
            mismatch = False
            if not len(data1) == len(data2):
                print("Number of data rows differ: ", len(data1), len(data2))
                mismatch = False
            if not len(data1[0]) == len(data2[0]):
                print("Number of data cols differ: ", len(data1[0]), len(data2[0]))
                mismatch = False
            if not mismatch:
                print("Data number of rows and cols match")
        return True

    @staticmethod
    def compare_headers(metadata, data1, data2):
        len1 = len(data1)
        len2 = len(data2)
        if len1 < metadata.header_row_end:
            print("Missing header data (length), data1")
        if len2 < metadata.header_row_end:
            print("Missing header data (length), data2")
        if len1 >= metadata.header_row_end and len2 >= metadata.header_row_end:
            row_length_check = True
            for row in range(0, metadata.header_row_end):
                check1 = len(data1[row]) >= metadata.data_col_end
                check2 = len(data2[row]) >= metadata.data_col_end
                if not check1:
                    print("Header row shorter then expected, data1, row " + str(row))
                if not check2:
                    print("Header row shorter then expected, data2, row " + str(row))
                row_length_check = row_length_check and check1 and check2
            identical = True
            if row_length_check:
                for row in range(0, metadata.header_row_end):
                    row_data1 = data1[row]
                    row_data2 = data2[row]
                    for col in range(0, metadata.data_col_end):
                        match = (row_data1[col] == row_data2[col])
                        identical = identical and match
                        if not match:
                            print("Header mismatch at row = " + str(row) + ", col = " + str(col) + ": "
                                  + str(row_data1[col]) + ", " + str(row_data2[col]))
            if identical:
                print("Headers match")

    @staticmethod
    def compare_first_col(metadata, data1, data2):
        len1 = len(data1)
        len2 = len(data2)
        if len1 < metadata.data_row_end:
            print("Missing rows (first col), data1 " + str(len1))
        if len2 < metadata.data_row_end:
            print("Missing rows (first col), data2 " + str(len2))
        if len1 >= metadata.data_row_end and len2 >= metadata.data_row_end:
            identical = True
            for row in range(0, metadata.data_row_end):
                row_data1 = data1[row]
                row_data2 = data2[row]
                match = (row_data1[0] == row_data2[0])
                identical = identical and match
                if not match:
                    print("First col mismatch at row = " + str(row) + ": "
                          + str(row_data1[0]) + ", " + str(row_data2[0]))
            if identical:
                print("First cols match")

    def compare_data_area(self, metadata, data1, data2):
        len1 = min(len(data1), metadata.data_row_end)
        len2 = min(len(data2), metadata.data_row_end)

        end_row = len1
        if not (len1 == len2):
            print("Data number of rows differ: " + str(len1) + ", " + str(len2))
        if len2 < len1:
            end_row = len2

        if end_row < metadata.data_row_end:
            if len1 < metadata.data_row_end:
                print("Missing data rows, data1, expected "
                      + str(metadata.data_row_end) + ", found" + str(len1))
            if len2 < metadata.data_row_end:
                print("Missing data rows, data2, expected "
                      + str(metadata.data_row_end) + ", found" + str(len2))
        types1 = data1[metadata.header_row_end - 2]
        types2 = data2[metadata.header_row_end - 2]

        types = [""]  # element at index zero is ignored

        for col in range(1, metadata.data_col_end):
            type1 = types1[col]
            type2 = types2[col]
            data_type = type1
            if not type1 == type2:
                print("Data type mismatch, col " + str(col) + ":", type1, type2)
                if self.type_expect_data(type1):
                    data_type = type1
                elif self.type_expect_data(type2):
                    data_type = type2
            types.append(data_type)

        identical = True
        for row in range(metadata.data_row_start, end_row):
            row_data1 = data1[row]
            row_data2 = data2[row]
            row_len1 = min(len(row_data1), metadata.data_col_end)
            row_len2 = min(len(row_data2), metadata.data_col_end)
            if not (row_len1 == row_len2):
                print("Data row " + str(row) + ", lengths differ: "
                      + str(row_len1) + ", " + str(row_len2))
            end_col = row_len1
            if end_col < metadata.data_col_end:
                if row_len1 < metadata.data_col_end:
                    print("Missing data row " + str(row) + " is short, data1, expected "
                          + str(metadata.data_col_end) + ", found" + str(row_len1))
                if row_len2 < metadata.data_col_end:
                    print("Missing data row " + str(row) + " is short, data1, expected "
                          + str(metadata.data_col_end) + ", found" + str(row_len2))
            if row_len2 < row_len1:
                end_col = row_len2

            for col in range(1, end_col):
                if not self.type_expect_data(types[col]):
                    continue
                match = (row_data1[col] == row_data2[col])
                identical = identical and match
                if not match:
                    print("Data mismatch at row = " + str(row) + ", col = " + str(col) + ": "
                          + str(row_data1[col]) + ", " + str(row_data2[col]))

        if identical:
            print("Data values match")

    @staticmethod
    def type_expect_data(data_type):
        return data_type == "MEAS" or data_type == "PARAM"


if __name__ == '__main__':
    c = Compare()
    c.compare()
