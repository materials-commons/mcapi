outfile = open('file_size.csv', 'w')

with open('file_size_raw.txt') as f:
    for line in f:
        line = line.strip()
        values = line.split()
        if len(values) != 4:
            print(line)
        names = values[3].split('/')
        outline = values[2] + "," + names[-1] + '\n'
        outfile.write(outline)

outfile.close()
