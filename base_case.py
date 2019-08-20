from __future__ import print_function
from ortools.sat.python import cp_model
import csv
from datetime import datetime
import json
from tabulate import tabulate


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, X, num_employees, num_days, num_shifts, num_timeslots, sols):
        cp_model.CpSolverSolutionCallback.__init__(self)
        print(num_employees, num_days, num_shifts, sols)
        self._X = X
        self._num_employees = num_employees
        self._num_days = num_days
        self._num_timeslots = num_timeslots
        self._num_shifts = num_shifts
        self._solutions = set(sols)
        self._solution_count = 0

    def on_solution_callback(self):
        self._solution_count += 1
        if self._solution_count in self._solutions:
            print(f'Solution {self._solution_count}')
            roster = []
            for t in range(self._num_timeslots):
                row = [t]
                for d in range(self._num_days):
                    day = []
                    for s in range(self._num_shifts):
                        for e in range(self._num_employees):
                            if self.Value(self._X(e, d, s, t)):
                                day.append((s, e))
                roster.append(row)


            roster_headers = list(sorted(set(datetime.strftime(shift["Date"], '%d/%m/%Y') for shift in self._shift_data)))
            roster_headers.insert(0, 'Shift Time')

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
    num_days = 7
    num_employees = 14
    num_timeslots = 3
    num_shifts = 3  # Number of shifts per timeslot, i.e. 3 people can work at the same time.

    days = range(num_days)
    employees = range(num_employees)
    timeslots = range(num_timeslots)
    shifts = range(num_shifts)

    model = cp_model.CpModel()
    X = {}

    ###############################
    # Defining decision variables #
    ###############################
    for e in employees:
        for d in days:
            for t in timeslots:
                for s in shifts:
                    X[(e, d, t, s)] = model.NewBoolVar(f'Employee: {e}, Day: {d}, Timeslot: {t}, Shift: {s}')

    ################################
    # Constraints                  #
    ################################

    # Ensuring that all hours are covered
    for d in days:
        for t in timeslots:
            model.Add(sum(X[(e, d, t, s)] for e in employees for s in shifts) == 1)

    # No employee works more than 5 days a week.
    # This currently just works off the given list being a week long.
    # This does NOT constrain to a rolling 7 day window.
    for e in employees:
        model.Add(sum(X[(e, d, s, t)] for d in days for s in shifts for t in timeslots) <= 5)

    # Employees work 1 shift per day at most
    for e in employees:
        for d in days:
            model.Add(sum(X[(e, d, s, t)] for s in shifts for t in timeslots) <= 1)

    # 10 hours break between shifts
    for d in days[:-1]:  # Don't worry about last day in schedule
        for e in employees:
            for s in shifts[1:]:
                model.Add(sum(X[e, d, s, t] for t in timeslots) > sum(X[e, d+1, s-1, t] for t in timeslots))

    # Evenly spread shifts across employees.
    # Naturally, all employees want as many shifts as they can,
    # so the min number of shifts for each, is the floor of the TOTAL shifts divided by the employees.
    # Taking the floor means, that there will be at most a variation of 1 shift between any two
    # employees, meaning the max number is just the min + 1
    min_shifts = (num_shifts* num_timeslots * num_days) // num_employees
    max_shifts = min_shifts + 1
    for e in employees:
        num_shifts = sum(X[(e, d, s, t)] for d in days for s in shifts for t in shifts)
        model.Add(min_shifts <= num_shifts)
        model.Add(num_shifts <= max_shifts)

    # Objective function
    # model.Minimize(sum(s[(d, e, t)] for d in days for e in employees for t in shifts))
    solver = cp_model.CpSolver()
    # solver.parameters.linearization_level = 0
    solution_printer = SolutionPrinter(X, len(employees), num_days, num_shifts, num_timeslots, range(2))
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

