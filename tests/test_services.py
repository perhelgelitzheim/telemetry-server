from app.services import calculate_p95_latency


def test_calculate_p95_latency_basic():
    """
    Test with a simple list of 100 values where the p95 is obvious.
    """
    latencies = list(range(1, 101))
    assert calculate_p95_latency(latencies) == 95


def test_calculate_p95_latency_interpolation():
    """
    Test with a list of 20 values using nearest-rank.
    The 95th percentile of [1..20] is 19.
    """
    latencies = list(range(1, 21))
    assert calculate_p95_latency(latencies) == 19


def test_calculate_p95_latency_empty_list():
    """
    Test that an empty list of latencies returns 0.
    """
    assert calculate_p95_latency([]) == 0


def test_calculate_p95_latency_single_value():
    """
    Test that a list with a single latency value returns that value.
    """
    assert calculate_p95_latency([150]) == 150


def test_calculate_p95_latency_with_duplicates():
    """
    Test with a list containing duplicate values.
    """
    latencies = [
        10,
        20,
        30,
        40,
        50,
        50,
        50,
        50,
        50,
        50,
        50,
        50,
        50,
        50,
        50,
        50,
        50,
        50,
        50,
        1000,
    ]
    assert calculate_p95_latency(latencies) == 50
