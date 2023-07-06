#!/usr/bin/env python3
"""
This script contains annotated python function which takes
takes a list mxd_lst of integers and floats and returns their sum as a float.
"""
from typing import Union


def sum_mixed_list(mxd_list: Union[int, float]) -> float:
    """ This function takes a mix list of an int and a flaot, returns float"""
    return sum(mxd_list)
