#!/usr/bin/env python3
"""
This script contains annotated python function which takes
a list input_list of floats as argument and returns their sum as a float
"""
from typing import List


def sum_list(input_list: List[float]) -> float:
    """ This function takes an input list of float and return their sum."""
    return sum(input_list)
