import numpy as np

__rewrite__ = False

import contextlib


@contextlib.contextmanager
def disabled_cmlq():
    global __rewrite__
    before = __rewrite__
    __rewrite__ = False
    yield
    __rewrite__ = before


counter = 0


def check_add_result(left, right, result):
    global counter
    counter += 1
    with disabled_cmlq():
        correct_result = left + right
        if not np.allclose(correct_result, result):
            print(f"+++++++++++++++ OPERATION DOES NOT MATCH (Iteration {counter} +++++++++++++++")
            print("Left:", left)
            print()
            print("Right:", right)
            print()
            print("Correct Result:", correct_result)
            print()
            print("Wrong Result:", result)


def kernel(TSTEPS, N, datatype=np.float64):
    A = np.fromfunction(lambda i, j: i * (j + 2) / N, (N, N), dtype=datatype)
    B = np.fromfunction(lambda i, j: i * (j + 3) / N, (N, N), dtype=datatype)

    for t in range(1, TSTEPS):
        # add1 = A[1:-1, 1:-1] + A[1:-1, :-2]
        # add2 = add1 + A[1:-1, 2:]
        # add3 = add2 + A[2:, 1:-1]
        # add4 = add3 + A[:-2, 1:-1]
        # B[1:-1, 1:-1] = 0.2 * (add4)
        # add1 = B[1:-1, 1:-1] + B[1:-1, :-2]
        # add2 = add1 + B[1:-1, 2:]
        # add3 = add2 + B[2:, 1:-1]
        # add4 = (add3 + B[:-2, 1:-1])
        # A[1:-1, 1:-1] = 0.2 * add4
        B[1:-1, 1:-1] = 0.2 * (A[1:-1, 1:-1] + A[1:-1, :-2] + A[1:-1, 2:] +
                               A[2:, 1:-1] + A[:-2, 1:-1])
        A[1:-1, 1:-1] = 0.2 * (B[1:-1, 1:-1] + B[1:-1, :-2] + B[1:-1, 2:] +
                               B[2:, 1:-1] + B[:-2, 1:-1])

    return A, B
