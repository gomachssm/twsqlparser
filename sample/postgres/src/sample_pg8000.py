#!/usr/bin/env python3
# (C) 2021 gomachssm

import os
import sys
import pg8000
import twsqlparser as twsp
from datetime import datetime as dt
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
pg8000.paramstyle = 'named'


def main():
    from PG8000Con import PG8000Con
    host = os.getenv('DBHOST', 'localhost')
    with PG8000Con(host=host, port=5432, user='postgres', password='password', database='postgres') as conn:
        cur = conn.cursor()
        path = os.path.abspath('./sample_insert.sql')
        params = {'langs': [
            (0, 'C',      1972, dt.now()),
            (1, 'D',      2001, dt.now()),
            (2, 'Erlang', 1986, dt.now()),
            (3, 'F#',     2005, dt.now()),
            (4, 'Go',     2009, dt(2009, 1, 23, 4, 56, 7, 890123)),
        ]}
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
