#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup  # type: ignore[import]
except ImportError:
    from distutils.core import setup


if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    sys.exit()

readme = open("README.md").read()
doclink = """
Documentation
-------------

The full documentation is at http://flowlayer.rtfd.org."""
history = open("HISTORY.md").read().replace(".. :changelog:", "")

setup(
    name="flowlayer",
    version="0.1.0",
    description="Lightweight data processing workflows with typing.",
    long_description=readme + "\n\n" + doclink + "\n\n" + history,
    author="Sam Star",
    author_email="justsam@contact.com",
    url="https://github.com/jsam/flowlayer",
    packages=[
        "flowlayer",
        "flowlayer.core",
    ],
    package_dir={"flowlayer": "flowlayer"},
    include_package_data=True,
    install_requires=[],
    license="MIT",
    zip_safe=False,
    keywords="flowlayer",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
