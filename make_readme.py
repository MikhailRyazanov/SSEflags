#!/usr/bin/env python3
from pydoc import plaintext, render_doc

from sseflags import get_flags, set_flags
from sseflags.benchmark import run, run_flags


def doc(obj):
    # render plain-text documentation
    txt = render_doc(obj, renderer=plaintext)
    # strip 1st line (header) plus 1st and last '\n'
    return txt[txt.find('\n') + 2:-1]


README = f"""\
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
    default    0.229
    ========================
             FTZ off  FTZ on
    ------------------------
    DAZ off    0.225   0.131
    DAZ on     0.224   0.131
    ========================
```

On other architectures, or if the underlying Cython extension is not built, the
module only reports that it has no effect.


## ``sseflags`` module

```
{doc(get_flags)}


{doc(set_flags)}
```

### ``sseflags.benchmark`` submodule

```
{doc(run)}


{doc(run_flags)}
```

## Installation

Compiled wheels for Linux, macOS and Windows can be installed
[from PyPI](https://pypi.org/project/sseflags).
They use [“Stable ABI”](https://docs.python.org/3/c-api/stable.html#stable-abi)
that should be compatible with all Python versions ⩾3.10. For portability, a
“universal wheel” is also available. It does not contain the Cython extension,
and thus has no effect on computations, but can be installed on unsupported
systems.
"""

with open('README.md', 'w') as f:
    f.write(README)
