#!/usr/bin/env python3
# (C) 2020 gomachssm

import os
import pg8000
import twsqlparser as twsp

pg8000.paramstyle = 'named'

conn = pg8000.connect(user='postgres', password='password', database='time')
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
conn.commit()
conn.close()



