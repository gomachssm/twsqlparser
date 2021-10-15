#!/usr/bin/env python3
# (C) 2021 gomachssm

import logging
import os
import pathlib
from copy import deepcopy
from uuid import uuid4
from functools import lru_cache

from .internal_exceptions import Msg, TwspException, TwspExecuteError, TwspValidateError
from .enums import ParamStyle, CommentType


logger = logging.getLogger(__name__)

NEWLINE_CHAR = '\n'

_TN = 'tmpnm'
_VL = 'value'
_DMY = '...dummy...'

_END = '/*end*/'
_FIND_TARGETS = ('"', "'", '(', '[', '{', '--', '/*', )
_BRACKET_PARE = {'[': ']', '(': ')', '{': '}'}
# ([{'"\ 以外の一般的な記号と空白文字
_EOP_SIMPLE_PARAM = ('!', '#', '$', '%', '&', ')', '-', '=', '^', '~',
                     '|', '@', '`', ';', '+', ':', '*', ']', '}',
                     ',', '/', '<', '>', '?', ' ',     # '.', '(', '_',
                     '\t', '\n', '\r', )
_EOP_END = (_END, )


def parse_file(file_path: str, query_params=None, delete_comment=True, encoding='utf-8', newline='\n',
               paramstyle: ParamStyle = None) -> (str, dict):
    """SQLファイルを読み込み、解析を行う

    Args:
        file_path (str): 実行対象SQLのファイルパス(必須)
        query_params (dict): SQL実行時に利用するパラメータ
        delete_comment (bool): True の場合、通常コメントを削除、 False の場合は削除しない
            デフォルトは True
        encoding (str): 対象ファイルの文字コード デフォルトは utf-8
        newline (str): 対象ファイルの改行コード (デフォルトは '\n')
        paramstyle (ParamStyle): 解析後のSQLパラメータ書式を決める。未指定時は `NAMED` と同じ扱い
    Returns:
        tuple(str, dict):
            str: 解析後のSQL
            dict: パラメータ更新後のdict
    """
    try:
        base_sql = _open_file(file_path, encoding=encoding)
        sql, qparams = parse_sql(base_sql, query_params, delete_comment=delete_comment, newline=newline,
                                 paramstyle=paramstyle)
        return sql, qparams
    except TwspException as e:
        logger.error(e.msg_txt)


def parse_sql(base_sql: str, query_params=None, delete_comment=True, newline='\n',
              paramstyle: ParamStyle = None) -> (str, dict):
    """SQLの解析を行う.

    Args :
        base_sql (str): 解析対象SQL(必須)
        query_params (dict): SQL実行時に利用するパラメータ
        delete_comment (bool): True の場合、通常コメントを削除、 False の場合は削除しない (デフォルトは True)
        newline (str): SQLに含まれる改行コード (デフォルトは '\n')
        paramstyle (ParamStyle): 解析後のSQLパラメータ書式を決める。未指定時は `NAMED` と同じ扱い

    Returns:
        tuple(str, dict):
            str: 解析後のSQL
            dict: パラメータ更新後のdict
    """
    global NEWLINE_CHAR
    NEWLINE_CHAR = newline
    pstyle = paramstyle or ParamStyle.NAMED
    _validate_paramstyle(pstyle)

    # PARAMSTYLEの値に応じたパラメータ書式のセット
    # TODO: グローバルではなく、引数で持ち回せるようにしたい
    prmfmt = pstyle.value
    try:
        qparams = deepcopy(query_params) if query_params else {}
        _is_collect_type('base_sql', base_sql, str)
        _is_collect_type('query_params', qparams, dict)
        # base_sql = _format_line_forifend(base_sql)
        sql, _, _ = _parse(base_sql, qparams, delete_comment, prmfmt)
        return sql, qparams
    except TwspException as e:
        logger.error(e)
        # logger.error(e.msg_txt)


