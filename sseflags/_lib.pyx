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

        #define MASK_FZ  ((uint64_t)1 << 24)
        #define MASK_AH  ((uint64_t)1 <<  1)
        #define MASK_FIZ ((uint64_t)1 <<  0)

        #define GET_FLAGS uint64_t fpcr = __arm_rsr64(ARM64_FPCR);\
                          bool fz  = fpcr & MASK_FZ,\
                               ah  = fpcr & MASK_AH,\
                               fiz = fpcr & MASK_FIZ;

        #define AFP_DAZ (fiz || (!ah && fz))

        #define SET_FLAGS fpcr &= ~(MASK_FZ | MASK_AH | MASK_FIZ);\
                          if (fz)  fpcr |= MASK_FZ;\
                          if (ah)  fpcr |= MASK_AH;\
                          if (fiz) fpcr |= MASK_FIZ;\
                          __arm_wsr64(ARM64_FPCR, fpcr);

        bool feat_afp, keep_ah;

        bool c_has_daz(void) {
            uint64_t fpcr = __arm_rsr64(ARM64_FPCR);
            // AH already set?
            if (fpcr & MASK_AH) {
                keep_ah = true;
                return feat_afp = true;
            }
            // AH can be set?
            __arm_wsr64(ARM64_FPCR, fpcr | MASK_AH);
            if (__arm_rsr64(ARM64_FPCR) & MASK_AH) {
                __arm_wsr64(ARM64_FPCR, fpcr);
                keep_ah = false;
                return feat_afp = true;
            }
            return feat_afp = false;
        }

        void c_set_daz(bool on) {
            if (!feat_afp)
                return;
            GET_FLAGS;
            if (keep_ah && ah) {
                fiz = on;
            } else {
                ah = on < fz;
                fiz = on > fz;
            }
            SET_FLAGS;
        }

        void c_set_ftz(bool on) {
            GET_FLAGS;
            if (feat_afp && !(keep_ah && ah)) {
                bool daz = AFP_DAZ;
                ah = daz < on;
                fiz = daz > on;
            }
            fz = on;
            SET_FLAGS;
        }

        bool c_get_daz(void) {
            GET_FLAGS;
            return feat_afp ? AFP_DAZ : fz;
        }

        bool c_get_ftz(void) {
            return __arm_rsr64(ARM64_FPCR) & MASK_FZ;
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


# Initialization
_use_daz = c_has_daz()


# Python wrappers for the C functions above

cpdef void _set_daz(bool on) noexcept nogil:
    c_set_daz(on)


cpdef void _set_ftz(bool on) noexcept nogil:
    c_set_ftz(on)


cpdef bool _get_daz() noexcept nogil:
    return c_get_daz()


cpdef bool _get_ftz() noexcept nogil:
    return c_get_ftz()
