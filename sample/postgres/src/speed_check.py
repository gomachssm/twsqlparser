#!/usr/bin/env python3
# (C) 2020 gomachssm

import os
import sys
import datetime
import pg8000
import twsqlparser as twsp

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

pg8000.paramstyle = 'named'


def main():
    from .PG8000Con import PG8000Con
    loop = 50
    methods = [twspsimpleinsert, simple_insert, twspmultiinsert, exec_many]
    timemap = {}
    with PG8000Con(host='localhost', port=5432, user='postgres', password='password', database='postgres') as conn:
        for mthd in [*methods, *(reversed(methods))]:
            msec = mthd(loop, conn)
            timemap[mthd.__name__] = timemap.get(mthd.__name__, 0) + msec
    print('====================')
    for k, v in timemap.items():
        print(f'{k:<16}\t{v}')


def twspmultiinsert(loop: int, conn):
    cur = conn.cursor()
    start = datetime.datetime.now().timestamp()
    for _ in range(loop):
        cur.execute('truncate table sample_lang')
        path = os.path.abspath('./sample_insert.sql')
        params = {'names': ['C', 'D', 'F#', 'Go', 'KQ']}
        sql, exec_param = twsp.parse_file(path, params)
        cur.execute(sql, exec_param)
    end = datetime.datetime.now().timestamp()
    conn.commit()
    msec = end - start
    print(f'twspmultiinsert: {msec}')
    return msec


def twspsimpleinsert(loop: int, conn):
    cur = conn.cursor()
    start = datetime.datetime.now().timestamp()
    for _ in range(loop):
        cur.execute('truncate table sample_lang')
        base_sql = "insert into sample_lang (name) values ( /*:name*/'hoge' );"
        names = ['C', 'D', 'F#', 'Go', 'KQ']
        for name in names:
            sql, exec_param = twsp.parse_sql(base_sql, {'name': name})
            cur.execute(sql, {'name': name})
    end = datetime.datetime.now().timestamp()
    conn.commit()
    msec = end - start
    print(f'twspsimpleinsert: {msec}')
    return msec


def simple_insert(loop: int, conn):
    cur = conn.cursor()
    start = datetime.datetime.now().timestamp()
    for _ in range(loop):
        cur.execute('truncate table sample_lang')
        names = ['C', 'D', 'F#', 'Go', 'KQ']
        sql = 'insert into sample_lang (name) values ( :name );'
        for name in names:
            cur.execute(sql, {'name': name})
    end = datetime.datetime.now().timestamp()
    conn.commit()
    msec = end - start
    print(f'simple_insert: {msec}')
    return msec


def exec_many(loop: int, conn):
    cur = conn.cursor()
    start = datetime.datetime.now().timestamp()
    for _ in range(loop):
        cur.execute('truncate table sample_lang')
        names = ['C', 'D', 'F#', 'Go', 'KQ']
        sql = 'insert into sample_lang (name) values ( :name );'
        params = ({'name': name} for name in names)
        cur.executemany(sql, params)
    end = datetime.datetime.now().timestamp()
    conn.commit()
    msec = end - start
    print(f'executemany: {msec}')
    return msec


if __name__ == '__main__':
    main()