def _parse(base_sql: str, qparams: dict, delete_comment: bool, prmfmt: str, eop=None, tmp_params=None,
           after_pcmt=False, ldng_sp_cnt=0) -> (str, int, int):
    """ SQLを解析してパラメータを埋め込む

    Args:
        base_sql (str): 元となるSQL
        qparams (dict): パラメータ
        delete_comment (bool): コメント削除フラグ
        eop (tuple->str or None): 解析終了文字 End of parse
        tmp_params (dict): for内の一時パラメータ default: None
        after_pcmt (bool): パラメータ直後フラグ default: False
        ldng_sp_cnt (int): 行頭から続く空白文字の個数 default: 0

    Returns:
        tuple:
            str: 構築したSQL
            int: 最後の改行から連続したスペースの個数
                1以上: その個数分のスペースが末尾に存在する
                0以下: 末尾にスペースが存在しない
            int: return時のインデックス
    """
    q = []
    max_idx = len(base_sql)
    i = 0
    tmp_params = tmp_params if tmp_params else {}
    while i < max_idx and not _startswith_eop(base_sql, i, eop):
        c, cc, i = _next_chars(base_sql, i, max_idx, eop)
        c, i, del_last_sp = _parse_switch_by_char(base_sql, c, cc, i, qparams, delete_comment, tmp_params, after_pcmt,
                                                  ldng_sp_cnt, prmfmt)
        if del_last_sp:
            q = _delete_last_space(q)
        ldng_sp_cnt = _update_blank_line(ldng_sp_cnt, c)
        q.append(c)

    result = ''.join(q)
    return result, ldng_sp_cnt, i


def _parse_switch_by_char(base_sql: str, c: str, cc: str, i: int, qparams: dict, delete_comment: bool,
                          tmp_params: dict, after_pcmt: bool, ldng_sp_cnt: int, prmfmt: str) -> (str, int, bool):
    del_last_sp = False
    if c in ("'", '"', '(', '[', '{'):
        c, i = _nextstring(c, base_sql, i, qparams, delete_comment, after_pcmt)
    elif cc == '--':
        # 行コメント -- の場合
        c, addi = _get_single_line_comment(base_sql[i - 1:], delete_comment)
        i += addi - 1
    elif cc == '/*':
        # 複数行コメント /*...*/ の場合
        c, addi, del_last_sp = _get_multi_line_comment(base_sql[i - 1:], qparams, delete_comment, tmp_params,
                                                       ldng_sp_cnt, prmfmt)
        i += addi - 1
    return c, i, del_last_sp


def _nxtchr(string: str, idx: int):
    return string[idx], idx + 1


def _fnd(string: str, target: str):
    index = string.find(target)
    return index if 0 <= index else len(string)


def _next_chars(string: str, idx: int, mxidx: int, eop=None) -> (str, str, int):
    targets = _FIND_TARGETS + eop if eop else _FIND_TARGETS
    min_idx = min([_fnd(string[idx:], tgt) for tgt in targets])
    if min_idx == 0:
        c, i = _nxtchr(string, idx)
        cc = f'{c}{string[i]}' if i < mxidx else None
    else:
        i = idx + min_idx
        c = string[idx:i]
        cc = c
    return c, cc, i


def _nextstring(c: str, base_sql: str, i: int, qparams: dict, delete_comment: bool, after_pcmt: bool) -> (str, int):
    addi = 0
    if c in ("'", '"'):
        # ' か " の文字列の場合
        c, addi = _nextquote(c, base_sql[i:])
    elif after_pcmt and c in ('(', '[', '{'):
        # パラメータ直後が括弧の場合
        c, addi = _nextbracket(c, base_sql[i:], qparams, delete_comment)
    return c, i + addi


def _nextquote(quote: str, sql_after_quote: str) -> (str, int):
    chars = [quote]
    max_idx = len(sql_after_quote) - 1
    addi = 0
    while addi <= max_idx:
        c, addi = _nxtchr(sql_after_quote, addi)
        if c == quote:
            # 2連続のクォート以外の場合、文字列はそこまで
            if max_idx <= addi or sql_after_quote[addi + 1] != quote:
                chars.append(c)
                break
            chars.append(c)
            c, addi = _nxtchr(sql_after_quote, addi)
        chars.append(c)
    quote_string = ''.join(chars)
    return quote_string, addi


