import sys
from pprint import pprint

import numpy as np
import numpy.typing as npt
import laplace

import dis
import os
from timeit import timeit

import channel_flow
import nbody
import floyd_warshall
import adi
import jacobi_2d
import adist
import vadv
import correlat
import azimhist
import mandelbrot
import fdtd2d
import gramschmidt

import better_exceptions
profile = "PROFILE" in os.environ
test_numba = len(sys.argv) > 1 and sys.argv[1] == "numba"

def writeinst(opc: str, arg: int = 0):
    "Makes life easier in writing python bytecode"
    nb = max(1, -(-arg.bit_length() // 8))
    ab = arg.to_bytes(nb, sys.byteorder)
    ext_arg = dis._all_opmap['EXTENDED_ARG']
    inst = bytearray()
    for i in range(nb - 1):
        inst.append(ext_arg)
        inst.append(ab[i])
    inst.append(dis._all_opmap[opc])
    inst.append(ab[-1])

    return bytes(inst)


def patch(function, patches, stack_adjustment=0):
    code = dis.Bytecode(function, show_caches=True)
    bytelist = []
    for instr in code:
        name = instr.opname
        arg = instr.arg
        if instr.offset in patches:
            patch = patches[instr.offset]
            name = patch[0]
            if patch[1] is not None:
                arg = patch[1]

        if arg is None:
            arg = 0
        bytelist.append(writeinst(name, arg))

    bytes = b"".join(bytelist)

    orig = function.__code__
    function.__code__ = orig.replace(co_code=bytes, co_consts=orig.co_consts, co_names=orig.co_names,
                                     co_flags=orig.co_flags, co_stacksize=orig.co_stacksize + stack_adjustment)


state1 = np.random.RandomState()
state2 = np.random.RandomState()

n = 10
rng = np.random.default_rng()
rand_array = rng.standard_normal(n)


def normal_fast():
    global n
    global rand_array
    noise = rand_array * 3
    arange = np.arange(n)
    constant = (n / 23)
    div = arange / constant
    breakpoint()
    sin = np.sin(div)
    sin_minus = sin - 0.3
    pulses = np.maximum(sin_minus, -5.0)
    pulses_multiply = pulses * 300
    pulses_plus_noise = (pulses_multiply) + noise
    waveform = (pulses_plus_noise).astype(np.int16)
    return waveform


def patch_normal_fast():
    patch(normal_fast, {
        # 14: ("NP_AFLOAT_MULTIPLY_FLOAT", 1),  # replace BINARY_OP multiply
        # 92: ("NP_ALONG_DIVIDE_FLOAT", 1),  # replace BINARY_OP divide
        # 98: ("JUMP_FORWARD", 14),
        # 130: ("NP_AFLOAT_SIN", 3),  # replace CALL sin
        # 144: ("NP_AFLOAT_SUBTRACT_FLOAT", 1),  # replace subtract
        # 150: ("JUMP_FORWARD", 14),
        # 184: ("NP_AFLOAT_MAXIMUM", 3),  # replace CALL maximum
        # 198: ("NP_AFLOAT_MULTIPLY_FLOAT", 1),  # replace pulses multiplication
        # 208: ("NP_AFLOAT_ADD_AFLOAT", 1),  # replace pulses plus noise
    }, 1)
    global __rewrite__
    global __lltrace__
    __rewrite__ = True
    __lltrace__ = True


def normal_legacy():
    global n
    global rand_array
    noise = rand_array * 3
    arange = np.arange(n)
    constant = (n / 23)
    div = arange / constant
    sin = np.sin(div)
    sin_minus = sin - 0.3
    pulses = np.maximum(sin_minus, -5.0)
    pulses_multiply = pulses * 300
    pulses_plus_noise = (pulses_multiply) + noise
    waveform = (pulses_plus_noise).astype(np.int16)
    return waveform


def laplace_solve_fast():
    laplace.solve_laplace()


def patch_laplace():
    os.environ["CMLQ_REWRITE"] = "1"

    # patch(laplace.LaplaceSolver.step, {
    #     208: ("NP_AFLOAT_ADD_AFLOAT", 1),
    #     214: ("NP_AFLOAT_MULTIPLY_FLOAT", 1),
    #     258: ("NP_AFLOAT_ADD_AFLOAT", 1),
    #     264: ("NP_AFLOAT_MULTIPLY_FLOAT", 1),
    #     268: ("NP_AFLOAT_ADD_AFLOAT", 1),
    #     274: ("NP_AFLOAT_MULTIPLY_FLOAT", 1),
    #     342: ("NP_AFLOAT_SUBTRACT_FLOAT", 1),
    #     # 362: ("NP_AFLOAT_SUBTRACT_FLOAT", 1),
    # }, 0)


def laplace_solve_baseline():
    laplace.solve_laplace()


def test_channel_flow():
    nx = 201
    ny = 201

    u = np.zeros((ny, nx), dtype=np.float64)
    v = np.zeros((ny, nx), dtype=np.float64)
    p = np.ones((ny, nx), dtype=np.float64)
    dx = 2 / (nx - 1)
    dy = 2 / (ny - 1)
    dt = .1 / ((nx - 1) * (ny - 1))

    nit = 20
    rho = 1.0
    nu = 0.1
    F = 1.0
    channel_flow.channel_flow(nit, u, v, dt, dx, dy, p, rho, nu, F)


def patch_channel_flow():
    pass


def test_nbody():
    N = 100
    tEnd = 9.0
    dt = 0.01
    G = 1.0
    softening = 0.1
    from numpy.random import default_rng
    rng = default_rng(42)
    breakpoint()
    mass = 20.0 * np.ones((N, 1)) / N  # total mass of particles is 20
    pos = rng.random((N, 3))  # randomly selected positions and velocities
    vel = rng.random((N, 3))
    Nt = int(np.ceil(tEnd / dt))
    return nbody.nbody(mass, pos, vel, N, Nt, dt, G, softening)


__rewrite__ = False


def patch_nbody():
    os.environ["CMLQ_REWRITE"] = "1"

    patch(nbody.getAcc, {
        # 92: ("NP_AFLOAT_SUBTRACT_AFLOAT", 1),
        # 122: ("NP_AFLOAT_SUBTRACT_AFLOAT", 1),
        # 152: ("NP_AFLOAT_SUBTRACT_AFLOAT", 1),
    }, 0)

    patch(nbody.getEnergy, {
        # 56: ("NP_FLOAT_MULTIPLY_NPFLOAT", 1),
        # 152: ("NP_AFLOAT_SUBTRACT_AFLOAT", 1),
        # 182: ("NP_AFLOAT_SUBTRACT_AFLOAT", 1),
        # 212: ("NP_AFLOAT_SUBTRACT_AFLOAT", 1),
        # 264: ("NP_AFLOAT_ADD_AFLOAT", 1),
        # 276: ("NP_AFLOAT_ADD_AFLOAT", 1),
        # 440: ("NP_FLOAT_MULTIPLY_NPFLOAT", 1),
    }, 0)


def test_floyd_marshall():
    return floyd_warshall.kernel(850)


def test_adi():
    return adi.kernel(50, 500)


def test_jacobi2d():
    return jacobi_2d.kernel(1000, 2800)


def test_adist():
    return adist.arc_distance(10000000)


def test_vadv():
    return vadv.vadv(180, 180, 160)


def test_correlat():
    return correlat.kernel(3200, 4000)


def test_gramschmidt():
    return gramschmidt.kernel(600, 500)

def test_azimhist():
    return azimhist.kernel(1000000, 1000)


def test_mandelbrot():
    return mandelbrot.mandelbrot(-2.25, 0.75, -1.50, 1.50, 1000, 1000, 100, horizon=2.0)


def test_fdtd2d():
    return fdtd2d.kernel(500, 1000, 1200)


def enable_cmlq():
    if "BASELINE" not in os.environ:
        os.environ["CMLQ_REWRITE"] = "1"


def test_subscript():
    a = np.array([[1, 2, 3], [4, 5, 6]], np.float64)

    for i in range(100):
        breakpoint()
        a[1:, :] = a[1:, :] - 0.5

    return a;

def do_nothing():
    pass


N = 20000

reps = 3

# baseline = normal_legacy
# cmlq = normal_fast
# dis_fun = normal_fast
# patch_cmlq = enable_cmlq

# baseline = laplace_solve_baseline
# cmlq = laplace_solve_fast
# dis_fun = laplace.LaplaceSolver.step
# patch_cmlq = enable_cmlq

# baseline = test_channel_flow
# cmlq = test_channel_flow
# dis_fun = channel_flow.pressure_poisson_periodic
# patch_cmlq = enable_cmlq

# baseline = test_nbody
# cmlq = test_nbody
# dis_fun = nbody.getEnergy
# patch_cmlq = enable_cmlq

# baseline = test_floyd_marshall
# cmlq = test_floyd_marshall
# dis_fun = floyd_warshall.kernel
# patch_cmlq = enable_cmlq

baseline = test_adi
cmlq = test_adi
dis_fun = adi.kernel
patch_cmlq = enable_cmlq

# baseline = test_jacobi2d
# cmlq = test_jacobi2d
# dis_fun = jacobi_2d.kernel
# patch_cmlq = enable_cmlq

# baseline = test_fdtd2d
# cmlq = test_fdtd2d
# dis_fun = fdtd2d.kernel
# patch_cmlq = enable_cmlq


# baseline = test_adist
# cmlq = test_adist
# dis_fun = adist.arc_distance
# patch_cmlq = enable_cmlq

# baseline = test_vadv
# cmlq = test_vadv
# dis_fun = vadv.vadv
# patch_cmlq = enable_cmlq

# baseline = test_correlat
# cmlq = test_correlat
# dis_fun = correlat.kernel
# patch_cmlq = enable_cmlq


# baseline = test_azimhist
# cmlq = test_azimhist
# dis_fun = azimhist.kernel
# patch_cmlq = enable_cmlq


# baseline = test_mandelbrot
# cmlq = test_mandelbrot
# dis_fun = mandelbrot.mandelbrot
# patch_cmlq = enable_cmlq

# baseline = test_gramschmidt
# cmlq = test_gramschmidt
# dis_fun = gramschmidt.kernel
# patch_cmlq = enable_cmlq

# baseline = test_subscript
# cmlq = test_subscript
# dis_fun = test_subscript
# patch_cmlq = enable_cmlq


def check_array_equality(a, b):
    print(a.dtype)
    if a.dtype == np.float64:
        return np.allclose(a, b)
    if a.dtype == np.int32:
        return np.all(np.equal(a, b))
    if a.dtype == np.complex128:
        return np.all(np.equal(a, b))

    assert False, "Unsupported dtype"


cmlq_name = cmlq.__name__

if not profile:
    print("===== BASELINE =====")
    time_old = timeit(f"{baseline.__name__}()", globals=globals(), number=reps)
    baseline_result = baseline()
    # time_old = 1
else:
    print("Profiling enabled")

if not test_numba:

    print(f"===== {cmlq_name} BEFORE PATCH =====")
    dis.dis(dis_fun, show_caches=False)
    patch_cmlq()

    print("===== CMLQ =====")
    try:
        time_after_patch = timeit(f"{cmlq_name}()", globals=globals(), number=reps)
    except Exception as e:
        print("===== BROKEN REWRITE =====")
        dis.dis(dis_fun, show_caches=False, adaptive=True)
        raise e
    time_new = time_after_patch

    print(f"===== {cmlq_name} AFTER RUN =====")
    dis.dis(dis_fun, show_caches=False, adaptive=True)

    if not profile:
        cmlq_result = cmlq()
        num_instructions = len([i for i in dis.get_instructions(dis_fun)])
        num_quickened = len(list([i for i in dis.get_instructions(dis_fun) if i.opname == "EXTERNAL"]))
        print(f"{num_quickened} / {num_instructions} instructions quickened")


        if baseline_result is not None:
            print(type(baseline_result))
            equal = True
            if isinstance(baseline_result, tuple):
                for baseline, cmlq in zip(baseline_result, cmlq_result):
                    equality = check_array_equality(baseline, cmlq)
                    equal = equal and equality
            else:
                equal = check_array_equality(baseline_result, cmlq_result)
            if not equal:
                print("Results do not match")
                print("Baseline:", baseline_result)
                print("CMLQ:", cmlq_result)
        else:
            print("No baseline result reported")

else:
    import numba


    @numba.jit(nopython=True)
    def normal_jit():
        global n
        # with numba.objmode(rand_array="float64[:]"):
        #     rng = np.random.default_rng()
        #     rand_array = rng.standard_normal(n)
        rand_array = np.arange(n)
        noise = rand_array * 3
        print(noise)
        arange = np.arange(n)
        constant = (n / 23)
        div = arange / constant
        print(div)
        sin = np.sin(div)
        print(sin)
        sin_minus = sin - 0.3
        pulses = np.maximum(sin_minus, 0.0)
        print(pulses)
        pulses_multiply = pulses * 300
        pulses_plus_noise = (pulses_multiply) + noise
        waveform = (pulses_plus_noise).astype(np.int16)
        return waveform


    @numba.jit(nopython=True, parallel=False, fastmath=True)
    def kernel(TSTEPS, N, u):

        v = np.empty(u.shape, dtype=u.dtype)
        p = np.empty(u.shape, dtype=u.dtype)
        q = np.empty(u.shape, dtype=u.dtype)

        DX = 1.0 / N
        DY = 1.0 / N
        DT = 1.0 / TSTEPS
        B1 = 2.0
        B2 = 1.0
        mul1 = B1 * DT / (DX * DX)
        mul2 = B2 * DT / (DY * DY)

        a = -mul1 / 2.0
        b = 1.0 + mul2
        c = a
        d = -mul2 / 2.0
        e = 1.0 + mul2
        f = d

        for t in range(1, TSTEPS + 1):
            v[0, 1:N - 1] = 1.0
            p[1:N - 1, 0] = 0.0
            q[1:N - 1, 0] = v[0, 1:N - 1]
            for j in range(1, N - 1):
                p[1:N - 1, j] = -c / (a * p[1:N - 1, j - 1] + b)
                q[1:N - 1,
                j] = (-d * u[j, 0:N - 2] +
                      (1.0 + 2.0 * d) * u[j, 1:N - 1] - f * u[j, 2:N] -
                      a * q[1:N - 1, j - 1]) / (a * p[1:N - 1, j - 1] + b)
            v[N - 1, 1:N - 1] = 1.0
            for j in range(N - 2, 0, -1):
                v[j, 1:N - 1] = p[1:N - 1, j] * v[j + 1, 1:N - 1] + q[1:N - 1, j]

            u[1:N - 1, 0] = 1.0
            p[1:N - 1, 0] = 0.0
            q[1:N - 1, 0] = u[1:N - 1, 0]
            for j in range(1, N - 1):
                p[1:N - 1, j] = -f / (d * p[1:N - 1, j - 1] + e)
                q[1:N - 1,
                j] = (-a * v[0:N - 2, j] +
                      (1.0 + 2.0 * a) * v[1:N - 1, j] - c * v[2:N, j] -
                      d * q[1:N - 1, j - 1]) / (d * p[1:N - 1, j - 1] + e)
            u[1:N - 1, N - 1] = 1.0
            for j in range(N - 2, 0, -1):
                u[1:N - 1, j] = p[1:N - 1, j] * u[1:N - 1, j + 1] + q[1:N - 1, j]


    print("Running with numba")


    def call_kernel():
        u = np.fromfunction(lambda i, j: (i + N - j) / N, (N, N), dtype=np.float64)
        kernel(5, 100, u)


    # jit = normal_jit()
    jit = call_kernel

    # warmup
    jit()
    time_new = timeit(f"{jit.__name__}()", globals=globals(), number=reps)
    llvm_code = kernel.inspect_llvm()
    asm_code = kernel.inspect_asm()
    compile_result = kernel.overloads[kernel.signatures[0]]

if not profile:
    print(f"OLD: {time_old}")
print(f"NEW: {time_new}")

if not profile:
    print(f"OLD/NEW: {time_old / time_new}")

pprint(np.core.multiarray.get_cmlq_stats())
pprint(get_cmlq_functions())
pprint(get_cmlq_stats(dis_fun.__code__))

if test_numba and len(sys.argv) > 2:
    if sys.argv[2] == "show-llvm":
        for v, k in llvm_code.items():
            print(v, k)

    if sys.argv[2] == "show-asm":
        for v, k in asm_code.items():
            print(v, k)

    if sys.argv[2] == "show-passes":
        nopython_times = compile_result.metadata['pipeline_times']['nopython']
        for k in nopython_times.keys():
            print(k)

# print(b)
# print((b - a) / a)
