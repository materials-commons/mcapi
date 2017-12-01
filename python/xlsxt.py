#!/usr/bin/env python

import xlsxwriter

if __name__ == "__main__":
    workbook = xlsxwriter.Workbook('/tmp/mc/T.xlsx')
    worksheet = workbook.add_worksheet()

    # Some data we want to write to the worksheet.
    data = (
        ['Rent', "temp(c)"],
        ['R1', 'T1']
    )

    # Start from the first cell. Rows and columns are zero indexed.
    row = 0
    col = 0

    # Iterate over the data and write it out row by row.
    for item, temp in data:
        worksheet.write(row, col, item)
        worksheet.write(row, col + 1, temp)
        row += 1

    worksheet.data_validation('B1', {'validate': 'list',
                                      'source': ['temp(c)', 'temp(f)', 'temp(k)']})
    workbook.close()
