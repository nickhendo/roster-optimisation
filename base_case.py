from __future__ import print_function
from ortools.sat.python import cp_model
import csv
from datetime import datetime
import json
from tabulate import tabulate


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, shifts, num_employees, num_days, num_shifts, sols, employee_names, shift_data):
        cp_model.CpSolverSolutionCallback.__init__(self)
        print(num_employees, num_days, num_shifts, sols)
        self._shifts = shifts
        self._num_employees = num_employees
        self._num_days = num_days
        self._num_shifts = num_shifts
        self._solutions = set(sols)
        self._solution_count = 0
        self._employee_names = employee_names
        self._shift_data = shift_data

    def on_solution_callback(self):
        self._solution_count += 1
        if self._solution_count in self._solutions:
            print(f'Solution {self._solution_count}')
            roster_headers = list(sorted(set(datetime.strftime(shift["Date"], '%d/%m/%Y') for shift in self._shift_data)))
            roster_headers.insert(0, 'Shift Time')
            roster = []

            for t in range(self._num_shifts):
                shifts = []
                for d in range(self._num_days):
                    employees = []
                    for e in range(self._num_employees):
                        if self.Value(self._shifts[(d, e, t)]):
                            employees.append(self._employee_names[e])
                    shifts.append(employees)
                if f'{self._shift_data[d * t]["Start"]} to {self._shift_data[d * t]["End"]}' not in shifts:
                    shifts.insert(0, f'{self._shift_data[d * t]["Start"]} to {self._shift_data[d * t]["End"]}')
                roster.append(shifts)

            print(tabulate(roster, roster_headers, tablefmt='grid'))
            print()

        else:
            self.StopSearch()

    def solution_count(self):
        return self._solution_count


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

    # print(shifts)
    # print(json.dumps(employees, indent=4))
    return shifts, employees

def main():
    shift_data, employee_data = import_data()
    days = list(set(datetime.strftime(shift["Date"], '%d/%m/%Y') for shift in shift_data))
    employee_names = [f"{employee['First Name']} {employee['Last Name']}" for employee in employee_data]
    days = range(len(days))
    employees = range(len(employee_data))
    shifts = range(8)
    model = cp_model.CpModel()
    s = {}
    # Defining decision variable
    for d in days:
        for e in employees:
            for t in shifts:
                s[(d, e, t)] = model.NewBoolVar(f'Day: {d}, Employee: {e}, Shift: {t}')

    # Ensuring that all hours are covered
    for d in days:
        for t in shifts:
            model.Add(sum(s[(d, e, t)] for e in employees) == 1)

    # No employee works more than 5 days a week
    for e in employees:
        model.Add(sum(s[(d, e, t)] for d in days for t in shifts) <= 5)

    # Employees work 1 shift per day at most
    for e in employees:
        for d in days:
            model.Add(sum(s[(d, e, t)] for t in shifts) <= 1)

    # Evenly spread shifts across employees
    min_shifts = (len(shifts) * len(days)) // len(employees)
    max_shifts = min_shifts + 1
    for e in employees:
        num_shifts = sum(s[(d, e, t)] for d in days for t in shifts)
        model.Add(min_shifts <= num_shifts)
        model.Add(num_shifts <= max_shifts)

    # Objective function
    # model.Minimize(sum(s[(d, e, t)] for d in days for e in employees for t in shifts))
    solver = cp_model.CpSolver()
    solver.parameters.linearization_level = 0
    solution_printer = SolutionPrinter(s, len(employees), len(days), len(shifts), range(2), employee_names, shift_data)
    solver.SearchForAllSolutions(model, solution_printer)
    #
    print()
    print('Statistics')
    print('  - conflicts       : %i' % solver.NumConflicts())
    print('  - branches        : %i' % solver.NumBranches())
    print('  - wall time       : %f s' % solver.WallTime())
    print('  - solutions found : %i' % solution_printer.solution_count())
    # week_grid = []
    # for t in shifts:
    #     times = []
    #     for d in days:
    #         workers = []
    #         for e in employees:
    #             if solver.Value(s[(d, e, t)]) == 1:
    #                 workers.append(e)
    #         times.append(workers)
    #     week_grid.append(times)
    # headers = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    # print(tabulate(week_grid, headers=headers, tablefmt='grid'))
    # print(f'Objective value: {solver.ObjectiveValue()}\nWall time: {solver.WallTime()}')


if __name__ == '__main__':
    main()

