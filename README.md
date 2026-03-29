# SSE flags

NumPy for x86 platforms (IA-32 and AMD64 architectures) uses SSE and/or AVX for
floating-point calculations. Unfortunately, on Intel CPUs, they work very
slowly with
[subnormal (denormal) numbers](https://en.wikipedia.org/wiki/Subnormal_number).
To avoid such performance degradation, if somewhat worse floating-point
accuracy in extreme cases can be tolerated, the
[DAZ (denormals-are-zero) and FTZ (flush-to-zero) CPU flags](https://www.intel.com/content/www/us/en/docs/dpcpp-cpp-compiler/developer-guide-reference/2025-2/set-the-ftz-and-daz-flags.html)
were introduced to treat input and/or output subnormal numbers as zeros. This
module provides access to these CPU flags from Python.

To test the effect on your system, use ``sseflags.benchmark.run()`` or run
```
    python3 -m sseflags.benchmark
```
in the command line. Example output on Intel i9-12900K (subnormal numbers are
very slow):
```
    Times in milliseconds:
    normal     0.037
    default    1.979
    ========================
             FTZ off  FTZ on
    ------------------------
    DAZ off    1.993   2.037
    DAZ on     6.669   0.037
    ========================
```

AMD CPUs do not show performance degradation on subnormal numbers in the 64-bit
mode, and thus enabling DAZ/FTZ can only decrease the accuracy slightly.
Example benchmarks on AMD Ryzen 7 6800U (negligible degradation for subnormal
numbers; notice that times are in *micro*seconds):
```
    Times in microseconds:
    normal    14.434
    default   16.834
    ========================
             FTZ off  FTZ on
    ------------------------
    DAZ off   16.829  15.383
    DAZ on    15.353  14.500
    ========================
```
Nevertheless, DAZ/FTZ might be useful in 32-bit Python (same CPU, noticeable
difference):
```
    Times in milliseconds:
    normal     0.132
    default    0.229
    ========================
             FTZ off  FTZ on
    ------------------------
    DAZ off    0.225   0.131
    DAZ on     0.224   0.131
    ========================
```

AArch64 (ARM64) has the
[FZ flag](https://developer.arm.com/documentation/ddi0601/2025-12/AArch64-Registers/FPCR--Floating-point-Control-Register#fieldset_0-24_24)
to treat subnormal numbers as zeros similarly to both DAZ and FTZ together.
Therefore, enabling it with the same interface is implemented here for
compatibility. ARM CPUs with the
[FEAT_AFP feature](
https://developer.arm.com/documentation/ddi0487/maa/-Part-A-Arm-Architecture-Introduction-and-Overview/-Chapter-A2-A-profile-Architecture-Extensions/-A2-2-Armv8-A-architecture-extensions/-A2-2-8-The-Armv8-7-architecture-extension#feat_feat_afp)
(for example, Apple M3 but not M1) also support “alternate floating-point behavior”
[providing control](https://developer.arm.com/documentation/ddi0487/maa/-Part-A-Arm-Architecture-Introduction-and-Overview/-Chapter-A1-Introduction-to-the-Arm-Architecture/-A1-5-Floating-point-support/-A1-5-6-Flushing-denormalized-numbers-to-zero)
equivalent to separate DAZ and FTZ flags; however, this is not implemented yet (mostly due to the lack of testing).

On other architectures, or if the underlying Cython extension is not built, the
module only reports that it has no effect.


## ``sseflags`` module

```
type Flags = {'daz': bool | None, 'ftz': bool | None}


get_flags() -> sseflags.Flags
    Query current states of the DAZ and FTZ flags, see set_flags() for details.
    Can be used for restoring the default behavior:

        flags = get_flags()            # remember the original flag states
        set_flags(daz=True, ftz=True)  # enable DAZ and FTZ
        ...                            # do some calculations
        set_flags(**flags)             # restore the original flag states

    Returns
    -------
    flags : dict
        dictionary with the keys 'daz' and 'ftz', values of which represent the
        corresponding flag state: True for set, False for cleared, None if not
        implemented


set_flags(
    daz: bool | None = None,
    ftz: bool | None = None,
    verbose: bool = False
) -> bool
    Set the DAZ (denormals-are-zero) and/or FTZ (flush-to-zero) CPU flags for
    SSE and AVX floating-point calculations, which can be useful for Intel CPUs
    that work very slowly with subnormal (denormal) numbers.

    On AArch64 (ARM64) CPUs, both DAZ and FTZ are represented by the FZ flag,
    thus the daz and ftz parameters must be equal (or daz omitted).

    On unsupported architectures, or if the underlying Cython extension was not
    built, this function only reports that it has no effect. The availability
    can be checked by calling set_flags() without arguments.

    Parameters
    ----------
    daz : bool or None, optional
        True to set, False to clear the DAZ flag; None (default) to leave
        unchanged

    ftz : bool or None, optional
        True to set, False to clear the FTZ flag; None (default) to leave
        unchanged

    verbose : bool, optional
        pass True to print a warning if the operation is not implemented

    Returns
    -------
    implemented : bool
        True if this operation is implemented and supported, False if not
```

### ``sseflags.benchmark`` submodule

```
run(repeat: int = 100, min_t: float = 1.0, verbose: bool = True) -> None
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


run_flags(
    flags: Union[sseflags.Flags, Literal['default', 'normal']],
    repeat: int = 100,
    min_t: float = 1.0
) -> float | None
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
    time : float or None
        average time per iteration in seconds; None if the flags cannot be set
```

## Installation

Compiled wheels for Linux, macOS and Windows can be installed
[from PyPI](https://pypi.org/project/sseflags).
They use [“Stable ABI”](https://docs.python.org/3/c-api/stable.html#stable-abi)
that should be compatible with all Python versions ⩾3.10. For portability, a
“universal wheel” is also available, which does not contain the Cython
extension, and thus has no effect on computations, but can be installed on
unsupported systems. It can still benchmark the performance difference between
subnormal and normal numbers.
