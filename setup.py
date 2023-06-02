#!/usr/bin/env python
from pathlib import Path
from setuptools import setup, find_packages

HERE = Path(__file__).resolve().parent

about = {}
exec((HERE / "overpy" / "__about__.py").read_text(), about)

setup(
    name=about["__title__"],
    version=about["__version__"],

    description=about["__summary__"],
    license=about["__license__"],
    url=about["__uri__"],
    author=about["__author__"],
    keywords="OverPy Overpass OSM OpenStreetMap",
    install_requires=[],
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests"]),
    package_data={
        # "": ["README"],
    },
    tests_require=["pytest"],
)
