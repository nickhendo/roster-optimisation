import csv
from datetime import datetime
import json


class Shifts:
    def __init__(self, file_path):
        self.load(file_path)

    def load(self, file_path):
        self._file_path = file_path
        self._rows = []
        with open(self._file_path, encoding='utf-8-sig') as csvfile:
            data = csv.DictReader(csvfile, delimiter=',')
            for row in data:
                row["Date_Object"] = datetime.strptime(row["Date"], '%d/%m/%Y').date()
                row["Start_Object"] = datetime.strptime(row["Start"], '%I:%M:%S %p').time()
                row["End_Object"] = datetime.strptime(row["End"], '%I:%M:%S %p').time()
                self._rows.append(row)

    def get_days(self):
        days = []
        for row in sorted(self._rows, key=lambda key: key['Date_Object']):
            if row["Date"] not in days:
                days.append(row["Date"])
        return days

    def num_days(self):
        return len(self.get_days())

    def get_timeslots(self):
        timeslots = []
        for row in self._rows:
            time = (row["Start"], row["End"], row["Start_Object"])
            if time not in timeslots:
                timeslots.append(time)
        return [f"{time[0]} to {time[1]}" for time in sorted(timeslots, key=lambda x: x[2])]


    def __repr__(self):
        return json.dumps([{key: value for key, value in row.items() if 'object' not in key.lower()}
                           for row in self._rows], indent=4)


class Employees:
    def __init__(self, file_path):
        self.load(file_path)

    def load(self, file_path):
        self._file_path = file_path
        self._rows = []
        with open(self._file_path, encoding='utf-8-sig') as csvfile:
            data = csv.DictReader(csvfile, delimiter=',')
            for row in data:
                self._rows.append(row)

    def get_name(self, index):
        name = sorted(self._rows, key=lambda key: key['Last Name'])[index]
        return f'{name["First Name"]} {name["Last Name"]}'

    def num_employees(self):
        return len(self._rows)

    def __repr__(self):
        return json.dumps(self._rows, indent=4)


if __name__ == '__main__':
    pass
