#!/usr/bin/env python

from ..api import get_all_templates
import xlsxwriter


def yes_no(setting):
    if setting:
        return 'Yes'
    return 'No'


def write_template_ws(template, wb):
    ws = wb.add_worksheet(template.name[:30])
    setup_params = template.input_data['setup'][0]['properties']
    ws.write_row(0, 0, ['PROC: ' + template.name])
    params = []
    param_headers = []
    max_column_lens = []
    min_width = 8
    for index, p in enumerate(setup_params):
        param_headers.append('PARAM')
        param_width = len(p['name']) + 3
        if param_width < min_width:
            max_column_lens.append(min_width)
        else:
            max_column_lens.append(param_width)
        params.append(p['name'])
    ws.write_row(2, 0, param_headers)
    ws.write_row(3, 0, params)
    for index, ignore in enumerate(max_column_lens):
        ws.set_column(index, index, max_column_lens[index])


def write_to_toc_ws(ws, row, template):
    transforms = yes_no(template.input_data['does_transform'])
    destructive = yes_no(template.input_data['destructive'])
    ws.write_row(row, 0, [index, template.name, template.input_data['process_type'],
                          template.description, transforms, destructive])
    return [len(template.name), len(template.input_data['process_type']), len(template.description)]


if __name__ == "__main__":
    workbook = xlsxwriter.Workbook('/tmp/mc/T.xlsx')
    templates = get_all_templates()
    ws = workbook.add_worksheet('Templates')
    ws.write_row(0, 0, ['Index', 'Template Name', 'Type', 'Description', 'Transforms Sample', 'Destructive'])

    ws_row = 1
    max_toc_lens = [0, 0, 0]
    for index, template in enumerate(templates):
        toc_lens = write_to_toc_ws(ws, ws_row, template)
        if toc_lens[0] > max_toc_lens[0]:
            max_toc_lens[0] = toc_lens[0]
        if toc_lens[1] > max_toc_lens[1]:
            max_toc_lens[1] = toc_lens[1]
        if toc_lens[2] > max_toc_lens[2]:
            max_toc_lens[2] = toc_lens[2]
        ws_row += 1
        write_template_ws(template, workbook)
    ws.set_column(0, 0, 7)
    ws.set_column(1, 1, max_toc_lens[0]+3)
    ws.set_column(2, 2, max_toc_lens[1]+3)
    ws.set_column(3, 3, max_toc_lens[2]+3)
    ws.set_column(4, 4, len('Transforms Sample')+3)
    ws.set_column(5, 5, len('Destructive')+3)
    # worksheet.data_validation('B1', {'validate': 'list',
    #                                   'source': ['temp(c)', 'temp(f)', 'temp(k)']})
    workbook.close()
