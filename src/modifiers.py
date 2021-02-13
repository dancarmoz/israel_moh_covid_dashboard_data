import numpy
import itertools

from . import date_utils


class Modifier:
    def __init__(self, plot):
        self.plot = plot

    def x(self):
        return self.plot.x()

    def y(self):
        return self.plot.y()

    def label(self):
        return self.plot.label()


class Multiply(Modifier):
    def __init__(self, factor, plot):
        super().__init__(plot)
        self._y = [v * factor for v in self.plot.y()]

    def y(self):
        return self._y


class Average(Modifier):
    def __init__(self, window, plot):
        super().__init__(plot)
        self._x = plot.x()[window-1:]
        self._y = self.moving_average(plot.y(), window)

    @staticmethod
    def moving_average(x, w):
        return numpy.convolve(x, numpy.ones(w), 'valid') / w

    def x(self):
        return self._x

    def y(self):
        return self._y


class ChopFromEnd(Modifier):
    def __init__(self, chop, plot):
        super().__init__(plot)
        self._x = plot.x()[:-chop]
        self._y = plot.y()[:-chop]

    def x(self):
        return self._x

    def y(self):
        return self._y


class ChopToDate(Modifier):
    def __init__(self, date, plot):
        super().__init__(plot)

        chop = 0
        for chop, x in enumerate(plot.x()):
            if date <= date_utils.num_to_datetime(x):
                break

        self._x = plot.x()[chop:]
        self._y = plot.y()[chop:]

    def x(self):
        return self._x

    def y(self):
        return self._y


class Group(Modifier):
    def __init__(self, label, plots):
        super().__init__(plots[0])
        zipped = itertools.zip_longest(*(plot.y() for plot in plots))
        self._y = [sum(zip) for zip in zipped]
        self._label = label

    def y(self):
        return self._y

    def label(self):
        return self._label
