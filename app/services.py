import math
from typing import List


def calculate_p95_latency(latencies: List[int]) -> float:
    """
    Calculates the 95th percentile for a list of latency values.

    Args:
        latencies: A list of integers representing latency in ms.

    Returns:
        The 95th percentile value as a float. Returns 0.0 if the list is empty.
    """
    if not latencies:
        return 0.0

    latencies.sort()
    index = math.ceil(0.95 * len(latencies)) - 1
    return float(latencies[index])
