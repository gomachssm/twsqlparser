#!/usr/bin/env python3
# (C) 2020 gomachssm

from messages import Msg

_NONETYPE_ = type(None)


class TwspException(Exception):
    """ twsqlparser内部で利用する例外の基底クラス """
    def __init__(self, msgenum=None, *args):
        """例外を作成する

        Args:
            msgenum (Msg): メッセージID
            params (list): メッセージで利用するパラメータ
        """
        arg1type = type(msgenum)
        if arg1type not in (Msg, _NONETYPE_):
            raise TypeError('arg1: msgenum type must be Msg or None.')
        self.msgid = msgenum
        self.args = args
        self.msg_txt = None if not msgenum else f'{msgenum.name} {msgenum.value.format(args)}'
        super(Exception, self).__init__(self.msg_txt)


class TwspValidateError(TwspException):
    def __init__(self, msgenum, *args):
        """検証例外

        Args:
            msgenum (messages.Msg): メッセージID
            params (list): メッセージで利用するパラメータ
        """
        super(TwspException, self).__init__(msgenum, *args)


class TwspExecuteError(TwspException):
    def __init__(self, msgenum, *args):
        """実行例外

        Args:
            msgenum (messages.Msg): メッセージID
            params (list): メッセージで利用するパラメータ
        """
        super(TwspException, self).__init__(msgenum, *args)
