import openpyxl

def parse_sheet(sheet):
    # meaning of values are hardcoded
    # A - ignore
    # B - sample name - first time sample/gemoentry/location is hit, defines a sample type, location
    # C, D - ignore
    # E - sample casting geometry
    # F-H - sample location
    #     F - along width
    #     G - along thickness
    #     H - location
    # I-Q - measurement values
    #     I - reference standard
    #     J - number of points sampled
    #     K,L - number of good points using two standards of "goodness": 98-101 and 98-100.5
    #     M,N - the accumulated measurement value for each goodness set
    #     O - judgment of overall quailty
    #     P,Q - start row and end row for the points collected
    # R - results file(s) name ([name].xlsx and [name].txt)

    process_list = []
    for row in sheet.iter_rows(min_row=2):
        values = []
        for cell in row:
            values = values.append(cell.value)
        create_sample = {
            'type': "create-sample",
            'material': values[1],
            'geometry': values[4]
        }
        sectioning = {
            "location": values[7],
            "width": values[5],
            "thickness": values[6]
        }
        epma = {
            "standard": values[8],
            "points": values[9],
            "goodpoint_101": values[10],
            "goodpoint_100p5": values[11],
            "fg_101": values[12],
            "fg_100p5": values[13],
            "quality": values[14],
            "start_row": values[15],
            "end_row": values[16],
            "data_file": values[17]
        }
        process_list = process_list.append(
            {
                "creaet_sample": create_sample,
                "sectioning": sectioning,
                "epma": epma
            }
        )

    print process_list

def main():
    wb = openpyxl.load_workbook(filename='input_data/EPMA_Melt5b_MC_Demo.xlsx',read_only=True)
    ws = wb['Sheet1']
    process_by_row_list = parse_sheet(ws)


if __name__ == '__main__':
    main()