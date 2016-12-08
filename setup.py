#!/usr/bin/env python
import os
import sys
from setuptools import setup, find_packages

base_dir = os.path.dirname(__file__)

about = {}
with open(os.path.join(base_dir, "overpy", "__about__.py")) as f:
    exec(f.read(), about)

filename_readme = os.path.join(base_dir, "README.rst")
if sys.version_info[0] == 2:
    import io
    fp = io.open(filename_readme, encoding="utf-8")
else:
    fp = open(filename_readme, encoding="utf-8")
long_description = fp.read()

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
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy"
    ],
    keywords="OverPy Overpass OSM OpenStreetMap",
    install_requires=[],
    packages=find_packages(exclude=["*.tests", "*.tests.*"]),
    include_package_data=True,
    package_data={
        #"": ["README"],
    },
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
)
