#!/usr/bin/env python3
"""
This script contain an asynchronous comprehension function.
"""
from typing import Iterator

async_generator = __import__('0-async_generator').async_generator


async def async_comprehension() -> Iterator[float]:
    """
    The coroutine will collect 10 random numbers using an async
    comprehensing over async_generator,
    then return the 10 random numbers.
    """

    result = [i async for i in async_generator()]
    return result
