#!/usr/bin/env python3
"""
This script calls an asynchronous function n times
"""
import asyncio
from typing import List

task_wait_random = __import__('3-tasks').task_wait_random


async def task_wait_n(n: int, max_delay: int) -> List[float]:
    """
    This function calls task_wait_random n times with the specified max_delay
    returns: list of all the delays (float values)
    """

    delay = await asyncio.gather(
        *(task_wait_random(max_delay) for _ in range(n))
        )
    delay = sorted(delay)
    return delay
