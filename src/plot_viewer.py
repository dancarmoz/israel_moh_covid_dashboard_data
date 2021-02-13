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
        # Draw x axis dates
        x_axis_size = max(len(plot.x()) for plot in self.plots)
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, x_axis_size // 30)))

        self.ax.legend(loc='upper left')
        self.ax.grid(True)

        self.fig.autofmt_xdate()

        # Draw events
        start_date = num_to_datetime(min(plot.x()[0] for plot in self.plots))
        PlotEvents(plt).draw(start_date=start_date)

        # Draw plots
        alpha = 0.8
        for plot in self.plots:
            ax = self.ax
            if plot.separate_y_axis():
                ax = ax.twinx()
            x, y = plot.x(), plot.y()
            ax.scatter(x, y, label=plot.label(), alpha=alpha)
            line, = ax.plot(x, y, 'o--', alpha=alpha)
            ax.text(x[-1] + 1, y[-1], plot.label(), fontsize=11, color=line.get_color())

        plt.show()
