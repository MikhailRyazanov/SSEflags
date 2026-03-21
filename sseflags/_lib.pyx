# cython: language_level=3
# (disable unneeded features to reduce compiled size)
# cython: always_allow_keywords=False, auto_pickle=False, binding=False

from libcpp cimport bool


cdef extern from *:
    r""" // C code for Cython
    #include <stdbool.h>
    #include <pmmintrin.h>
    #include <xmmintrin.h>

    void c_set_daz(bool on) {
        _MM_SET_DENORMALS_ZERO_MODE(on ? _MM_DENORMALS_ZERO_ON
                                       : _MM_DENORMALS_ZERO_OFF);
    }

    void c_set_ftz(bool on) {
        _MM_SET_FLUSH_ZERO_MODE((on ? _MM_FLUSH_ZERO_ON
                                    : _MM_FLUSH_ZERO_OFF));
    }

    bool c_get_daz(void) {
        return _MM_GET_DENORMALS_ZERO_MODE();
    }

    bool c_get_ftz(void) {
        return _MM_GET_FLUSH_ZERO_MODE();
    }
    """
    # Cython declarations (not exported)
    void c_set_daz(bool on) nogil
    void c_set_ftz(bool on) nogil
    bool c_get_daz() nogil
    bool c_get_ftz() nogil


# Python wrappers for the C functions above

cpdef void _set_daz(bool on) noexcept nogil:
    c_set_daz(on)


cpdef void _set_ftz(bool on) noexcept nogil:
    c_set_ftz(on)


cpdef bool _get_daz() noexcept nogil:
    return c_get_daz()


cpdef bool _get_ftz() noexcept nogil:
    return c_get_ftz()
