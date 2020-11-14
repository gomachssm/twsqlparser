#!/usr/bin/env python3
# (C) 2020 gomachssm

import datetime
import os
import pg8000
import twsqlparser as twsp

pg8000.paramstyle = 'named'


def main():
    conn = pg8000.connect(user='postgres', password='password', database='time')
    loop = 50
    methods = [twspsimpleinsert, simple_insert, twspmultiinsert, exec_many]
    for mthd in methods:
        mthd(loop, conn)
    for mthd in reversed(methods):
        mthd(loop, conn)
    conn.close()


def twspmultiinsert(loop: int, conn):
    cur = conn.cursor()
    start = datetime.datetime.now().timestamp()
    for _ in range(loop):
        cur.execute('truncate table sample_lang')
        path = os.path.abspath('./sample_insert.sql')
        params = {'names': ['C', 'D', 'F#', 'Go', 'KQ']}
        sql, exec_param = twsp.parse_file(path, params)
        cur.execute(sql, exec_param)
        conn.commit()
    end = datetime.datetime.now().timestamp()
    print(f'twspmultiinsert: {end - start}')


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
        conn.commit()
    end = datetime.datetime.now().timestamp()
    print(f'twspsimpleinsert: {end - start}')


def simple_insert(loop: int, conn):
    cur = conn.cursor()
    start = datetime.datetime.now().timestamp()
    for _ in range(loop):
        cur.execute('truncate table sample_lang')
        names = ['C', 'D', 'F#', 'Go', 'KQ']
        sql = 'insert into sample_lang (name) values ( :name );'
        for name in names:
            cur.execute(sql, {'name': name})
        conn.commit()
    end = datetime.datetime.now().timestamp()
    print(f'simple_insert: {end - start}')


def exec_many(loop: int, conn):
    cur = conn.cursor()
    start = datetime.datetime.now().timestamp()
    for _ in range(loop):
        cur.execute('truncate table sample_lang')
        names = ['C', 'D', 'F#', 'Go', 'KQ']
        sql = 'insert into sample_lang (name) values ( :name );'
        params = ({'name': name} for name in names)
        cur.executemany(sql, params)
        conn.commit()
    end = datetime.datetime.now().timestamp()
    print(f'executemany: {end - start}')


if __name__ == '__main__':
    main()
