import openpyxl

def main():
    wb = openpyxl.load_workbook(filename='input_data/EPMA_Melt5b_MC_Demo.xlsx',read_only=True)
    ws = wb['Sheet1']
    for row in ws.iter_rows(min_row=2):
        values = []
        for cell in row:
            values.append(cell.values)
        print values

if __name__ == '__main__':
    main()