def _nextbracket(openbrkt: str, sql_after_brkt: str, qparams: dict, delete_comment: bool) -> (str, int):
    closingbrkt = _BRACKET_PARE.get(openbrkt)

    chars = [openbrkt]
    max_idx = len(sql_after_brkt) - 1
    addi = 0
    while addi <= max_idx:
        c, addi = _nxtchr(sql_after_brkt, addi)
        chars.append(c)
        if c == closingbrkt:
            break
    bracket_strings = ''.join(chars)
    return bracket_strings, addi


def _get_single_line_comment(sql_comment: str, delete_comment: bool) -> (str, int):
    c, addi = _single_line_comment(sql_comment)
    if delete_comment:
        c = ''
    return c, addi


def _single_line_comment(sql_comment: str) -> (str, int):
    # この関数が呼び出される時、文字列は必ず -- から始まる
    maxlen = len(sql_comment)
    new_line_idx = sql_comment.find(NEWLINE_CHAR)
    new_line_idx = maxlen if new_line_idx < 0 else new_line_idx
    comment_string = sql_comment[:new_line_idx]
    return comment_string, new_line_idx


def _get_multi_line_comment(sql_comment: str, qparams: dict, delete_comment: bool, tmp_params: dict,
                            ldng_sp_cnt: int, prmfmt: str) -> (str, int, bool):
    c, addi, is_comment, delete_last_sp = _multi_line_comment(sql_comment, qparams, delete_comment, tmp_params,
                                                              ldng_sp_cnt, prmfmt)
    if is_comment and delete_comment:
        c = ''
    return c, addi, delete_last_sp


def _multi_line_comment(sql_comment: str, qparams: dict, delete_comment: bool, tmp_params: dict,
                        ldng_sp_cnt: int, prmfmt: str) -> (str, int, bool):
    # この関数が呼び出される時、文字列は必ず /* から始まる
    cmtype, comment_string = _check_comment_type(sql_comment)
    is_comment = False
    del_last_sp = False
    # ex: comment_string : "/*:parameter*/"
    #     after_comment  : "'hogehoge' from xxx"
    after_comment = sql_comment[len(comment_string):]
    if cmtype is CommentType.PARAM:        # /*:param*/
        comment_string, idx = _parse_param_comment(comment_string, after_comment, qparams, tmp_params, prmfmt)
    elif cmtype is CommentType.DIRECT:     # /*$param*/
        comment_string, idx = _parse_direct_comment(comment_string, after_comment, qparams, tmp_params, prmfmt)
    elif cmtype is CommentType.IFEND:      # /*%if ~*/
        # TODO: ELSE対応
        comment_string, idx, del_last_sp = _parse_if_comment(
            comment_string, after_comment, qparams, delete_comment, tmp_params, ldng_sp_cnt, prmfmt)
    elif cmtype is CommentType.FOREND:     # /*%for ~*/
        comment_string, idx, del_last_sp = _parse_for_comment(
            comment_string, after_comment, qparams, delete_comment, tmp_params, ldng_sp_cnt, prmfmt)
    elif cmtype is CommentType.NORMAL:
        is_comment = True
        idx = len(comment_string)
    else:
        raise TwspException(Msg.E0003, sql_comment)
    return comment_string, idx, is_comment, del_last_sp


def _parse_param_comment(comment_string: str, after_comment: str, qparams: dict, tmp_params: dict,
                         prmfmt: str) -> (str, int):
    """
    Args:
        comment_string (str): コメント部分の文字列
            ex: /*:any_parameter*/
        after_comment (str): コメント直後の文字列
    Returns:
        tuple:
            str:
            int:
    """
    bind_name, _, load_len = _parse_simple_comment(comment_string, after_comment, qparams, tmp_params, prmfmt)
    return bind_name, load_len


def _parse_direct_comment(comment_string: str, after_comment: str, qparams: dict, tmp_params: dict,
                          prmfmt: str) -> (str, int):
    """
    Args:
        comment_string (str): コメント部分の文字列
            ex: /*$any_parameter*/
        after_comment (str): コメント直後の文字列
        qparams (dict): SQL実行時に利用するパラメータ
    Returns:
        tuple:
            str:
            int:
    """
    merged_params = _merge_qparams(qparams, tmp_params)
    _, value, load_len = _parse_simple_comment(comment_string, after_comment, merged_params, {}, prmfmt)
    return value, load_len


