import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from .plot_events import PlotEvents
from .date_utils import num_to_datetime


class PlotViewer:
    def __init__(self):
        fig, ax = plt.subplots(figsize=(23, 10))
        self.fig = fig
        self.ax = ax
        self.plots = []

    def add_plot(self, plot):
        self.plots.append(plot)

    def add_plots(self, plots):
        self.plots.extend(plots)

    def show(self):
        # Draw plots
        for plot in self.plots:
            alpha = 0.8
            x, y = plot.x(), plot.y()
            self.ax.scatter(x, y, label=plot.label(), alpha=alpha)
            line, = self.ax.plot(x, y, 'o--', alpha=alpha)
            self.ax.text(x[-1] + 1, y[-1], plot.label(), fontsize=11, color=line.get_color())

        # Draw x axis dates
        x_axis_size = len(self.plots[-1].x())
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, x_axis_size // 60)))

        self.ax.legend(loc='upper left')
        self.ax.grid(True)

        self.fig.autofmt_xdate()

        # Draw events
        start_date = num_to_datetime(min(plot.x()[0] for plot in self.plots))
        PlotEvents(plt).draw(start_date=start_date)

        plt.show()
