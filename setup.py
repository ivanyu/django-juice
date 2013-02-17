#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup
import os


# Allow setup.py to be run from any path.
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

NAME = "django-juice"
VERSION = "0.1b"

DESCRIPTION = "A collection of small reusable Django utilities in form of Django app."
LONG_DESCRIPTION = DESCRIPTION

AUTHOR = "Ivan Yurchenko <ivan0yurchenko@gmail.com>"
AUTHOR_EMAIL = "ivan0yurchenko@gmail.com"

MAINTAINER = AUTHOR
MAINTAINER_EMAIL = AUTHOR_EMAIL

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    keywords="django, views, forms, mixins",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=MAINTAINER,
    maintainer_email=MAINTAINER_EMAIL,
    url="https://github.com/ivanyu/django-juice/",
    license="MIT License",
    packages=["juice"],
    zip_safe=False,
    install_requires=[],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Django",
        "Environment :: Web Environment",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
