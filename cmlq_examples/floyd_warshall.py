# Copyright 2021 ETH Zurich and the NPBench authors. All rights reserved.

import numpy as np
def kernel(N, datatype=np.int32):

    path = np.fromfunction(lambda i, j: i * j % 7 + 1, (N, N), dtype=datatype)
    for i in range(N):
        for j in range(N):
            if (i + j) % 13 == 0 or (i + j) % 7 == 0 or (i + j) % 11 == 0:
                path[i, j] = 999

    for k in range(path.shape[0]):
        left = path[:, k]
        right = path[k, :]
        breakpoint()
        outer = np.add.outer(left, right)
        path[:] = np.minimum(path[:], outer)

    return path