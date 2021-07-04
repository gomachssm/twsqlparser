#!/usr/bin/env python3
# (C) 2021 gomachssm

import os
import sys
import sqlalchemy
import twsqlparser as twsp

import data_creator

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

USER = 'postgres'
PW = 'password'
DB = 'postgres'
PORT = 5432
HOST = os.getenv('DBHOST', 'localhost')


def main():
    engine = sqlalchemy.create_engine(f'postgresql://{USER}:{PW}@{HOST}:{PORT}/{DB}')
    with engine.connect() as conn:
        truncate_table(conn)

        path = os.path.abspath('./sample_insert.sql')
        params = data_creator.create_sample_param()
        insert_with_twsp(conn, path, params)
        # 'sqlalchemy.text()' is important, when use 'named' parameter.
        select_data(conn, 'select * from sample_lang')
        select_data_with_twsp(conn, os.path.abspath('./sample_select_alchemy.sql'), {'lang_names': ('C', 'Go')})
        # does not execute in sqlalchemy
        # select_data_with_twsp(conn, os.path.abspath('./sample_select_alchemy.sql'), {'lang_names': ['C', 'Go']})
        # select_data_with_twsp(conn, os.path.abspath('./sample_select_alchemy.sql'), {'lang_names': {'C', 'Go'}})


def truncate_table(conn):
    conn.execute('truncate table sample_lang')


def insert_with_twsp(conn, path, params=None):
    sql, exec_param = twsp.parse_file(path, params)
    print(f'SQL  : {sql}')
    print(f'Param: {exec_param}')
    conn.execute(sqlalchemy.text(sql), exec_param)


def select_data_with_twsp(conn, path, params=None):
    sql, exec_param = twsp.parse_file(path, params)
    select_data(conn, sql, exec_param)


def select_data(conn, sql, param=None):
    print('')
    print('--- Execute SELECT ---')
    print(f'SQL  : {sql}')
    print(f'Param: {param}')
    rows = conn.execute(sqlalchemy.text(sql), param)
    print('--- Results ---')
    for row in rows:
        print(row)


if __name__ == '__main__':
    main()
