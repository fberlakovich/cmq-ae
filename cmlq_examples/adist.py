import numpy as np

__rewrite__ = False

import contextlib
import inspect


@contextlib.contextmanager
def disabled_cmlq():
    global __rewrite__
    before = __rewrite__
    __rewrite__ = False
    yield
    __rewrite__ = before


counter = 0


def report_error(left, result, correct_result, wrong_result, operator):
    global counter
    if not np.allclose(correct_result, result):
        print(f"+++++++++++++++ {operator} DOES NOT MATCH (Iteration {counter}) +++++++++++++++")
        print("Left:", left)
        print()
        print("Right:", wrong_result)
        print()
        print("Correct Result:", correct_result)
        print()
        print("Wrong Result:", result)
        print("Line:", inspect.currentframe().f_back.f_back.f_lineno)

def check_power_result(left, right, result):
    global counter
    counter += 1
    with disabled_cmlq():
        correct_result = left ** right
        report_error(left, result, correct_result, right, "power")


def check_subtract_result(left, right, result):
    global counter
    with disabled_cmlq():
        correct_result = left - right
        report_error(left, result, correct_result, right, "subtract")


def check_div_result(left, right, result):
    global counter
    with disabled_cmlq():
        correct_result = left / right
        report_error(left, result, correct_result, right, "div")


def arc_distance(N):
    from numpy.random import default_rng
    rng = default_rng(42)
    theta_1, phi_1, theta_2, phi_2 = rng.random((N,)), rng.random((N,)), rng.random((N,)), rng.random((N,))

    """
    Calculates the pairwise arc distance between all points in vector a and b.
    """
    subtraction = theta_2 - theta_1
    check_subtract_result(theta_2, theta_1, subtraction)
    div_result = (subtraction) / 2
    check_div_result(subtraction, 2, div_result)
    left = np.sin(div_result)
    right = 2
    power_result1 = left ** right
    check_power_result(left, right, power_result1)
    subtraction = (phi_2 - phi_1)
    check_subtract_result(phi_2, phi_1, subtraction)
    div_result = subtraction / 2
    check_div_result(subtraction, 2, div_result)
    left = np.sin(div_result)
    power_result2 = left ** right
    check_power_result(left, right, power_result2)
    temp = power_result1 + np.cos(theta_1) * np.cos(theta_2) * power_result2
    distance_matrix = 2 * (np.arctan2(np.sqrt(temp), np.sqrt(1 - temp)))
    return distance_matrix
