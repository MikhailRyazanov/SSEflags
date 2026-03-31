# cython: language_level=3
# (disable unneeded features to reduce compiled size)
# cython: always_allow_keywords=False, auto_pickle=False, binding=False

from libcpp cimport bool


cdef extern from *:
    r""" // C code for Cython
    #include <stdbool.h>
    #if defined(__ARM_ARCH) // AArch64
        #include <inttypes.h>
        #if defined(_MSC_VER)
            // MSVC does not have arm_acle.h but defines int ARM64_FPCR
            #include <intrin.h>
            #define __arm_rsr64 _ReadStatusReg
            #define __arm_wsr64 _WriteStatusReg
        #else
            #include <arm_acle.h>
            #define ARM64_FPCR "FPCR"
        #endif
        #define MASK_FZ ((uint64_t)1 << 24)

        bool c_has_daz(void) {
            // by default, FZ means both DAZ and FTZ;
            // separate handling (FIZ as DAZ with AH=1) requires FEAT_AFP and
            // is not implemented yet
            return false;
        }

        void c_set_ftz(bool on) {
            uint64_t fpcr = __arm_rsr64(ARM64_FPCR);
            fpcr &= ~MASK_FZ;
            if (on)
                fpcr |= MASK_FZ;
            __arm_wsr64(ARM64_FPCR, fpcr);
        }

        bool c_get_ftz(void) {
            return __arm_rsr64(ARM64_FPCR) & MASK_FZ;
        }

        void c_set_daz(bool on) {
            // not implemented yet
        }

        bool c_get_daz(void) {
            return c_get_ftz();
        }
    #else // x86/AMD64
        #include <pmmintrin.h>
        #include <xmmintrin.h>

        bool c_has_daz(void) {
            return true;
        }

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
    #endif
    """
    # Cython declarations (not exported)
    bool c_has_daz() nogil
    void c_set_daz(bool on) nogil
    void c_set_ftz(bool on) nogil
    bool c_get_daz() nogil
    bool c_get_ftz() nogil


# Python wrappers for the C functions above

cpdef bool _has_daz() noexcept nogil:
    return c_has_daz()


cpdef void _set_daz(bool on) noexcept nogil:
    c_set_daz(on)


cpdef void _set_ftz(bool on) noexcept nogil:
    c_set_ftz(on)


cpdef bool _get_daz() noexcept nogil:
    return c_get_daz()


cpdef bool _get_ftz() noexcept nogil:
    return c_get_ftz()
