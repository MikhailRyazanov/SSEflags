from itertools import count
from sys import float_info
from time import time
from typing import Any, Literal

import numpy as np

from . import set_flags, get_flags, Flags


def run(repeat: int = 100, min_t: float = 1.0, verbose: bool = True) -> None:
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
    def vprint(*args: Any, **kwargs: Any) -> None:
        if verbose:
            print(*args, **kwargs, flush=True)

    ResKey = str | tuple[bool, bool]
    res: dict[ResKey, float] = {}

    vprint('Running normal...', end='')
    res['normal'] = run_flags('normal', repeat=repeat, min_t=min_t)
    vprint(' done.')

    vprint(f'Running default {get_flags()}...', end='')
    res['default'] = run_flags('default', repeat=repeat, min_t=min_t)
    vprint(' done.')

    if not set_flags():
        print('Setting DAZ/FTZ is not implemented.')
    else:
        for daz, ftz in [(False, False), (False, True),
                         (True, False), (True, True)]:
            flags: Flags = {'daz': daz, 'ftz': ftz}
            vprint(f'Running {flags}...', end='')
            res[daz, ftz] = run_flags(flags, repeat=repeat, min_t=min_t)
            vprint(' done.')
    vprint('')

    if max(res.values()) < 100e-6:
        prefix = 'micro'
        factor = 1e6
    else:
        prefix = 'milli'
        factor = 1e3

    def fmt(key: ResKey) -> str:
        return f'{res[key] * factor:6.3f}'

    print(f'Times in {prefix}seconds:')
    print(f'normal    {fmt("normal")}')
    print(f'default   {fmt("default")}')
    if (True, True) in res:
        print('=' * 24)
        print('         FTZ off  FTZ on')
        print('-' * 24)
        print(f'DAZ off   {fmt((False, False))}  {fmt((False, True))}')
        print(f'DAZ on    {fmt((True, False))}  {fmt((True, True))}')
        print('=' * 24)


def run_flags(flags: Flags | Literal['default',  'normal'],
              repeat: int = 100, min_t: float = 1.0) -> float:
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
    flags : dict or str
        dictionary with arguments passed to sseflags.set_flags() after creating
        subnormal test data;

        flags='default' benchmark without changing the flags (thus test data
        might be missing subnormal numbers, which corresponds to running
        self-contained calculations but does not represent calculations with
        external data);

        flags='normal' benchmark normal numbers for reference (should not
        depend on the flags)

    repeat : int, optional
        number of iterations in a batch

    min_t : float, optional
        batches are repeated until this amount of seconds passes

    Returns
    -------
    time : float
        average time per iteration in seconds
    """
    orig_flags = get_flags()

    # Python "float" (= NumPy "float64" = C "double" = IEEE 754 "binary64")
    # numbers below 2**float_info.min_exp are subnormal and span
    # float_info.mant_dig binary orders of magnitude
    x = np.arange(float_info.mant_dig)
    xx = (x + x[:, None]) / 2
    if flags == 'normal':
        A = 2.0**(-xx)
        B = -A
    else:
        if flags != 'default':
            # to ensure that subnormal test data can be created
            set_flags(daz=False, ftz=False)
        # A consists of normal elements, whose products would be subnormal,
        # A.dot(A) would be sum(normal * normal = subnormal) = subnormal
        A = 2.0**(float_info.min_exp / 2 - xx)
        # B consists of subnormal elements
        # B.dot(C) would be sum(subnormal * 1.0 = subnormal) = subnormal
        B = 2.0**(float_info.min_exp - xx)
        if flags != 'default':
            set_flags(**flags)
    C = np.ones_like(B)

    t0 = time()
    for i in count(1):
        for _ in range(repeat):
            A.dot(A)
            B.dot(C)
        if time() > t0 + min_t:
            break

    set_flags(**orig_flags)

    return (time() - t0) / (i * repeat)


if __name__ == '__main__':
    run()
