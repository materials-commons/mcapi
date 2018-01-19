def read_entire_sheet(sheet):
    data = []
    max_last_data_col = 0
    for row in sheet.iter_rows():
        empty_row = True
        values = []
        for cell in row:
            empty_row = empty_row and (not cell.value)
        if empty_row:
            print("encountered empty row at row_index = " + str(len(data)) + ".  " +
                  "Assuming end of data at this location")
            break
        for cell in row:
            value = cell.value
            if str(value).strip() == "" or ("n/a" in str(value).strip()):
                value = None
            if value and len(values) >= max_last_data_col:
                max_last_data_col = len(values) + 1
            values.append(value)
        data.append(values)
    if len(data[0]) > max_last_data_col:
        print("encountered empty col at col_index = " + str(max_last_data_col) + ".  " +
              "Assuming end of data at this location")
        remake_data = []
        for row in range(0, len(data)):
            values = []
            data_row = data[row]
            for col in range(0, max_last_data_col):
                value = data_row[col]
                values.append(value)
            remake_data.append(values)
        data = remake_data
    return data
