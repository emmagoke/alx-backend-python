#!/usr/bin/env python3
"""
This script contains a function that measures the running time of
an async function.
"""
import asyncio
import time

wait_n = __import__('1-concurrent_coroutines').wait_n


def measure_time(n: int, max_delay: int) -> float:
    """ This function measures the total execution time for wait_n. """

    start = time.perf_counter()
    asyncio.run(wait_n(n, max_delay))

    total_time = time.perf_counter() - start
    return total_time / n
