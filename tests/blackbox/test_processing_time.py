#!/usr/bin/env python3
# (C) 2020 gomachssm

import datetime
import os
import pytest
import sys

from twsqlparser import twsp

DIRNAME = os.path.abspath(os.path.dirname(__file__))


def has_param(sopt):
    """ pytest skip用
    指定された短縮オプションが含まれる場合だけテストする
    Returns:

    """
    args = [arg for arg in sys.argv[1:] if arg[0] == '-']
    for param in args:
        if param.startswith('--'):
            continue
        if param[0] == '-':
            if param.find(sopt) >= 0:
                # オプション有りなのでテストする
                return False
        else:
            break
    # pytest skip
    return True


@pytest.mark.skipif(has_param('k'), reason='pytestskip')
def test_exec_speed_100loop():
    # 実行環境、ホストの負荷によって結果が左右されるため、このテストケースは通常実施しない
    # 性能改善を実施する場合に限り、変更前の平均実行時間をassertの条件とし、
    # 変更後の実行時間を計測するために利用する
    pathlist = [absp('./data/input/example1_if.sql'),
                absp('./data/input/example2_for.sql'),
                absp('./data/input/nested_for.sql'), ]
    params = {'table_name': 'TABNAME',
              't_param': True, 'f_param': False,
              'c1': "'ABC'", 'c2': "'IJK'",
              'dct': {'k1': 'v1', 'k2': 'v2', 'k3': 'v3', 'k4': 'v4', 'k5': 'v5'}}
    pstimes = []
    for _ in range(10):
        start = datetime.datetime.now().timestamp()
        for _ in range(100):
            for input_path in pathlist:
                _, _ = twsp.parse_file(input_path, params, False)
        end = datetime.datetime.now().timestamp()
        pstime = end - start
        print(pstime)
        pstimes.append(pstime)
    avg_sec = sum(pstimes) / len(pstimes)
    assert avg_sec <= 0.57, pstimes


def absp(p):
    return os.path.join(DIRNAME, p)


if __name__ == '__main__':
    pytest.main(['--lf'])
