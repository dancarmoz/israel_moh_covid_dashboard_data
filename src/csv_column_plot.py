import csv

from datetime import datetime

from . import date_utils
from .plot import Plot


class CsvColumnPlot(Plot):

    def __init__(self, path, column, should_skip_first_line=False, start_date=datetime(2020, 3, 1)):
        self._label = column
        reader = csv.reader(open(path))

        if should_skip_first_line:
            next(reader)

        column_index = next(reader).index(column)

        self.dates = []
        self.values = []

        for row in reader:
            # Skip old dates
            date = date_utils.str_to_datetime(row[0])
            if date < start_date:
                continue

            # Record date
            self.dates.append(date_utils.datetime_to_num(date))

            # Record value
            self.values.append(float(row[column_index]))

    def x(self):
        return self.dates

    def y(self):
        return self.values

    def label(self):
        return self._label
