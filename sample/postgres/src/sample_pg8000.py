#!/usr/bin/env python3
# (C) 2021 gomachssm

import os
import sys
import pg8000
import twsqlparser as twsp

import data_creator

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
pg8000.paramstyle = 'named'


def main():
    from PG8000Con import PG8000Con
    host = os.getenv('DBHOST', 'localhost')
    with PG8000Con(host=host, port=5432, user='postgres', password='password', database='postgres') as conn:
        cur = conn.cursor()
        path = os.path.abspath('./sample_insert.sql')
        params = data_creator.create_sample_param()
        truncate_table(cur)
        insert_with_twsp(cur, path, params)
        select_data(cur, 'select * from sample_lang')
        select_data_with_twsp(cur, os.path.abspath('sample_select_pg8000.sql'), {'lang_names': ('C', 'Go')})
        select_data_with_twsp(cur, os.path.abspath('sample_select_pg8000.sql'), {'lang_names': ['C', 'Go']})
        # does not execute in pg8000
        # select_data_with_twsp(cur, os.path.abspath('sample_select_pg8000.sql'), {'lang_names': {'C', 'Go'}})


def truncate_table(cur):
    cur.execute('truncate table sample_lang')


def insert_with_twsp(cur, path, params=None):
    sql, exec_param = twsp.parse_file(path, params)
    print(f'SQL  : {sql}')
    print(f'Param: {exec_param}')
    cur.execute(sql, exec_param)


def select_data_with_twsp(cur, path, params=None):
    sql, exec_param = twsp.parse_file(path, params)
    select_data(cur, sql, exec_param)


def select_data(cur, sql, param=None):
    print('')
    print('--- Execute SELECT ---')
    print(f'SQL  : {sql}')
    print(f'Param: {param}')
    cur.execute(sql, param)
    print('--- Results ---')
    headernames = [colinfo[0] for colinfo in cur.description]
    print(headernames)
    print('-' * len('["' + '", "'.join(headernames) + '"]'))
    for row in cur.fetchall():
        print(row)


if __name__ == '__main__':
    main()
