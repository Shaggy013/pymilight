# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from setuptools.extension import Extension
from os import path
from Cython.Build import cythonize

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

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
    name='pymilight',
    version='0.0.1a',
    description='MiLights for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/dmkent/pymilight',
    author='David Kent',
    packages=find_packages(),
    ext_modules = cythonize(extensions),
    install_requires=[
        "cython",
        "paho.mqtt",
        #"RF24", TODO - install
    ],

    #entry_points={  # Optional
    #    'console_scripts': [
    #        'sample=sample:main',
    #    ],
    #},
)
