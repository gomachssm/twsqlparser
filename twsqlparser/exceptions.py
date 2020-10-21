#!/usr/bin/env python3
# (C) 2020 gomachssm

from enum import Enum, unique


@unique
class Msg(Enum):
    E0001 = 'Arg {0} must be {1}, but {2}'
    E0002 = 'Arg path is must be absolute: {0}'
    E0003 = 'Argument did not match any of the comment regular expressions: {0}'
    E0004 = 'Character exceeding the maximum length:{0} was found in the argument. {1}'
    E0005 = '{0}. %if statement is "{1}"'
    E0006 = 'Statement result type is not bool. %if statement is "{0}"'
    E0007 = 'Format must be "/*%for ~ in ~*/", value is {0}'
    E0008 = '{0}. %for statement is "{1}"'


class TwspException(Exception):
    def __init__(self, msgenum=None, *args):
        """
        Args:
            msgenum (Msg):
            params (list):
        """
        self.msgid = msgenum
        self.args = args
        self.msg_txt = None if not msgenum else f'{msgenum.name} {msgenum.value.format(args)}'
        super(Exception, self).__init__(self.msg_txt)


class TwspValidateError(TwspException):
    def __init__(self, msgenum, *args):
        super(TwspException, self).__init__(msgenum, *args)


class TwspExecuteError(TwspException):
    def __init__(self, msgenum, *args):
        super(TwspException, self).__init__(msgenum, *args)
