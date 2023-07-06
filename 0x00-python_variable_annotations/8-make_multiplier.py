#!/usr/bin/env python3
"""
This script contains annotated python function that takes
 a float multiplier as argument and
 returns a function that multiplies a float by multiplier.
"""
from typing import Callable


def make_multiplier(multiplier: float) -> Callable[[float], float]:
    """ This function returns another function. """

    def func(n: float) -> float:
        return float(n * multiplier)
    return func
