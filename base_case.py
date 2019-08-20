from __future__ import print_function
from ortools.sat.python import cp_model
import csv
from datetime import datetime
import json
from tabulate import tabulate


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, decision_var, num_employees, num_days, num_shifts, num_timeslots, num_sols):
        cp_model.CpSolverSolutionCallback.__init__(self)
        print(num_employees, num_days, num_timeslots, num_shifts, num_sols)
        self._decision_var = decision_var
        self._num_employees = num_employees
        self._num_days = num_days
        self._num_timeslots = num_timeslots
        self._num_shifts = num_shifts
        self._solutions = range(num_sols + 1)
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
                            if self.Value(self._decision_var[(e, d, t, s)]):
                                day.append((s, e))
                    row.append(day)
                roster.append(row)

            # print('here')
            roster_headers = list(range(self._num_days))
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
    num_employees = 13
    num_timeslots = 3
    num_shifts = 3  # Number of shifts per timeslot, i.e. 3 people can work at the same time.

    days = range(num_days)
    employees = range(num_employees)
    timeslots = range(num_timeslots)
    shifts = range(num_shifts)

    model = cp_model.CpModel()
    decision_var = {}

    ###############################
    # Defining decision variables #
    ###############################
    for e in employees:
        for d in days:
            for t in timeslots:
                for s in shifts:
                    decision_var[(e, d, t, s)] = model.NewBoolVar(f'Employee: {e}, Day: {d}, Timeslot: {t}, Shift: {s}')

    ################################
    # Constraints                  #
    ################################

    # Ensuring that all hours are covered
    for d in days:
        for t in timeslots:
            for s in shifts:
                model.Add(sum(decision_var[(e, d, t, s)] for e in employees) == 1)

    # No employee works more than 5 days a week.
    # This currently just works off the given list being a week long.
    # # This does NOT constrain to a rolling 7 day window.
    for e in employees:
        model.Add(sum(decision_var[(e, d, t, s)] for d in days for t in timeslots for s in shifts ) <= 5)

    # Employees work 1 shift per day at most
    for e in employees:
        for d in days:
            model.Add(sum(decision_var[(e, d, t, s)] for t in timeslots for s in shifts) <= 1)

    # 10 hours break between shifts
    for d in days[:-1]:
        for e in employees:
            model.Add(sum(decision_var[e, d, 1, s] for s in shifts) + sum(decision_var[e, d+1, 0, s] for s in shifts) <= 1)
            model.Add(sum(decision_var[e, d, 2, s] for s in shifts) + sum(decision_var[e, d+1, 1, s] for s in shifts) + sum(decision_var[e, d+1, 0, s] for s in shifts) <= 1)

    # Evenly spread shifts across employees.
    # Naturally, all employees want as many shifts as they can,
    # so the min number of shifts for each, is the floor of the TOTAL shifts divided by the employees.
    # Taking the floor means, that there will be at most a variation of 1 shift between any two
    # employees, meaning the max number is just the min + 1
    min_shifts = (num_shifts * num_timeslots * num_days) // num_employees
    max_shifts = min_shifts + 1
    for e in employees:
        num_working_shifts = sum(decision_var[(e, d, t, s)] for d in days for s in shifts for t in shifts)
        model.Add(min_shifts <= num_working_shifts)
        model.Add(num_working_shifts <= max_shifts)

    # Objective function
    # model.Minimize(sum(s[(d, e, t)] for d in days for e in employees for t in shifts))
    solver = cp_model.CpSolver()
    # solver.parameters.linearization_level = 0
    solution_printer = SolutionPrinter(decision_var, num_employees, num_days, num_shifts, num_timeslots, 2)
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

