# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name="python-translate",
    version="1.0.1",
    author="Adam Zieliński",
    author_email="adam@sf2.guru",
    packages=["python_translate"],
    include_package_data=True,
    url="https://github.com/adamziel/python_translate",

    license="MIT",
    description="Non-gettext translations for python.",

    # Dependent packages (distributions)
    install_requires=[
        "PyYAML==3.11",
        "codegen==1.0",
        "polib==1.0.6"
    ],
)