def _parse_simple_comment(comment_string: str, after_comment: str, qparams: dict, tmp_params: dict,
                          prmfmt: str) -> (str, str, int):
    # comment_string: '/*:param*/' or '/*$param*/'
    param_name = comment_string[3:-2]
    bind_name, value = _update_qparams_if_exist_tmp(param_name, qparams, tmp_params, prmfmt)

    dummy_value, _, _ = _parse(after_comment, {}, False, prmfmt, eop=_EOP_SIMPLE_PARAM, after_pcmt=True)
    load_len = len(comment_string) + len(dummy_value)

    return bind_name, value, load_len


def _update_qparams_if_exist_tmp(param: str, qparams: dict, tmp_params: dict, prmfmt: str):
    tmp_name = tmp_params.get(param, {}).get(_TN)
    if _tmpp_is_dummy(tmp_params):
        # tmp_paramsがダミーの場合
        updated_bind_name = prmfmt.format(param)
        updated_param_value = ''
    elif tmp_name is not None:
        updated_bind_name = prmfmt.format(tmp_name)
        updated_param_value = tmp_params.get(param, {}).get(_VL)
        qparams[tmp_name] = updated_param_value
    else:
        updated_bind_name = prmfmt.format(param)
        updated_param_value = qparams.get(param)
    return updated_bind_name, f'{updated_param_value}'


def _parse_if_comment(comment_string: str, after_comment: str, qparams: dict, delete_comment: bool,
                      tmp_params: dict, ldng_sp_cnt: int, prmfmt: str) -> (str, int, bool):
    if_strings, after_idx, del_last_sp = _get_str_in_forif(after_comment, qparams, delete_comment, tmp_params,
                                                           ldng_sp_cnt, prmfmt)
    is_true = _execute_if_statement(comment_string[3:-2], qparams, tmp_params)
    output_value = ''.join(if_strings) if is_true else ''
    addi = len(comment_string) + after_idx
    return output_value, addi, del_last_sp


def _parse_for_comment(comment_string: str, after_comment: str, qparams: dict, delete_comment: bool,
                       tmp_params: dict, ldng_sp_cnt: int, prmfmt: str) -> (str, int, bool):
    # comment_string: /*%for x in list_obj*/
    # after_comment: .*/*end*/
    for_strings, after_idx, del_last_sp = [], 0, False
    # 最後の1回はfor~endまでの文字数カウントのため、ダミーで空dictが返される
    for tmp_params in _get_for_variable_names(comment_string, qparams, tmp_params):
        _for_strings, after_idx, del_last_sp = _get_str_in_forif(after_comment, qparams, delete_comment, tmp_params,
                                                                 ldng_sp_cnt, prmfmt)
        for_strings.append(_for_strings)
    # 最後の1ループ分は無視
    output_value = ''.join(for_strings[:-1])
    addi = len(comment_string) + after_idx
    return output_value, addi, del_last_sp


def _get_for_variable_names(for_comment: str, qparams: dict, tmp_params: dict) -> dict:
    """
    Args:
        for_comment (str): '/*%for x in xxx*/'
        qparams (dict):
        tmp_params (dict):
            ex1: {}
            ex2:
            ex3: {__DMY: True}
    Returns:

    """
    vnames = [v.strip() for v in for_comment[7:-2].split(' in ')[0].split(',')]
    merged_params = _merge_qparams(qparams, tmp_params)
    vnames_str = ",".join(vnames)
    for_statement = f'for {vnames_str} in []' if _tmpp_is_dummy(tmp_params) else for_comment[3:-2]
    try:
        values_list = eval(f'[({vnames_str}) {for_statement}]', {}, merged_params)
    except Exception as e:
        raise TwspExecuteError(Msg.E0008, e, for_statement)

    prefix = str(uuid4()).replace('-', '_')
    for tmp_variable in _enum_temp_variables(vnames, values_list, prefix):
        yield {**tmp_params, **tmp_variable}
    yield {_DMY: True}
    # 変数名のリスト
    # for a in range(3)なら
    # -> {'a': {'tmpnm': 'xxxxxxxxxxxx_0_a', 'value': 0}}
    # -> {'a': {'tmpnm': 'xxxxxxxxxxxx_1_a', 'value': 1}}
    # -> {'a': {'tmpnm': 'xxxxxxxxxxxx_2_a', 'value': 2}}
    # -> {__DMY: True}
    # for a,b,c in zip(['A', 'b'], ['I', 'j'], ['X', 'y'])なら、
    # -> {'a': {'tmpnm': 'xxxxxxxxxxxx_0_a', 'value': 'A'},
    #     'b': {'tmpnm': 'xxxxxxxxxxxx_0_b', 'value': 'I'},
    #     'c': {'tmpnm': 'xxxxxxxxxxxx_0_c', 'value': 'X'}}
    # -> {'a': {'tmpnm': 'xxxxxxxxxxxx_1_a', 'value': 'b'},
    #     'b': {'tmpnm': 'xxxxxxxxxxxx_1_b', 'value': 'j'},
    #     'c': {'tmpnm': 'xxxxxxxxxxxx_1_c', 'value': 'y'}}
    # -> {__DMY: True}


