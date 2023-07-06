#!/usr/bin/env python3
"""
This script contains annotated python function that takes
 a iterable and returns a the iterable or None. (Example of Duck typing).
"""
from typing import Any, Sequence, Union


# The types of the elements of the input are not know
def safe_first_element(lst: Sequence[Any]) -> Union[Any, None]:
    """ This function takes any form of Sequence
    and returns any type or None"""
    if lst:
        return lst[0]
    else:
        return None
