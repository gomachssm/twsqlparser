#!/usr/bin/env python3
# (C) 2020 gomachssm

import os
import sys


def pip_installed_map() -> dict:
    import pip._internal.commands.freeze
    packs = {}
    for p in pip._internal.commands.freeze.freeze():
        package, _, version = p.split('=')
        packs[package] = version
    from pprint import pprint
    pprint(packs)
    return packs


def check_pip_package(*pkgs) -> bool:
    packs = pip_installed_map()
    for pkg in pkgs:
        if not packs.get(pkg):
            # Return false, when package version is empty.
            print(f'[DEBUG] Not installed package: {pkg} .')
            return False
    print(f'[DEBUG] Required packages are already installed! {pkgs}')
    return True


if not check_pip_package('twsqlparser'):
    print('[DEBUG] Append local path for pytest in development.')
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../'))
