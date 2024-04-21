from datetime import datetime
import os
import contextlib
import inspect
import numpy as np

from collections import defaultdict

counters = defaultdict(int)

@contextlib.contextmanager
def disabled_cmlq():
    before = os.environ["CMLQ_REWRITE"] if "CMLQ_REWRITE" in os.environ else None
    if before:
        del os.environ["CMLQ_REWRITE"]
    yield
    if before is not None:
        os.environ["CMLQ_REWRITE"] = before


def report_error(left, right, opt_result, correct_result, operator):
    global counters
    counter = counters[operator]
    if not np.allclose(correct_result, opt_result):
        print(f"+++++++++++++++ {operator} DOES NOT MATCH (Iteration {counter}) +++++++++++++++")
        print("Left Type:", left.dtype)
        print("Left:", left)
        print()
        print("Right Type:", right.dtype)
        print("Right:", right)
        print()
        print("Correct Result:", correct_result)
        print()
        print("Wrong Result:", opt_result)
        print("Line:", inspect.currentframe().f_back.f_back.f_lineno)
        raise(Exception)


def check_div_result(left, right, opt_result):
    global counters
    operator = "div"
    counters[operator] += 1
    with disabled_cmlq():
        correct_result = left / right
        report_error(left, right, opt_result, correct_result, operator)

def check_add_result(left, right, opt_result):
    global counters
    operator = "add"
    counters[operator] += 1
    with disabled_cmlq():
        correct_result = left + right
        report_error(left, right, opt_result, correct_result, operator)

def check_sub_result(left, right, opt_result):
    global counters
    operator = "minus"
    counters[operator] += 1
    with disabled_cmlq():
        correct_result = left - right
        report_error(left, right, opt_result, correct_result, operator)

def check_mul_result(left, right, opt_result):
    global counters
    operator = "multiply"
    if "CMLQ_REWRITE" not in os.environ or os.environ["CMLQ_REWRITE"] == "0":
        return
    counters[operator] += 1
    with disabled_cmlq():
        correct_result = left * right
        report_error(left, right, opt_result, correct_result, operator)