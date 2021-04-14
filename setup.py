#!/usr/bin/env python
import os
import sys
from pathlib import Path
from setuptools import setup, find_packages

HERE = Path(__file__).resolve().parent

about = {}
exec((HERE / "overpy" / "__about__.py").read_text(), about)

long_description = (HERE / "README.rst").read_text()

setup(
    name=about["__title__"],
    version=about["__version__"],

    description=about["__summary__"],
    long_description=long_description,
    license=about["__license__"],
    url=about["__uri__"],

    zip_safe=False,
    author=about["__author__"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy"
    ],
    keywords="OverPy Overpass OSM OpenStreetMap",
    install_requires=[],
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests"]),
    include_package_data=True,
    package_data={
        #"": ["README"],
    },
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
)
