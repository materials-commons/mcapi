import openpyxl

path1 = "/Users/weymouth/Desktop/input.xlsx"
path2 = "/Users/weymouth/Desktop/test-output/workflow.xlsx"
sheet1 = 'EPMA Results (Original)'
sheet2 = 'Sheet'

class Compare:
    def __init__(self):
        pass

    def read_entire_sheet(self, sheet):
        data = []
        for row in sheet.iter_rows():
            empty_row = True
            values = []
            for cell in row:
                empty_row = empty_row and cell.value
            if empty_row:
                print("encountered empty row at row_index = " + str(len(data)) + ".  " +
                      "Assuming end of data at this location")
                break
            for cell in row:
                value = cell.value
                if value and (str(value).strip() == "" or ("n/a" in str(value).strip())):
                    value = None
                values.append(value)
            data.append(values)
        return data

    def compare(self):
        wb1 = openpyxl.load_workbook(filename=path1)
        print(wb1.get_sheet_names())
        ws1 = wb1[sheet1]
        data1 = self.read_entire_sheet(ws1)

        wb2 = openpyxl.load_workbook(filename=path2)
        print(wb2.get_sheet_names())
        ws2 = wb2[sheet2]
        data2 = self.read_entire_sheet(ws2)

        len1 = len(data1)
        len2 = len(data2)

        end_row = len1
        if not (len1 == len2):
            print("lengths differ: " + str(len1) + ", " + str(len2))
        if len2 < len1:
            end_row = len2

        for row in range(0, end_row):
            identical = True
            row_data1 = data1[row]
            row_data2 = data2[row]
            row_len1 = len(row_data1)
            row_len2 = len(row_data2)
            if not (row_len1 == row_len2):
                print("Row " + str(row) + ", lengths differ: "
                      + str(row_len1) + ", " + str(row_len2))
            end_col = row_len1
            if (row_len2 < row_len1):
                end_col = row_len2
            for col in range(0, end_col):
                match = (row_data1[col] == row_data2[col])
                identical = identical and match
                if not match:
                    print("Mismatch at row = " + row + ", col = " + col + ": "
                          + str(row_data1[col]) + ", " + str(row_data2[col]))
            if row_len1 > end_col:
                print("Extra items, row " + str(row) + ", spreadsheet 1")
                for col in range(end_col, row_len1):
                    print("    " + str(row_data1[col]))
            if row_len2 > end_col:
                print("Extra items, row " + str(row) + ", spreadsheet 2")
                for col in range(end_col, row_len2):
                    print("    " + str(row_data2[col]))


if __name__ == '__main__':
    c = Compare()
    c.compare()
