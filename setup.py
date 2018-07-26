import os
import sys
from setuptools import setup

with open("README.md") as f:
    readme = f.read()

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    ]

setup(
    name = "ZebraStripes",
    version = "0.0.1",
    description = "Zebra stripes for zebraFish!",
    long_description = readme,
    packages = [ "ZebraStripes" ],
    package_dir = { 'ZebraStripes' : '.' },
    # install_requires = [ 'opencv-python', 'pillow' ],
    author = "Dilawar Singh",
    author_email = "dilawars@ncbs.res.in",
    url = "http://github.com/dilawar/ZebraStripes",
    license='GPL',
    classifiers=classifiers,
    entry_points = {
        'console_scripts': ['zebra-stripes=ZebraStripes.main:main'],
        }
)
