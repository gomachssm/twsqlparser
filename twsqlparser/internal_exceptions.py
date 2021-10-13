#!/usr/bin/env python3
# (C) 2021 gomachssm

import enum

_NONETYPE_ = type(None)


@enum.unique
class Msg(enum.Enum):
    E0001 = 'Arg {0} must be {1}, but {2}'
    E0002 = 'Arg path is must be absolute: {0}'
    E0003 = 'Argument did not match any of the comment regular expressions: {0}'
    E0004 = 'Character exceeding the maximum length:{0} was found in the argument. {1}'
    E0005 = '{0}. %if statement is "{1}"'
    E0006 = 'Statement result type is not bool. %if statement is "{0}"'
    E0007 = 'Format must be "/*%for ~ in ~*/", value is {0}'
    E0008 = '{0}. %for statement is "{1}"'
    E0009 = 'Variable "paramstyle" must be either {0} or {1}, but "{2}".'


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
