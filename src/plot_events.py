from datetime import datetime, timedelta


class PlotEvents:
    def __init__(self, plt):
        self.plt = plt

    def vertical_span(self, date, date_end, color):
        self.plt.axvspan(date, date_end, facecolor=color, alpha=0.5)
        self.plt.text(date, 150, '', rotation=90)

    def vertical_line(self, date, text, color):
        self.plt.axvline(x=date, color=color, alpha=0.5)
        bottom, top = self.plt.ylim()
        self.plt.text(date, bottom + top / 50, text, rotation=90)

    def draw(self, start_date):
        # Event example
        # self.vertical_line(datetime(2021, 1, 1), 'Event', 'g')

        partial_lockdown = '#f0cccc'
        full_lockdown = '#f08888'

        # Second lockdown
        if start_date < datetime(2020, 9, 18):
            self.vertical_span(datetime(2020, 9, 18), datetime(2020, 9, 25), partial_lockdown)
            self.vertical_span(datetime(2020, 9, 25), datetime(2020, 10, 13), full_lockdown)
            self.vertical_span(datetime(2020, 10, 13), datetime(2020, 10, 17), partial_lockdown)

        # Third lockdown
        self.vertical_span(datetime(2020, 12, 27), datetime(2021, 1, 8), partial_lockdown)
        self.vertical_span(datetime(2021, 1, 8), datetime(2021, 2, 4), full_lockdown)
