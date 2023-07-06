#!/usr/bin/env python3
"""
This script contains an Annoted function that takes
an tuple and int and returns a List
"""
from typing import Any, Tuple, List


def zoom_array(lst: Tuple, factor: int = 2) -> List:
    """ This function takes a tuple and an int. """
    zoomed_in: List[Any] = [
        item for item in lst
        for i in range(factor)
    ]
    return zoomed_in


array = (12, 72, 91)

zoom_2x = zoom_array(array)

zoom_3x = zoom_array(array, 3)
