#!/usr/bin/env python

from ..api import get_all_templates
import xlsxwriter

colors = []


def yes_no(setting):
    if setting:
        return 'Yes'
    return 'No'


def write_template_ws(template, wb, fill_color):
    ws = wb.add_worksheet(template.name[:30])
    setup_params = template.input_data['setup'][0]['properties']
    ws.write_row(0, 0, ['PROC: ' + template.name])
    params = []
    headers = []
    max_column_lens = []
    min_width = 8
    for index, p in enumerate(setup_params):
        headers.append('PARAM')
        param_width = len(p['name']) + 3
        if param_width < min_width:
            max_column_lens.append(min_width)
        else:
            max_column_lens.append(param_width)
        params.append(p['name'])

    measurements = template.input_data['measurements']
    for m in measurements:
        headers.append('MEAS')
        param_width = len(m['name'])+3
        if param_width < min_width:
            max_column_lens.append(min_width)
        else:
            max_column_lens.append(param_width)
        params.append(m['name'])

    ws.write_row(1, 0, [' '])
    ws.write_row(2, 0, headers)
    ws.write_row(3, 0, params)
    ws.set_column(0, len(max_column_lens), None, fill_color)
    for index, ignore in enumerate(max_column_lens):
        if index == 0:
            ws.set_column(index, index, len(template.name)+9)
        else:
            ws.set_column(index, index, max_column_lens[index])
    if not max_column_lens:
        ws.set_column(0, 0, len(template.name) + 9)


def write_to_toc_ws(ws, row, template):
    transforms = yes_no(template.input_data['does_transform'])
    destructive = yes_no(template.input_data['destructive'])
    ws.write_row(row, 0, [index, template.name, template.input_data['process_type'],
                          template.description, transforms, destructive])
    return [len(template.name), len(template.input_data['process_type']), len(template.description)]


def setup_colors(wb):
    colors.append(wb.add_format({'bg_color': '00FFFF'}))  # 1. Aqua
    colors.append(wb.add_format({'bg_color': '7FFFD4'}))  # 2. Aquamarine
    colors.append(wb.add_format({'bg_color': 'DAA520'}))  # 3. GoldenRod
    colors.append(wb.add_format({'bg_color': 'F5F5DC'}))  # 4. Beige
    colors.append(wb.add_format({'bg_color': '8FBC8F'}))  # 5. DarkSeaGreen
    colors.append(wb.add_format({'bg_color': 'B0C4DE'}))  # 6. LightSteelBlue
    colors.append(wb.add_format({'bg_color': 'A52A2A'}))  # 7. Brown
    colors.append(wb.add_format({'bg_color': 'DEB887'}))  # 8. BurlyWood
    colors.append(wb.add_format({'bg_color': '5F9EA0'}))  # 9. CadetBlue
    colors.append(wb.add_format({'bg_color': '7FFF00'}))  # 10. Chartreuse
    colors.append(wb.add_format({'bg_color': 'D2691E'}))  # 11. Chocolate
    colors.append(wb.add_format({'bg_color': 'FFB6C1'}))  # 12. LightPink
    colors.append(wb.add_format({'bg_color': '6495ED'}))  # 13. CornflowerBlue
    colors.append(wb.add_format({'bg_color': 'FFF8DC'}))  # 14. Cornsilk
    colors.append(wb.add_format({'bg_color': 'FFA07A'}))  # 15. LightSalmon


if __name__ == "__main__":
    workbook = xlsxwriter.Workbook('/tmp/mc/T.xlsx')
    setup_colors(workbook)
    templates = get_all_templates()
    ws = workbook.add_worksheet('Templates')
    ws.write_row(0, 0, ['Index', 'Template Name', 'Type', 'Description', 'Transforms Sample', 'Destructive'])

    ws_row = 1
    max_toc_lens = [0, 0, 0]
    fill_color_index = 0
    for index, template in enumerate(templates):
        if fill_color_index == len(colors):
            fill_color_index = 0
        toc_lens = write_to_toc_ws(ws, ws_row, template)
        if toc_lens[0] > max_toc_lens[0]:
            max_toc_lens[0] = toc_lens[0]
        if toc_lens[1] > max_toc_lens[1]:
            max_toc_lens[1] = toc_lens[1]
        if toc_lens[2] > max_toc_lens[2]:
            max_toc_lens[2] = toc_lens[2]
        ws_row += 1
        write_template_ws(template, workbook, colors[fill_color_index])
        fill_color_index += 1
    ws.set_column(0, 0, 7)
    ws.set_column(1, 1, max_toc_lens[0] + 3)
    ws.set_column(2, 2, max_toc_lens[1] + 3)
    ws.set_column(3, 3, max_toc_lens[2] + 3)
    ws.set_column(4, 4, len('Transforms Sample') + 3)
    ws.set_column(5, 5, len('Destructive') + 3)
    # worksheet.data_validation('B1', {'validate': 'list',
    #                                   'source': ['temp(c)', 'temp(f)', 'temp(k)']})
    workbook.close()
