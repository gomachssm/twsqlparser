#!/usr/bin/env python3

import os
import setuptools
import shutil

PKG_NAME = 'twsqlparser'
here = os.path.abspath(os.path.dirname(__file__))


def abspath(path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))


def delete_dir(path_list: list):
    for path in path_list:
        path = abspath(path)
        if not os.path.isdir(path):
            print(f'[DEBUG] Directory `{path}` is not exist.')
            continue
        shutil.rmtree(path)
        print(f'[DEBUG] Succeed, Directory `{path}` is deleted.')


def load_md(path: str):
    with open(path, 'r', encoding='UTF-8') as f:
        return f.read()


def load_env_by_exec_py(path: str):
    env_map = {}
    python_file_path = abspath(path)
    with open(python_file_path, mode='r', encoding='utf-8') as f:
        exec(f.read(), env_map)
        return env_map


def setup_pkg():
    delete_dir(['build', 'dist', 'twsqlparser.egg-info'])
    about = load_env_by_exec_py('twsqlparser/__pkg_info__.py')
    setuptools.setup(
        name=PKG_NAME,
        packages=[PKG_NAME],
        version=about['__version__'],
        license=about['__license__'],
        author=about['__author__'],
        url=about['__url__'],
        package_dir={PKG_NAME: PKG_NAME},
        description='2way SQL parser for Python',
        long_description=load_md(abspath('./README.md')),
        long_description_content_type='text/markdown',
        keywords='two way sql twsql twowaysql two-way 2way 2way-sql',
        python_requires=">=3.6",
        classifiers=['License :: OSI Approved :: Apache Software License',
                     'Programming Language :: Python :: 3.6',
                     'Programming Language :: Python :: 3.7',
                     'Programming Language :: Python :: 3.8',
                     'Programming Language :: Python :: 3.9']
    )


if __name__ == '__main__':
    setup_pkg()
