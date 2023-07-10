#!/usr/bin/env python3
"""
This script calls an asynchronous function n times
"""
import asyncio
from typing import List

wait_random = __import__('0-basic_async_syntax').wait_random


async def wait_n(n: int, max_delay: int) -> List[float]:
    """
    This function calls wait_random n times with the specified max_delay
    returns: list of all the delays (float values)
    """

    delay = await asyncio.gather(*(wait_random(max_delay) for _ in range(n)))
    delay.sort()
    return delay
