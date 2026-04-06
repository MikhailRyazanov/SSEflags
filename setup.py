import os
from pathlib import Path
import sys
from setuptools import setup, Extension

sys.path.insert(0, '')  # include CWD (missing in build isolation)
from sseflags import __version__

extra_link_args = None
if sys.platform == 'win32':  # for MSVC
    extra_compile_args = ['/Os']
else:  # for GCC and Clang
    extra_compile_args = ['-Os', '-g0']
    if sys.platform != 'darwin':  # ld on macOS does not support these
        extra_link_args = ['-s', '-Wl,-z,norelro', '-Wl,-z,noseparate-code']
ext_modules = [
    # ("Path" below is a workaround for Setuptools bug on Windows,
    #  see https://github.com/pypa/setuptools/issues/5093)
    Extension('sseflags._lib', [Path('sseflags/_lib.pyx')],
              extra_compile_args=extra_compile_args,
              extra_link_args=extra_link_args,
              define_macros=[('Py_LIMITED_API', 0x030A0000)],  # 0x0B = 11
              py_limited_api=True)
]
# "sseflags=none python -m build --wheel" to build a "universal" wheel
# (...-none-any.whl) without Cython extension
if os.environ.get('sseflags') == 'none':
    ext_modules = None

setup(version=__version__, ext_modules=ext_modules,
      options={'bdist_wheel': {'py_limited_api': 'cp310'}})
