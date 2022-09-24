import re

def number_parser(number: str):
    clean_number: str = re.sub('\D+', '', number)
    if len(clean_number) > 11 and clean_number.startswith("55"):
        clean_number = clean_number.removeprefix("55")
    
    if len(clean_number) == 11:
        return f'55{clean_number[0:2]}{clean_number[3:7]}{clean_number[7:11]}'
    elif len(clean_number) == 10:
        return f"55{clean_number}"
    

if __name__ == "__main__":
    print(f"Parsed number: {number_parser(input('Input number: '))}")