#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pathlib

from setuptools import setup

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")


def _parse_requirements_file(requirements_file):
    parsed_requirements = []
    with open(requirements_file) as rfh:
        for line in rfh.readlines():
            line = line.strip()
            if not line or line.startswith(("#", "-r", "--")):
                continue
            parsed_requirements.append(line)
    return parsed_requirements


setup(
    name='mock-api',
    description='mock-api',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.7, <4",
    packages=["src"],
    install_requires=_parse_requirements_file("requirements.txt"),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'mock-api = __main__:main',
        ]
    }
)
