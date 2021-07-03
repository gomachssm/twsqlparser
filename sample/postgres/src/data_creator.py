#!/usr/bin/env python3
# (C) 2021 gomachssm

import datetime


def create_sample_param():
    base_data = []
    base_data.append(('C',      1972, datetime.datetime.now()))
    base_data.append(('D',      2001, datetime.datetime.now()))
    base_data.append(('Erlang', 1986, datetime.datetime.now()))
    base_data.append(('F#',     2005, datetime.datetime.now()))
    base_data.append(('Go',     2009, datetime.datetime(2009, 1, 23, 4, 56, 7, 890123)))
    langs = [(i, *data) for i, data in enumerate(base_data)]
    params = {'langs': langs}
    return params
