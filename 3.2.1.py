import csv
import re

def csv_reader(name):
    """считывает данные из файла csv
    Args:
        name(str): название файла
    Returns:
        list, list: списсок заголовков файла, список строк файла
    """
    csv_list = csv.reader(open(name, encoding='utf-8-sig'))
    data = [x for x in csv_list]
    return data[0], data[1::]

name = input('Введите название файла: ')
header, vac = csv_reader(name)
years = {}
#a = csv.writer(open("vacancies/test.csv", "w"))
for raw in vac:
    year = raw[-1][-24:-20]
    if year not in years.keys():
        years[year] = [raw]
    else:
        years[year].append(raw)
    #a.writerow(raw)
for key in years.keys():
    a = csv.writer(open(f"vacancies/{key}.csv", "w", newline=''))
    a.writerow(header)
    a.writerows(years[key])