#!/usr/bin/env python3
"""
This script contains a function that measures the running time of an
asynchronous function.
"""
import asyncio
import time

async_comprehension = __import__('1-async_comprehension').async_comprehension


async def measure_runtime() -> float:
    """
    This coroutine will execute async_comprehension four times in parallel
    and  measure the total runtime and return it.
    """

    start = time.perf_counter()
    await asyncio.gather(*(async_comprehension() for _ in range(4)))
    total_time = time.perf_counter() - start

    return total_time
