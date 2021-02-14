from . import date_utils
from .modifiers import Multiply


def normalize_plots_to_date(date, plots):
    indexes = []
    for plot in plots:
        for i, x in enumerate(plot.x()):
            if date_utils.is_same_day(x, date):
                indexes.append(i)
                break

    factors = []
    for i, plot in enumerate(plots):
        factors.append(plot.y()[indexes[i]])

    first = factors[0]
    factors = [first / f for f in factors]

    return [Multiply(f, plots[i]) for i, f in enumerate(factors)]
