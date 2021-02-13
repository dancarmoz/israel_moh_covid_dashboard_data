from abc import ABC, abstractmethod


class Plot(ABC):
    @abstractmethod
    def x(self):
        pass

    @abstractmethod
    def y(self):
        pass

    @abstractmethod
    def label(self):
        pass

    @abstractmethod
    def separate_y_axis(self):
        pass
