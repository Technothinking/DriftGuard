import numpy as np

def calculate_psi(expected, actual, bins=10):
    expected_percents, _ = np.histogram(expected, bins=bins)
    actual_percents, _ = np.histogram(actual, bins=bins)

    expected_percents = expected_percents / len(expected)
    actual_percents = actual_percents / len(actual)

    psi = np.sum(
        (expected_percents - actual_percents) *
        np.log((expected_percents + 1e-6) / (actual_percents + 1e-6))
    )

    return psi