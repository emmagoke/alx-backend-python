#!/usr/bin/env python3
"""
THis script contains an asynchronous function
"""
import asyncio
import random


async def wait_random(max_delay: int = 10) -> float:
    """ This function waits for a random delay between 0 and max_delay. """

    delay = random.uniform(0, max_delay + 1)
    await asyncio.sleep(delay)
    return delay
