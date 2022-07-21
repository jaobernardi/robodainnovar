
from copy import copy
import json
import csv
from phone_parser import number_parser
from tabulate import tabulate

def read_file(file):
    data = ""
    while bit := file.read(1):
        if bit == "\n":
            yield data.split(";")
            data = ""
            continue
        data += bit

def main():
    data = []
    indexes = {"names": [], "phones": []}
    while True:
        path = input("File path: ")
        file = read_file(open(path, 'r'))
        header = next(file)
        print(tabulate([header], headers=[i for i in range(len(header))]))
        name_clm = int(input("Name column index: "))
        number_clm = int(input("Number column index: "))

        for line in file:
            if line[name_clm] in indexes['names']:
                continue
            indexes['names'].append(line[name_clm])
            number = number_parser(line[number_clm])
            if number in indexes['phones'] or not number:
                continue
            indexes['phones'].append(number)
            data.append({"name": line[name_clm], "number": number})
        
        option = input("[S]ave current data, [A]dd more files, [P]review current data: ")
        match option.lower():
            case 's':
                with open("output.json", "w") as file:
                    file.write(json.dumps(data, indent=4))
                break
            case 'p':
                with open("preview.json", "w") as file:
                    file.write(json.dumps(data, indent=4))

if __name__ == "__main__":
    main()