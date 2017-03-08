# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="python-translate",
    version="1.0.13",
    author="Adam Zieliński",
    author_email="adam@sf2.guru",
    packages=find_packages(),
    include_package_data=True,
    url="https://github.com/adamziel/python_translate",

    license="MIT",
    description="Non-gettext translations for python.",

    # Dependent packages (distributions)
    install_requires=[
        "PyYAML>=3.11",
        "codegen>=1.0",
        "polib>=1.0.6"
    ],
)
