#!/usr/bin/env python3
# (C) 2021 gomachssm

import datetime


def create_sample_param():
    base_data = [
        ('C',      1972, datetime.datetime.now()),
        ('D',      2001, datetime.datetime.now()),
        ('Erlang', 1986, datetime.datetime.now()),
        ('F#',     2005, datetime.datetime.now()),
        ('Go',     2009, datetime.datetime(2009, 1, 23, 4, 56, 7, 890123)),
    ]
    langs = [(i, *data) for i, data in enumerate(base_data)]
    params = {'langs': langs}
    return params
