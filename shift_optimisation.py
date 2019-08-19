import csv
import json
from datetime import datetime


def import_data(shifts_file='files/shifts.csv', employees_file='files/employees.csv'):
    shifts = []
    employees = []

    with open(shifts_file, encoding='utf-8-sig') as csvfile:
        employee_shifts = csv.DictReader(csvfile, delimiter=',')
        for shift in employee_shifts:
            shift["Date"] = datetime.strptime(shift["Date"], '%d/%m/%Y').date()
            shift["Start"] = datetime.strptime(shift["Start"], '%I:%M:%S %p').time()
            shift["End"] = datetime.strptime(shift["End"], '%I:%M:%S %p').time()
            shifts.append(shift)

    with open(employees_file, encoding='utf-8-sig') as csvfile:
        employee_names = csv.DictReader(csvfile, delimiter=',')
        for employee in employee_names:
            employees.append(employee)

    print(shifts)
    # print(json.dumps(employees, indent=4))
    return shifts, employees


def main():
    shifts, employees = import_data()
    working_days = {}
    for shift in shifts:
        date = datetime.strftime(shift["Date"], '%d/%m/%Y')
        if date not in working_days.keys():
            working_days[date] = [shift]
        else:
            working_days[date].append(shift)
    print(working_days)

if __name__ == '__main__':
    main()
