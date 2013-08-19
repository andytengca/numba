from numbapro.npm import types, cgutils
from . import ptx

def SRegImplFactory(func):
    class SRegImpl(object):
        function = func, (), types.uint32

        def generic_implement(self, context, args, argtys, retty):
            builder = context.builder
            sreg = ptx.SREG_MAPPING[self.function[0]]
            lretty = self.function[-1].llvm_as_value()
            func = cgutils.get_function(builder, sreg, lretty, ())
            return builder.call(func, ())
    return SRegImpl

TidX = SRegImplFactory(ptx._ptx_sreg_tidx)
TidY = SRegImplFactory(ptx._ptx_sreg_tidy)
TidZ = SRegImplFactory(ptx._ptx_sreg_tidz)

NTidX = SRegImplFactory(ptx._ptx_sreg_ntidx)
NTidY = SRegImplFactory(ptx._ptx_sreg_ntidy)
NTidZ = SRegImplFactory(ptx._ptx_sreg_ntidz)

CTAidX = SRegImplFactory(ptx._ptx_sreg_ctaidx)
CTAidY = SRegImplFactory(ptx._ptx_sreg_ctaidy)

NCTAidX = SRegImplFactory(ptx._ptx_sreg_nctaidx)
NCTAidY = SRegImplFactory(ptx._ptx_sreg_nctaidy)


#-------------------------------------------------------------------------------
#  Grid

class Grid1D(object):
    function = ptx._ptx_grid1d, (types.uint32,), types.intp

    def generic_implement(self, context, args, argtys, retty):
        builder = context.builder

        fname_tidx = ptx.SREG_MAPPING[ptx._ptx_sreg_tidx]
        fname_ntidx = ptx.SREG_MAPPING[ptx._ptx_sreg_ntidx]
        fname_ctaidx = ptx.SREG_MAPPING[ptx._ptx_sreg_ctaidx]

        li32 = types.uint32.llvm_as_value()
        fn_tidx = cgutils.get_function(builder, fname_tidx, li32, ())
        fn_ntidx = cgutils.get_function(builder, fname_ntidx, li32, ())
        fn_ctaidx = cgutils.get_function(builder, fname_ctaidx, li32, ())

        tidx = builder.call(fn_tidx, ())
        ntidx = builder.call(fn_ntidx, ())
        ctaidx = builder.call(fn_ctaidx, ())

        tidx = context.cast(tidx, types.uint32, retty)
        ntidx = context.cast(ntidx, types.uint32, retty)
        ctaidx = context.cast(ctaidx, types.uint32, retty)

        return builder.add(tidx, builder.mul(ntidx, ctaidx))


class Grid2D(object):
    return_type = types.tupletype(types.intp, types.intp)
    function = ptx._ptx_grid2d, (types.uint32,), return_type

    def generic_implement(self, context, args, argtys, retty):
        builder = context.builder

        fname_tidx = ptx.SREG_MAPPING[ptx._ptx_sreg_tidx]
        fname_tidy = ptx.SREG_MAPPING[ptx._ptx_sreg_tidy]
        fname_ntidx = ptx.SREG_MAPPING[ptx._ptx_sreg_ntidx]
        fname_ntidy = ptx.SREG_MAPPING[ptx._ptx_sreg_ntidy]
        fname_ctaidx = ptx.SREG_MAPPING[ptx._ptx_sreg_ctaidx]
        fname_ctaidy = ptx.SREG_MAPPING[ptx._ptx_sreg_ctaidy]

        li32 = types.uint32.llvm_as_value()
        fn_tidx = cgutils.get_function(builder, fname_tidx, li32, ())
        fn_tidy = cgutils.get_function(builder, fname_tidy, li32, ())
        fn_ntidx = cgutils.get_function(builder, fname_ntidx, li32, ())
        fn_ntidy = cgutils.get_function(builder, fname_ntidy, li32, ())
        fn_ctaidx = cgutils.get_function(builder, fname_ctaidx, li32, ())
        fn_ctaidy = cgutils.get_function(builder, fname_ctaidy, li32, ())

        tidx = builder.call(fn_tidx, ())
        tidy = builder.call(fn_tidy, ())
        ntidx = builder.call(fn_ntidx, ())
        ntidy = builder.call(fn_ntidy, ())
        ctaidx = builder.call(fn_ctaidx, ())
        ctaidy = builder.call(fn_ctaidy, ())

        tidx = context.cast(tidx, types.uint32, types.intp)
        tidy = context.cast(tidy, types.uint32, types.intp)
        ntidx = context.cast(ntidx, types.uint32, types.intp)
        ntidy = context.cast(ntidy, types.uint32, types.intp)
        ctaidx = context.cast(ctaidx, types.uint32, types.intp)
        ctaidy = context.cast(ctaidy, types.uint32, types.intp)

        x = builder.add(tidx, builder.mul(ntidx, ctaidx))
        y = builder.add(tidy, builder.mul(ntidy, ctaidy))

        return retty.desc.llvm_pack(builder, (x, y))


extensions = [
    # SReg
    TidX, TidY, TidZ,
    NTidX, NTidY, NTidZ,
    CTAidX, CTAidY,
    NCTAidX, NCTAidY,
    # Grid
    Grid1D, Grid2D,
]

