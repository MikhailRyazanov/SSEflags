from typing import TypedDict
try:
    from ._lib import _has_daz, _get_daz, _get_ftz, _set_daz, _set_ftz
    _ext = True
    _use_daz = _has_daz()
except ImportError:
    _ext = False

__version__ = '0.3'

Flags = TypedDict('Flags', {'daz': bool | None, 'ftz': bool | None},
                  total=False)


def get_flags() -> Flags:
    """
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
    """
    flags: Flags = {'daz': None, 'ftz': None}
    if _ext:
        flags['daz'] = _get_daz()
        flags['ftz'] = _get_ftz()
    return flags


def set_flags(daz: bool | None = None, ftz: bool | None = None,
              verbose: bool = False) -> bool:
    """
    Set the DAZ (denormals-are-zero) and/or FTZ (flush-to-zero) CPU flags for
    SSE and AVX floating-point calculations, which can be useful for Intel CPUs
    that work very slowly with subnormal (denormal) numbers.

    On AArch64 (ARM64) CPUs, both DAZ and FTZ are represented by the FZ flag,
    thus the daz and ftz parameters must be equal.

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
    """
    if _ext:
        if not _use_daz and daz != ftz:
            if verbose:
                print('Setting the DAZ and FTZ flags independently is not '
                      'supported for this CPU.')
            return False
        if daz is not None:
            _set_daz(daz)
        if ftz is not None:
            _set_ftz(ftz)
        return True

    if verbose:
        print('Cannot change the DAZ/FTZ flags: the extension was not '
              'compiled or is not needed for this CPU.')
    return False
