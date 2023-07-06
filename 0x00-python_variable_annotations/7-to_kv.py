#!/usr/bin/env python3
"""
This script contains annotated python function that takes
a string k and an int OR float v as arguments and returns a tuple.
The first element of the tuple is the string k.
The second element is the square of the int/float v
and we be annotated as a float.
"""
from typing import Union, Tuple


def to_kv(k: str, v: Union[int, float]) -> Tuple[str, float]:
    """ This function takes a str and a int or float and returns a tuple"""
    v_sq = v ** 2
    return (k, v_sq)
