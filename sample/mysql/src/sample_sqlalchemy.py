#!/usr/bin/env python3
# (C) 2021 gomachssm

import os
import sys
import sqlalchemy
import twsqlparser as twsp

import data_creator

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

USER = 'mysql'
PW = 'mysql'
DB = 'mysql'
PORT = 3306
HOST = os.getenv('DBHOST', 'localhost')


def main():
    engine = sqlalchemy.create_engine(f'mysql+mysqlconnector://{USER}:{PW}@{HOST}:{PORT}/{DB}?charset=utf8')
    with engine.connect() as conn:
        path = os.path.abspath('./sample_insert.sql')
        params = data_creator.create_sample_param()
        sql, exec_param = twsp.parse_file(path, params)
        print('=== execute query ===============================')
        print(sql)
        print('=== query parameter =============================')
        print(exec_param)
        conn.execute('truncate table sample_lang')
        # 'sqlalchemy.text()' is important, when use 'named' parameter.
        conn.execute(sqlalchemy.text(sql), exec_param)
        rows = conn.execute('select * from sample_lang')
        print('=== select results ==============================')
        for row in rows:
            print(row)


if __name__ == '__main__':
    main()
