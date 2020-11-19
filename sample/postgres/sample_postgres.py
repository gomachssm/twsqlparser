#!/usr/bin/env python3
# (C) 2020 gomachssm

import os
import sys
import pg8000
import twsqlparser as twsp

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
pg8000.paramstyle = 'named'


def main():
    from .PG8000Con import PG8000Con
    with PG8000Con(host='localhost', port=5432, user='postgres', password='password', database='postgres') as conn:
        cur = conn.cursor()
        path = os.path.abspath('./sample_insert.sql')
        params = {'names': ['C', 'D', 'F#', 'Go', 'KQ']}
        sql, exec_param = twsp.parse_file(path, params)
        print(sql)
        print(exec_param)
        cur.execute('truncate table sample_lang')
        cur.execute(sql, exec_param)
        cur.execute('select * from sample_lang')
        for row in cur.fetchall():
            print(row)


if __name__ == '__main__':
    main()
