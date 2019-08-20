from __future__ import print_function
from ortools.sat.python import cp_model
from tabulate import tabulate

import orm


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, decision_var, num_shifts, num_timeslots, num_sols, shifts, employees):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._shifts = shifts
        self._employees = employees
        self._decision_var = decision_var
        self._num_employees = self._employees.num_employees()
        self._num_days = self._shifts.num_days()
        self._num_timeslots = num_timeslots
        self._num_shifts = num_shifts
        self._solutions = range(num_sols-1)
        self._solution_count = 0

    def on_solution_callback(self):
        """Loop through vars and build roster based on current solution """
        if self._solution_count not in self._solutions:
            self.StopSearch()
        print(f'Solution {self._solution_count}')
        roster = []
        for t in range(self._num_timeslots):
            row = [self._shifts.get_timeslots()[t]]
            for d in range(self._num_days):
                day = []
                for s in range(self._num_shifts):
                    for e in range(self._num_employees):
                        if self.Value(self._decision_var[(e, d, t, s)]):
                            day.append(self._employees.get_name(e))
                row.append(day)
            roster.append(row)

        roster_headers = list(self._shifts.get_days())
        roster_headers.insert(0, 'Shift Time')
        print(tabulate(roster, roster_headers, tablefmt='grid'))
        print()
        self._solution_count += 1

    def solution_count(self):
        return self._solution_count


def main():
    shift_data = orm.Shifts('files/shifts.csv')
    employee_data = orm.Employees('files/employees.csv')

    num_days = shift_data.num_days()
    num_employees = employee_data.num_employees()
    num_timeslots = 3  # A timeslot is considered the actual time an employee is working, i.e. 5:00AM to 1:30PM
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
    # Variable is binary, equaling 1 if (e)mployee is working on (d)ay, during (t)imeslot and in (s)hift, otherwise 0
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
        model.Add(sum(decision_var[(e, d, t, s)] for d in days for t in timeslots for s in shifts) <= 5)

    # Employees work 1 shift per day at most
    for e in employees:
        for d in days:
            model.Add(sum(decision_var[(e, d, t, s)] for t in timeslots for s in shifts) <= 1)

    # 10 hours break between shifts. Should ideally be in a loop to allow for a dynamic number of shifts per day
    for d in days[:-1]:
        for e in employees:
            model.Add(sum(decision_var[e, d, 1, s] for s in shifts) +
                      sum(decision_var[e, d+1, 0, s] for s in shifts) <= 1)
            model.Add(sum(decision_var[e, d, 2, s] for s in shifts) +
                      sum(decision_var[e, d+1, 1, s] for s in shifts) +
                      sum(decision_var[e, d+1, 0, s] for s in shifts) <= 1)

    # No more than 5 working days in a row
    for d in days[:-5]:
        for e in employees:
            model.Add(sum(sum(decision_var[e, d + x, t, s] for t in timeslots for s in shifts) for x in range(5)) <= 5)

    # No more than 5 days working in any 7 day rolling window
    for d in days[:-7]:
        for e in employees:
            model.Add(sum(sum(decision_var[e, d + x, t, s] for t in timeslots for s in shifts) for x in range(7)) <= 5)

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

    solver = cp_model.CpSolver()
    solution_printer = SolutionPrinter(decision_var, num_employees, num_timeslots, 2, shift_data, employee_data)
    # Since an objective function hasn't been implemented, ideally to minimize start time variance or consecutive days
    # off, there is no 'best' solution. As a result, all solutions are found, stopping after the specified number.
    solver.SearchForAllSolutions(model, solution_printer)

    print()
    print('Statistics')
    print('  - conflicts       : %i' % solver.NumConflicts())
    print('  - branches        : %i' % solver.NumBranches())
    print('  - wall time       : %f s' % solver.WallTime())
    print('  - solutions found : %i' % solution_printer.solution_count())


if __name__ == '__main__':
    main()
