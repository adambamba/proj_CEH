"""Color handling and additional colormaps.

Copyright: Fabien Maussion, 2014-2015

License: GPLv3+
"""
from __future__ import division
# Builtins
# External libs
import numpy as np
from numpy import ma
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap
# Locals


class ExtendedNorm(mpl.colors.BoundaryNorm):
    """ A better BoundaryNorm with an ``extend'' keyword.

    TODO: remove this when PR is accpeted

    See: https://github.com/matplotlib/matplotlib/issues/4850
         https://github.com/matplotlib/matplotlib/pull/5034
    """

    def __init__(self, boundaries, ncolors, extend='neither'):

        _b = np.atleast_1d(boundaries).astype(float)
        mpl.colors.BoundaryNorm.__init__(self, _b, ncolors, clip=False)

        # 'neither' | 'both' | 'min' | 'max'
        if extend == 'both':
            _b = np.append(_b, _b[-1]+1)
            _b = np.insert(_b, 0, _b[0]-1)
        elif extend == 'min':
            _b = np.insert(_b, 0, _b[0]-1)
        elif extend == 'max':
            _b = np.append(_b, _b[-1]+1)
        self._b = _b
        self._N = len(self._b)
        if self._N - 1 == self.Ncmap:
            self._interp = False
        else:
            self._interp = True

    def __call__(self, value):
        xx, is_scalar = self.process_value(value)
        mask = ma.getmaskarray(xx)
        xx = np.atleast_1d(xx.filled(self.vmax + 1))
        iret = np.zeros(xx.shape, dtype=np.int16)
        for i, b in enumerate(self._b):
            iret[xx >= b] = i
        if self._interp:
            scalefac = float(self.Ncmap - 1) / (self._N - 2)
            iret = (iret * scalefac).astype(np.int16)
        iret[xx < self.vmin] = -1
        iret[xx >= self.vmax] = self.Ncmap
        ret = ma.array(iret, mask=mask)
        if is_scalar:
            ret = int(ret[0])  # assume python scalar
        return ret


def _topo():
    """Topographical colormap.

    http://soliton.vm.bytemark.co.uk/pub/cpt-city/wkp/schwarzwald/tn/wiki
    -schwarzwald-cont.png.index.html

    Copyright:
    Creative commons attribution share-alike 3.0 unported
    http://soliton.vm.bytemark.co.uk/pub/cpt-city/wkp/schwarzwald/copying.html
    """

    # Quick n dirty solution, to be meliorated later
    cl = ((174, 239, 213),
          (175, 240, 211),
          (176, 242, 208),
          (176, 242, 202),
          (177, 242, 196),
          (176, 243, 190),
          (176, 244, 186),
          (178, 246, 181),
          (181, 246, 178),
          (186, 247, 178),
          (192, 247, 178),
          (198, 248, 178),
          (204, 249, 178),
          (210, 250, 177),
          (217, 250, 178),
          (224, 251, 178),
          (231, 252, 178),
          (238, 252, 179),
          (245, 252, 179),
          (250, 252, 178),
          (248, 249, 172),
          (238, 244, 162),
          (226, 240, 151),
          (213, 235, 140),
          (198, 228, 128),
          (184, 222, 118),
          (170, 216, 108),
          (154, 211,  98),
          (140, 205,  89),
          (125, 199,  82),
          (110, 194,  74),
          ( 94, 188,  66),
          ( 77, 182,  57),
          ( 62, 176,  50),
          ( 49, 171,  44),
          ( 39, 165,  42),
          ( 30, 160,  43),
          ( 24, 154,  46),
          ( 18, 148,  49),
          ( 14, 142,  52),
          (  9, 137,  56),
          (  7, 132,  60),
          ( 12, 130,  63),
          ( 24, 130,  63),
          ( 40, 132,  61),
          ( 52, 136,  60),
          ( 64, 140,  59),
          ( 76, 142,  59),
          ( 87, 146,  56),
          ( 99, 148,  54),
          (110, 150,  52),
          (120, 154,  50),
          (128, 156,  48),
          (137, 160,  46),
          (147, 162,  43),
          (156, 164,  41),
          (166, 166,  39),
          (176, 170,  36),
          (187, 173,  34),
          (197, 176,  30),
          (207, 177,  28),
          (218, 179,  24),
          (228, 180,  20),
          (238, 182,  14),
          (246, 182,   8),
          (248, 176,   4),
          (244, 166,   2),
          (238, 155,   2),
          (232, 144,   2),
          (226, 132,   2),
          (220, 122,   2),
          (216, 111,   2),
          (211, 102,   2),
          (206,  92,   2),
          (200,  84,   2),
          (192,  74,   2),
          (186,  66,   2),
          (180,  58,   2),
          (174,  49,   2),
          (169,  42,   2),
          (163,  36,   2),
          (157,  30,   2),
          (151,  23,   2),
          (146,  18,   1),
          (141,  14,   1),
          (135,   8,   0),
          (130,   5,   0),
          (125,   4,   0),
          (122,   8,   2),
          (119,  13,   2),
          (118,  16,   2),
          (117,  18,   4),
          (117,  20,   4),
          (117,  21,   4),
          (116,  22,   4),
          (116,  24,   5),
          (114,  26,   6),
          (114,  29,   6),
          (112,  31,   7),
          (111,  33,   8),
          (110,  35,   8),
          (110,  36,   8),
          (109,  38,   9),
          (108,  40,  10),
          (108,  40,  10),
          (108,  42,  10),
          (107,  44,  11),
          (106,  44,  12),
          (106,  46,  12),
          (107,  48,  14),
          (110,  52,  18),
          (113,  57,  23),
          (116,  62,  28),
          (118,  66,  32),
          (121,  70,  37),
          (125,  74,  43),
          (128,  79,  50),
          (131,  85,  56),
          (135,  90,  63),
          (138,  96,  69),
          (140, 101,  76),
          (144, 106,  84),
          (147, 111,  90),
          (150, 116,  96),
          (152, 122, 104),
          (156, 129, 112),
          (158, 135, 120),
          (160, 141, 130),
          (163, 147, 139),
          (166, 154, 147),
          (167, 160, 156),
          (170, 167, 164),
          (172, 172, 171),
          (174, 174, 174),
          (178, 178, 178),
          (181, 181, 181),
          (184, 184, 184),
          (188, 188, 188),
          (192, 192, 192),
          (196, 196, 196),
          (200, 200, 200),
          (204, 204, 204),
          (208, 206, 208),
          (212, 210, 212),
          (216, 214, 216),
          (218, 216, 218),
          (221, 219, 221),
          (225, 223, 225),
          (229, 227, 229),
          (233, 231, 233),
          (235, 233, 235))

    cl = np.asarray(cl).astype(np.float) / 256.
    return LinearSegmentedColormap.from_list('topo', cl, N=256)


def get_cm(name='none'):
    """Get a colormap defined by Cleo (more to come!)"""
    return globals()['_' + name]()