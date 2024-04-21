import sys

import numpy
# import numba

test_numba = len(sys.argv) > 1 and sys.argv[1] == "numba"


# @numba.experimental.jitclass
class Grid:
    """A simple grid class that stores the details and solution of the
    computational grid."""

    xmin: float
    xmax: float
    ymin: float
    ymax: float
    dx: float
    dy: float

    def __init__(self, nx=10, ny=10, xmin=0.0, xmax=1.0,
                 ymin=0.0, ymax=1.0):
        self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax
        self.dx = float(xmax - xmin) / (nx - 1)
        self.dy = float(ymax - ymin) / (ny - 1)
        self.u = numpy.zeros((nx, ny), 'd')
        # used to compute the change in solution in some of the methods.
        self.old_u = self.u.copy()

    def set_boundary_condition(self, func):
        """Sets the BC given a function of two variables."""
        xmin, ymin = self.xmin, self.ymin
        xmax, ymax = self.xmax, self.ymax
        x = numpy.arange(xmin, xmax + self.dx * 0.5, self.dx)
        y = numpy.arange(ymin, ymax + self.dy * 0.5, self.dy)
        self.u[0, :] = func(xmin, y)
        self.u[-1, :] = func(xmax, y)
        self.u[:, 0] = func(x, ymin)
        self.u[:, -1] = func(x, ymax)

    def computeError(self):
        """Computes absolute error using an L2 norm for the solution.
        This requires that self.u and self.old_u must be appropriately
        setup."""
        v = (self.u - self.old_u).flat
        return numpy.sqrt(numpy.dot(v, v))


# @numba.experimental.jitclass
class LaplaceSolver:
    """A simple Laplacian solver that can use different schemes to
    solve the problem."""

    def __init__(self, grid):
        self.grid = grid

    def step(self, dt=0.0):
        """Takes a time step using a NumPy expression."""
        g = self.grid
        dx2, dy2 = g.dx ** 2, g.dy ** 2
        dnr_inv = 0.5 / (dx2 + dy2)
        u = g.u
        g.old_u = u.copy()  # needed to compute the error.

        # The actual iteration
        u[1:-1, 1:-1] = ((u[0:-2, 1:-1] + u[2:, 1:-1]) * dy2 +
                         (u[1:-1, 0:-2] + u[1:-1, 2:]) * dx2) * dnr_inv

        v = (g.u - g.old_u).flat
        return numpy.sqrt(numpy.dot(v, v))

    def solve(self, n_iter=0, eps=1.0e-16):
        err = self.step()
        count = 1

        while err > eps:
            if n_iter and count >= n_iter:
                return err
            err = self.step()
            count = count + 1

        return count


def boundary_condition(x, y):
    """Used to set the boundary condition for the grid of points.
    Change this as you feel fit."""
    return (x ** 2 - y ** 2)


# def test(nmin=5, nmax=30, dn=5, eps=1.0e-16, n_iter=0, stepper='numeric'):
#     iters = []
#     n_grd = numpy.arange(nmin, nmax, dn)
#     times = []
#     for i in n_grd:
#         g = Grid(nx=i, ny=i)
#         g.set_boundary_condition(boundary_condition)
#         s = LaplaceSolver(g, stepper)
#         t1 = time.clock()
#         iters.append(s.solve(n_iter=n_iter, eps=eps))
#         dt = time.clock() - t1
#         times.append(dt)
#         print("Solution for nx = ny = %d, took %f seconds" % (i, dt))
#     return (n_grd ** 2, iters, times)


def solve_laplace(nx=500, ny=500, eps=1.0e-16, n_iter=1000):
    g = Grid(nx, ny)
    g.set_boundary_condition(boundary_condition)
    s = LaplaceSolver(g)
    s.solve(n_iter=n_iter, eps=eps)
