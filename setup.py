from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

extensions = [
    Extension(
        "pymilight.packet_formatter", ["pymilight/packet_formatter.pyx"],
        include_dirs = ["include", "vendor", "src/compat"],
    )
]

setup(
    ext_modules = cythonize(extensions)
)
