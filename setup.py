#!/usr/bin/env python3

import os
import setuptools

import twsqlparser

PKG_NAME = 'twsqlparser'


def abspath(path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))


def load_md(path):
    with open(path, 'r', encoding='UTF-8') as f:
        return f.read()


def setup_pkg():
    setuptools.setup(
        name=PKG_NAME,
        packages=[PKG_NAME],
        version=twsqlparser.__version__,
        license=twsqlparser.__license__,
        author=twsqlparser.__author__,
        url=twsqlparser.__url__,
        description='2way SQL parser for Python',
        long_description=load_md(abspath('./README.md')),
        long_description_content_type='text/markdown',
        keywords='two way sql twsql twowaysql two-way 2way 2way-sql',
        classifiers=['License :: OSI Approved :: Apache Software License',
                     'Programming Language :: Python :: 3.6',
                     'Programming Language :: Python :: 3.7',
                     'Programming Language :: Python :: 3.8',
                     'Programming Language :: Python :: 3.9']
    )


if __name__ == '__main__':
    setup_pkg()
