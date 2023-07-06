#!/usr/bin/env python3
"""
This script contains annotated python function that takes
 a iterable and returns a the iterable and length.
"""
from typing import Sequence, List, Tuple, Iterable


def element_length(lst: Iterable[Sequence]) -> List[Tuple[Sequence, int]]:
    """ This function take an iterable"""
    return [(i, len(i)) for i in lst]
