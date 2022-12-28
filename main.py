import csv
import re
from collections import Counter
import openpyxl
from openpyxl.styles import Border, Side, Font
import matplotlib.pyplot as plt
import numpy as np
import doctest
import time
from multiprocessing import Pool, Queue, Process
from pathlib import Path


class Report:
    """Класс для представления отчета
    Attributes:
        file (Workbook): контейнер для всех остальных частей XLSX-документа
    """
    def __init__(self):
        """Инициализирует объект Report, создает страницу в таблице exel под именем 'Статистика по годам'
        """
        self.file = openpyxl.Workbook()

        ws = self.file.active
        ws.title = "Статистика по годам"

    def generate_excel(self, list_years):
        """Заполняет страницу 'Статистика по годам' exel таблицы переданной информацией начиная с 2007 года,
         создает и заполняет страницу "Статистика по городам" переданными данными
        Args:
            list_years([{str: int}]): список словарей содержащих статистику по годам
        """
        ws = self.file["Статистика по годам"]
        ws.append(["Год", "Средняя зарплата", f"Средняя зарплата - {prof}", "Количество вакансий" , f"Количество вакансий - {prof}"])
        years = list(list_years[0].keys())
        l = len(years)
        i = 0
        flag = True
        thins = Side(border_style="thin", color="000000")
        for col in ws.iter_cols(min_row=2, max_col=5, max_row=l+1):
            min = 2007
            if flag:
                j = 0
                for cell in col:
                    cell.value = years[j]
                    cell.border = Border(top=thins, bottom=thins, left=thins, right=thins)
                    j += 1
                flag = False
            else:
                for cell in col:
                    cell.value = list_years[i][min]
                    cell.border = Border(top=thins, bottom=thins, left=thins, right=thins)
                    min += 1
                i += 1
        for col in ws.columns:
            length = max(len(str(cell.value)) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = length + 2
        self.file.save('report.xlsx')


def clean_string(string):
    """очищает строку от спец символов
    Args:
        string(str): строка
    Returns:
        str: строка без спецсимволов
    """
    return ' '.join(re.sub(r"<[^>]+>", '', string).split())


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


def csv_filer(reader):
    """очищает каждую строку файла от спец символов
        Args:
            reader(list): список строк файла
        Returns:
            list: очищенный список строк файла
        """
    all_vac = [x for x in reader if '' not in x and len(x) == len(reader[0])]
    vac = [[clean_string(y) for y in x] for x in all_vac]
    return vac


def read_csv_year(args, q):
    folder = args[0]
    name = args[1]
    prof = args[2]
    header, vac = csv_reader(f"{folder}/{name}.csv")
    vac = csv_filer(vac)
    dict_naming = {}
    for i in range(len(header)):
        dict_naming[header[i]] = i
    salary_dynamic = {}
    count_dynamic = {}
    salary_prof_dynamic = {}
    prof_count = {}
    for item in vac:
        year = int(item[dict_naming['published_at']].split('-')[0])
        if year not in count_dynamic:
            count_dynamic[year] = 0
        count_dynamic[year] += 1
        for i in range(len(item)):
            if header[i] == 'salary_from':
                salary = (float(item[i]) + float(item[i + 1])) / 2
                if item[dict_naming['salary_currency']] != 'RUR':
                    salary *= currency_to_rub[item[dict_naming['salary_currency']]]
                if year not in salary_dynamic:
                    salary_dynamic[year] = []
                salary_dynamic[year].append(int(salary))
                if year not in salary_prof_dynamic:
                    salary_prof_dynamic[year] = []
                if prof in item[0]: salary_prof_dynamic[year].append(int(salary))
                if year not in prof_count:
                    prof_count[year] = 0
                if prof in item[0]: prof_count[year] += 1
    for key in salary_dynamic:
        salary_dynamic[key] = sum(salary_dynamic[key]) // len(salary_dynamic[key])
    for key in salary_prof_dynamic:
        salary_prof_dynamic[key] = sum(salary_prof_dynamic[key]) // max(len(salary_prof_dynamic[key]), 1)
    q.put([salary_dynamic, count_dynamic, salary_prof_dynamic, prof_count])


currency_to_rub = {
    "AZN": 35.68,
    "BYR": 23.91,
    "EUR": 59.90,
    "GEL": 21.74,
    "KGS": 0.76,
    "KZT": 0.13,
    "RUR": 1,
    "UAH": 1.64,
    "USD": 60.66,
    "UZS": 0.0055,
}




if __name__ == '__main__':
    folder = input('Введите название папки с файлами: ')
    prof = input('Введите название профессии: ')
    salary_dynamic = {}
    count_dynamic = {}
    salary_prof_dynamic = {}
    prof_count = {}
    path = Path(folder)
    years_count = len(list(path.iterdir()))
    start_time = time.time()
    years = []
    for i in range(0, years_count):
        years.append([folder, f"{2007 + i}", prof])
    q = Queue()
    x = []
    for year in years:
        p = Process(target=read_csv_year, args=(year, q))
        x.append(p)
        p.start()

    for i in range(0, years_count):
        p = x[i]
        p.join()
        data = q.get()
        year = list(data[0].keys())[0]
        salary_dynamic[year] = data[0][year]
        count_dynamic[year] = data[1][year]
        salary_prof_dynamic[year] = data[2][year]
        prof_count[year] = data[3][year]
    print('Динамика уровня зарплат по годам:', salary_dynamic)
    print('Динамика количества вакансий по годам:', count_dynamic)
    print('Динамика уровня зарплат по годам для выбранной профессии:', salary_prof_dynamic)
    print('Динамика количества вакансий по годам для выбранной профессии:', prof_count)

    report = Report()
    report.generate_excel([salary_dynamic, salary_prof_dynamic, count_dynamic, prof_count])
    print("Время работы: %s seconds" % round(time.time() - start_time, 4))




