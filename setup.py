from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

extensions = [
    Extension(
        "pymilight.packet_formatter", ["pymilight/packet_formatter.pyx"],
        include_dirs = ["include", "src/compat"],
    )
]

setup(
    ext_modules = cythonize(extensions)
)
