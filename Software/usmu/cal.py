import numpy as np
from collections import namedtuple
from numpy.polynomial import Polynomial

LinFitResult = namedtuple("LinFitResult", ["slope", "intercept"])

class LinFitter:
    def __init__(self):
        self.x = []
        self.y = []

    def add_point(self, x: float, y:float):
        self.x.append(x)
        self.y.append(y)

    def fit(self):
        p = Polynomial.fit(self.x, self.y, 1)
        intercept, slope = p.convert().coef
        return LinFitResult(slope=slope, intercept=intercept)
