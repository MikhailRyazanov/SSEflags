from itertools import count
from sys import float_info
from time import time

import numpy as np

from . import set_flags, get_flags


def run(repeat=100, min_t=1.0, verbose=True):
    """
    Run benchmarks with all possible combinations of the DAZ and FTZ flags to
    check their effect on NumPy performance (see run_flags() for details).

    Parameters
    ----------
    repeat : int, optional
        number of iterations in a batch

    min_t : float, optional
        minimal amount of time in seconds to benchmark each combination

    verbose : bool, optional
        pass False to suppress the progress report
    """
    def vprint(*args):
        if verbose:
            print(*args)

    flags = get_flags()
    vprint(f'Default: {flags}.')

    if not set_flags():
        print('Setting DAZ/FTZ is not implemented.')
        return

    res = {}
    for daz, ftz in [(None, None),
                     (False, False), (False, True),
                     (True, False), (True, True)]:
        res[daz, ftz] = run_flags({'daz': daz, 'ftz': ftz},
                                  repeat=repeat, min_t=min_t)
        vprint(f'Done {get_flags()}.')

    set_flags(**flags)
    vprint('Restored: {get_flags()}.\n')

    if max(res.values()) < 100e-6:
        prefix = 'micro'
        factor = 1e6
    else:
        prefix = 'milli'
        factor = 1e3

    def fmt(daz, ftz):
        return f'{res[(daz, ftz)] * factor:6.3f}'

    print(f'Times in {prefix}seconds:')
    print(f'default   {fmt(None, None)}')
    print('=' * 24)
    print('         FTZ off  FTZ on')
    print('-' * 24)
    print(f'DAZ off   {fmt(False, False)}  {fmt(False, True)}')
    print(f'DAZ on    {fmt(True, False)}  {fmt(True, True)}')
    print('=' * 24)


def run_flags(flags, repeat=100, min_t=1.0):
    """
    Set the DAZ and FTZ flags to given states and run a benchmark of NumPy
    matrix multiplication. Each iteration involves multiplication of normal
    numbers that would produce subnormal numbers and multiplication of
    subnormal numbers by normal numbers, which also would produce subnormal
    numbers.

    The test is designed for clear demonstration of performance degradation (if
    it is present); the effect for real-world data is usually less severe.

    Parameters
    ----------
    flags : dict
        dictionary with arguments passed to sseflags.set_flags()

    repeat : int, optional
        number of iterations in a batch

    min_t : float, optional
        batches are repeated until this amount of seconds passes

    Returns
    -------
    time : float
        average time per iteration in seconds
    """
    if None not in flags:
        # to ensure that subnormal test data can be created
        set_flags(daz=False, ftz=False)

    # Python "float" (= NumPy "float64" = C "double" = IEEE 754 "binary64")
    # numbers below 2**float_info.min_exp are subnormal and span
    # float_info.mant_dig binary orders of magnitude, thus:
    # A consists of normal elements, whose products would be subnormal,
    # B consists of subnormal elements
    x = np.arange(float_info.mant_dig)
    A = 2.0**(float_info.min_exp / 2 - (x + x[:, None]) / 2)
    B = 2.0**(float_info.min_exp - (x + x[:, None]) / 2)
    C = np.ones_like(B)

    set_flags(**flags)
    t0 = time()
    for i in count(1):
        for _ in range(repeat):
            A.dot(A)  # sum(normal * normal = subnormal) = subnormal
            B.dot(C)  # sum(subnormal * 1.0 = subnormal) = subnormal
        if time() > t0 + min_t:
            break
    return (time() - t0) / (i * repeat)


if __name__ == '__main__':
    run()
