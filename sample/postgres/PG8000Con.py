#!/usr/bin/env python3
# (C) 2020 gomachssm

from pg8000 import Connection


class PG8000Con(Connection):
    """ pg8000.ConnectionクラスのWrapperクラス
    with構文で利用する際、例外なくwithを抜けた場合、コミットする。
    例外が発生しwithを抜ける場合、ロールバックする。
    それ以外の仕様はpg8000.Connectionと同様。
    """
    def __init__(self, user, **kwargs):
        super(PG8000Con, self).__init__(user, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._sock:
            if exc_type:
                self.rollback()
            else:
                self.commit()
            self.close()

    def __del__(self):
        if self._sock:
            self.close()
