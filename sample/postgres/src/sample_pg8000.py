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
        sql, exec_param = twsp.parse_file(path, params)
        print('=== execute query ===============================')
        print(sql)
        print('=== query parameter =============================')
        print(exec_param)

        cur.execute('truncate table sample_lang')
        cur.execute(sql, exec_param)
        cur.execute('select * from sample_lang')
        print('=== select results ==============================')
        for row in cur.fetchall():
            print(row)


if __name__ == '__main__':
    main()
