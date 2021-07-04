#!/usr/bin/env python3
# (C) 2021 gomachssm

import os
import twsqlparser as twsp
import data_creator


def execute_samplecode(executable_obj):
    insert_data(executable_obj)


def insert_data(executable_obj):
    """サンプルDBにデータを登録します

    Args:
        executable_obj:

    Returns:

    """
    path = os.path.abspath('./sample_insert.sql')
    params = data_creator.create_sample_param()
    sql, exec_param = twsp.parse_file(path, params)
    print('=== execute query ===============================')
    print(sql)
    print('=== query parameter =============================')
    print(exec_param)

    executable_obj.execute('truncate table sample_lang')
    executable_obj.execute(sql, exec_param)
    executable_obj.execute('select * from sample_lang')
    print('=== select results ==============================')
    for row in executable_obj.fetchall():
        print(row)