def _enum_temp_variables(vnames: list, values_list: list, prefix: str):
    if len(vnames) == 1:
        for vi, values in enumerate(values_list):
            vname = vnames[0]
            tmp_name = _gen_tmp_name(vname, vi, prefix)
            yield {vname: {_TN: tmp_name, _VL: values}}
    else:
        for vi, values in enumerate(values_list):
            tmpdct = {}
            for ni, vname in enumerate(vnames):
                tmp_name = _gen_tmp_name(vname, vi, prefix)
                tmpdct[vname] = {_TN: tmp_name, _VL: values[ni]}
            yield tmpdct


def _gen_tmp_name(vname: str, loop_count: int, prefix: str) -> str:
    name = f'{prefix}_{loop_count}_{vname}'
    return name


def _get_str_in_forif(after_comment: str, qparams: dict, delete_comment: bool, tmp_params: dict,
                      ldng_sp_cnt: int, prmfmt: str) -> (str, int, bool):
    """
    Args:
        after_comment (str): /*%for ~*/または/*%if ~*/の直後に続く文字列
        qparams (dict): パラメータ
        delete_comment (bool):
        tmp_params (dict):
        ldng_sp_cnt (int):
    Returns:

    """
    # for ~ end、や if ~ end に挟まれた文字を取得する
    nextq, after_idx, del_last_sp = _nxtq_in_forif(after_comment, ldng_sp_cnt)
    # 改行削除済みの場合、 ldng_sp_cnt は 0 から
    ldng_sp_cnt = -1 if after_comment == nextq else 0
    output_value, _, vlen = _parse(nextq, qparams, delete_comment, prmfmt, _EOP_END, tmp_params=tmp_params,
                                   ldng_sp_cnt=ldng_sp_cnt)
    nextq = nextq[vlen:]
    after_idx += vlen

    output_value, addi = _end_in_forif(output_value, nextq)
    after_idx += addi
    return output_value, after_idx, del_last_sp


def _nxtq_in_forif(nextq: str, ldng_sp_cnt: int) -> (str, int, bool):
    if 0 <= ldng_sp_cnt:
        nlidx = nextq.find(NEWLINE_CHAR) + 1
        if nextq[:nlidx].strip() == '':
            return nextq[nlidx:], nlidx, True
    return nextq, 0, False


def _end_in_forif(output_value: str, nextq: str) -> (str, int):
    # /*end*/が見つからずSQLの末尾に到達した場合
    if not nextq:
        return output_value, 0
    # nextq: '/*end*/\n   order by ~'
    # /*end*/ でsplitするのは1回のみ
    target_last_line = output_value.split(NEWLINE_CHAR)[-1]
    next_first_line = nextq.split(NEWLINE_CHAR, 1)[0]
    sp_stripped = f'{target_last_line}{next_first_line}'.strip(' ')
    if sp_stripped == _END:
        # /*end*/の行に含まれる文字がスペースのみの場合、次の行から読み込ませる
        newline_len = len(NEWLINE_CHAR)
        output_idx = len(output_value) - len(target_last_line)
        forif_string = output_value[:output_idx]
        add_idx = len(next_first_line) + newline_len
        return forif_string, add_idx
    else:
        # /*end*/までの文字数を返す len('/*end*/')
        return output_value, 7


