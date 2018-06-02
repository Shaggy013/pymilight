from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

include_dirs = ["include", "vendor", "src/compat"]

extensions = [
    Extension(
        "pymilight.packet_formatter.packet_formatter",
        ["pymilight/packet_formatter/packet_formatter.pyx"],
        include_dirs=include_dirs,
    ),
    Extension(
        "pymilight.rgb_converter",
        ["pymilight/rgb_converter.pyx"],
        include_dirs=include_dirs,
        define_macros=[
            ('PYMILIGHT_NEED_MINMAX', '1')
        ],
    ),
]

setup(
    ext_modules = cythonize(extensions)
)
