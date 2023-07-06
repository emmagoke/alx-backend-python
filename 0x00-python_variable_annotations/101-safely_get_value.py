#!/usr/bin/env python3
"""
This script contains annotated python function that takes
 a iterable and returns a the iterable or None. (Example of Duck typing).
 """
from typing import Any, Mapping, Union, TypeVar

TV = TypeVar('T')
_def = Union[TV, None]
ret = Union[Any, TV]


def safely_get_value(dct: Mapping, key: Any, default: _def = None) -> ret:
    """ This function takes in a dict, any type, and any type"""
    if key in dct:
        return dct[key]
    else:
        return default