def _is_continue(string: str, end_str: str):
    if not string or string.startswith(end_str):
        return False
    return True


def _execute_if_statement(statement: str, qparams: dict, tmp_params: dict) -> bool:
    # statement: "if BOOL_EXPRESSION"
    if _tmpp_is_dummy(tmp_params):
        return True
    try:
        tparams = {}
        for key, value in _tmpp_items(tmp_params):
            tparams[key] = value
        is_true = eval(f'True {statement} else False', {}, {**qparams, **tparams})
    except NameError as e:
        raise TwspExecuteError(Msg.E0005, e, statement)
    if type(is_true) != bool:
        raise TwspExecuteError(Msg.E0006, statement)
    return is_true


def _check_comment_type(sql_after_comment: str) -> (CommentType, str):
    # /*:param*/                    -> :param       利用できる文字は英数字とアンダースコア
    # /*$param*/                    -> {param}      利用できる文字は英数字とアンダースコア
    # /*%if a == b*/hoge/*end*/     -> 条件がTrueの場合、/*end*/までに挟まれた部分が出力
    # /*%for a in b*/and a /*end*/  -> and a and a and a and a ... iterate by b
    # other patterns are multi line comment.
    for ctyp in CommentType:
        matched = ctyp.value.findall(sql_after_comment)
        if len(matched) > 0:
            return ctyp, matched[0]


def __get_cache_maxsize() -> int:
    default_size = 20
    env_size = os.getenv('TWSP_CACHE_SIZE')
    try:
        size = int(env_size)
    except Exception:
        size = None
    return size if size else default_size


@lru_cache(maxsize=__get_cache_maxsize())
def _open_file(file_path, encoding='utf-8'):
    _is_collect_type('file_path', file_path, str)
    if not _is_absolute(file_path):
        raise TwspValidateError(Msg.E0002, file_path)
    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()


def _is_absolute(path):
    p = pathlib.Path(path)
    return p.is_absolute()


def _is_collect_type(argname, value, expected_type):
    if type(value) != expected_type:
        raise TwspValidateError(Msg.E0001, argname, expected_type, type(value))


def _startswith_eop(base_sql: str, i: int, eop: list) -> bool:
    if not eop:
        return False
    for e in eop:
        if base_sql[i:].startswith(f'{e}'):
            return True
    return False


def _update_blank_line(ldng_sp_cnt: int, c: str) -> int:
    if not c:
        return ldng_sp_cnt

    ridx = c.rfind(NEWLINE_CHAR)
    if ldng_sp_cnt < 0 and ridx < 0 == 1:
        return -1
    after_nl = c[ridx + 1:]
    if after_nl.lstrip(' ') == '':
        # 改行後、全部スペースの場合
        return len(after_nl)
    else:
        return -1


def _delete_last_space(q: list) -> list:
    idx = len(q) - 1
    while -1 < idx:
        idx_str = q[idx].rstrip(' ')
        if idx_str:
            q[idx] = idx_str
            break
        del q[idx]
        idx -= 1
    return q


# #######################################
# temp_params
# #######################################
def _tmpp_is_dummy(tmpp: dict) -> bool:
    return True if tmpp.get(_DMY) is True else False


def _tmpp_items(tmpp: dict) -> (any, any):
    for key, v in tmpp.items():
        value = v.get(_VL)
        yield key, value


def _merge_qparams(qparams: dict, tmp_params: dict) -> dict:
    if _tmpp_is_dummy(tmp_params):
        return {**qparams}

    merged_params = {**qparams}
    for key, value in _tmpp_items(tmp_params):
        merged_params[key] = value
    return merged_params


def _validate_paramstyle(paramstyle):
    if (not isinstance(paramstyle, ParamStyle)) or paramstyle not in ParamStyle:
        ps = [f'{p.__class__.__name__}.{p.name}' for p in ParamStyle]
        raise TwspValidateError(Msg.E0009, f'{", ".join(ps[:-1])}', ps[-1], paramstyle)
    return True
