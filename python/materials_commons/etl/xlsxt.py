#!/usr/bin/env python

from ..api import get_all_templates
import xlsxwriter


def yes_no(setting):
    if setting:
        return 'Yes'
    return 'No'


if __name__ == "__main__":
    workbook = xlsxwriter.Workbook('/tmp/mc/T.xlsx')
    templates = get_all_templates()
    ws = workbook.add_worksheet('Templates')
    ws.write_row(0, 0, ['Index', 'Template Name', 'Type', 'Description', 'Transforms Sample', 'Destructive'])

    row = 1
    for index, template in enumerate(templates):
        template_ws = workbook.add_worksheet(template.name[:30])
        transforms = yes_no(template.input_data['does_transform'])
        destructive = yes_no(template.input_data['destructive'])
        ws.write_row(row, 0, [index, template.name, template.input_data['process_type'],
                              template.description, transforms, destructive])
        row += 1
    # worksheet.data_validation('B1', {'validate': 'list',
    #                                   'source': ['temp(c)', 'temp(f)', 'temp(k)']})
    workbook.close()
