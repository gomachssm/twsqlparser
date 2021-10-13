#!/usr/bin/env python3
# (C) 2021 gomachssm
import re
from enum import Enum

_REG_PARAM = r'/\*:[a-zA-Z0-9_]*\*/'
_REG_DIRECT = r'/\*\$[a-zA-Z0-9_]*\*/'
_REG_IF = r'/\*%if .+?\*/'
_REG_FOR = r'/\*%for .+? in .+?\*/'
_REG_END = r'/\*end\*/'


class ParamStyle(Enum):
    NAMED = ':{0}'
    PYFORMAT = '%({0})s'


class CommentType(Enum):
    # :~*/ に一致する場合
    PARAM = re.compile(f'^{_REG_PARAM}')
    # $~*/ に一致する場合
    DIRECT = re.compile(f'^{_REG_DIRECT}')
    # %if ~ */ に一致する場合
    IFEND = re.compile(f'^{_REG_IF}')
    # %for ~ */ に一致する場合
    FOREND = re.compile(f'^{_REG_FOR}')
    # 最初の */まで
    NORMAL = re.compile(r'^/\*.*?\*/', re.DOTALL)
