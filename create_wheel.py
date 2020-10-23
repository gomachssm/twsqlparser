#!/usr/bin/env python3
# (C) 2020 gomachssm

import os
import shutil
import subprocess


def clean_dir(dirpath: str):
    if os.path.isdir(dirpath):
        shutil.rmtree(dirpath, ignore_errors=True, )


def install_pkg(pkg):
    if has_pkg(pkg):
        logger.info(f'"{pkg}" is installed already.')
        return
    pip_command = f'pip install -U {pkg}'
    logger.info(f'Start command: "{" ".join(pip_command)}"')
    stdout, _ = command(pip_command)
    logger.debug(stdout)


def has_pkg(pkg: str) -> bool:
    stdout, stderr = command('pip freeze --all')
    installed_packages = stdout.replace('\r\n', '\n').replace('\r', '\n')
    for installed_package in installed_packages.split('\n'):
        logger.debug(installed_package)
        if installed_package.startswith(pkg):
            return True
    return False


def python_version():
    stdout, _ = command('python -V')
    return stdout


def command(cmd: str):
    logger.debug(f'execute command: {cmd}')
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as cmd_result:
        out, error = cmd_result.communicate()
    stdout = out.decode() if out else None
    stderr = error.decode() if error else None
    logger.debug(f'[stdout]{stdout}')
    logger.debug(f'[stderr]{stderr}')
    return stdout, stderr


def exec_cmd_in_batch(script: str):
    ostyp = get_ostype()
    encoding = 'ms932' if ostyp == 'win' else 'utf-8'
    exp = 'bat' if ostyp == 'win' else 'sh'
    filepath = f'xxxxxxxxxx.{exp}'
    try:
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(script)
        batch_command = filepath if ostyp == 'win' else f'sh {filepath}'
        command(batch_command)
    finally:
        os.remove(filepath)


def get_ostype():
    if os.name == 'nt':
        return 'win'
    return 'linux'


def get_logger():
    import logging.config
    import sys
    level = logging.DEBUG if sys.flags.debug == 0 else logging.INFO
    log_setting = {'version': 1, 'disable_existing_loggers': False,
                   'root': {'level': level, 'handlers': ['ctConsole']},
                   'handlers': {'ctConsole': {'class': 'logging.StreamHandler',
                                              'formatter': 'ctlogFormatter',
                                              'stream': 'ext://sys.stdout'}},
                   'formatters': {'ctlogFormatter': {'format': '%(asctime)s %(levelname)-8s %(message)s'}}}
    logging.config.dictConfig(log_setting)
    lgr = logging.getLogger(__name__)
    return lgr


def main():
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    print(python_version())
    for dirname in ['build', 'dist', 'twsqlparser.egg-info']:
        clean_dir(dirname)
    for pkg in ['wheel', 'twine']:
        install_pkg(pkg)
    exec_cmd_in_batch('python setup.py sdist bdist_wheel')
    exec_cmd_in_batch('twine upload --repository testpypi dist/*')


logger = get_logger()


if __name__ == '__main__':
    main()
