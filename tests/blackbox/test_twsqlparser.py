#!/usr/bin/env python3
# (C) 2020 gomachssm

import os
import pytest
import unittest.mock

from twsqlparser import twsp

DIRNAME = os.path.abspath(os.path.dirname(__file__))
UUID4PATH = 'twsqlparser.twsp.uuid4'
called_count = 0
DELETE_PATTERN = [False, True]


class ExpSql:
    def __init__(self, inputsql, exp_delete_comment_false=None, exp_delete_comment_true=None, add_params=None):
        self.__inputsql = inputsql
        self.__qfalse = exp_delete_comment_false if exp_delete_comment_false else self.__inputsql
        self.__qtrue = exp_delete_comment_true if exp_delete_comment_true else self.__qfalse
        self.params = add_params if add_params else {}

    def sql(self):
        return self.__inputsql

    def expected(self, delete_comment=False):
        return self.__qtrue if delete_comment else self.__qfalse


@pytest.fixture(scope='function', autouse=True)
def __reset_count():
    global called_count
    called_count = 0
    yield


def mockid():
    global called_count
    result = f'xxxxxx{called_count}'[-6:]
    called_count += 1
    return result


@pytest.mark.parametrize('bs, qp, dc, eop, ap, lsc, expr, expl, expi', [
    ('hoge', {}, False, None, False, -1, 'hoge', -1, 4),
    ('ho/*end*/ge', {}, False, [twsp._END], False, -1, 'ho', -1, 2),
    ('"ho/*end*/"ge', {}, False, [twsp._END], False, -1, '"ho/*end*/"ge', -1, 13),
])
def test_unit__parse(bs, qp, dc, eop, ap, lsc, expr, expl, expi):
    result, ldng_sp_cnt, idx = twsp._parse(bs, qp, dc, eop, ap, lsc)
    assert result == expr
    assert ldng_sp_cnt == expl
    assert idx == expi


@pytest.mark.parametrize('s', [
    ExpSql("select a from dual"),
    ExpSql("select b "),
    ExpSql("select c"),
])
def test_parse_sql_simple(s):
    actual, rparam = twsp.parse_sql(s.sql(), {})
    assert_sql_oneline(actual, s.expected(), s)
    assert rparam == {}


@pytest.mark.parametrize('s', [
    ExpSql("select '' from dual"),
    ExpSql("select '""' from dual"),
    ExpSql("select '''a''' from dual"),
    ExpSql("select '''''' from dual"),
    ExpSql("select '\"''\"\"''' as \"'\"\"x\"\"'\" from dual"),
])
def test_parse_sql_quotes(s):
    actual, rparam = twsp.parse_sql(s.sql(), {})
    assert_sql_oneline(actual, s.expected(), s.sql())
    assert rparam == {}


@pytest.mark.parametrize('q', [
    ExpSql("select--\n1--",
           "select--\n1--", "select\n1"),
    ExpSql("select -- comment\n 1 from dual",
           "select -- comment\n 1 from dual", "select \n 1 from dual"),
    ExpSql("select--comment\n1 from dual",
           "select--comment\n1 from dual", "select\n1 from dual"),
    ExpSql("select\n-- comment\n 1 from dual",
           "select\n-- comment\n 1 from dual", "select\n\n 1 from dual"),
    ExpSql("select\n-- comment 1 from dual",
           "select\n-- comment 1 from dual", "select\n"),
    ExpSql("select\n-- comment\n1--hoge\nfrom\ndual",
           "select\n-- comment\n1--hoge\nfrom\ndual", "select\n\n1\nfrom\ndual"),
    ExpSql("select\n---comment\n1--#hoge\nfrom\ndual",
           "select\n---comment\n1--#hoge\nfrom\ndual", "select\n\n1\nfrom\ndual"),
])
@pytest.mark.parametrize('delete_comment', DELETE_PATTERN)
def test_parse_singleline_comment(q, delete_comment):
    actual, rparam = twsp.parse_sql(q.sql(), {}, delete_comment)
    assert_sql_oneline(actual, q.expected(delete_comment), (delete_comment, q.sql()))
    assert rparam == {}


@pytest.mark.parametrize('q', [
    ExpSql("select /*:p1*/ from a", "select :p1 from a"),
    ExpSql("select /*:p1*/\n from a", "select :p1\n from a"),
    ExpSql("select /*:p1*/12345 from a", "select :p1 from a"),
    ExpSql("select /*:p1*/'abc def' from a", "select :p1 from a"),
    ExpSql("select /*:p1*/0 from a where c1 = /*:p2*/'x'", "select :p1 from a where c1 = :p2"),
    ExpSql("select /*:p1*/'foo bar' from a where c1 = /*:p2*/0", "select :p1 from a where c1 = :p2"),
])
def test_parse_multicomment_param(q):
    params = {'p1': 'A', 'p2': 'B', 'p3': 'C'}
    actual, rparam = twsp.parse_sql(q.sql(), params, False)
    assert_sql_oneline(actual, q.expected(), q.sql())
    assert rparam == params


@pytest.mark.parametrize('q', [
    ExpSql("select 'x' from a where c1 in /*:p3*/(0,1,2)", "select 'x' from a where c1 in :p3"),
    ExpSql("select 'x' from a where c1 in /*:p3*/(0, 1, 2)", "select 'x' from a where c1 in :p3"),
    ExpSql("select /*:p1*/9, /*:p2*/, /*:p3*/9 from a", "select :p1, :p2, :p3 from a"),
    ExpSql("select 1 from a where x in (/*:p1*/9, /*:p2*/, /*:p3*/9)", "select 1 from a where x in (:p1, :p2, :p3)"),
])
def test_parse_multicomment_param_brkt(q):
    params = {'p1': 'A', 'p2': 'B', 'p3': 'C'}
    actual, rparam = twsp.parse_sql(q.sql(), params, False)
    assert_sql_oneline(actual, q.expected(), q.sql())
    assert rparam == params


@pytest.mark.parametrize('q', [
    ExpSql("select /*$p1*/ from a", "select A from a"),
    ExpSql("select /*$p1*/\n from a", "select A\n from a"),
    ExpSql("select /*$p1*/12345 from a", "select A from a"),
    ExpSql("select /*$p1*/'abc def' from a", "select A from a"),
    ExpSql("select /*$p1*/0 from a where c1 = /*$p2*/'x'", "select A from a where c1 = B"),
    ExpSql("select /*$p1*/'foo bar' from a where c1 = /*$p2*/0", "select A from a where c1 = B"),
])
def test_parse_multicomment_direct(q):
    params = {'p1': 'A', 'p2': 'B', 'p3': (7, 8, 9)}
    actual, rparam = twsp.parse_sql(q.sql(), params, False)
    assert_sql_oneline(actual, q.expected(), q.sql())
    assert rparam == params


@pytest.mark.parametrize('q', [
    ExpSql("select 'x' from a where c1 in /*$p3*/(0,1,2)", "select 'x' from a where c1 in (7, 8, 9)"),
    ExpSql("select 'x' from a where c1 in /*$p3*/(0, 1, 2)", "select 'x' from a where c1 in (7, 8, 9)"),
    ExpSql("select /*$p1*/9, /*$p2*/, /*$p3*/9 from a", "select A, B, (7, 8, 9) from a"),
    ExpSql("select 1 from a where x in (/*$p1*/9, /*$p2*/, /*$p3*/9)", "select 1 from a where x in (A, B, (7, 8, 9))"),
])
def test_parse_multicomment_direct_brkt(q):
    params = {'p1': 'A', 'p2': 'B', 'p3': (7, 8, 9)}
    actual, rparam = twsp.parse_sql(q.sql(), params, False)
    assert_sql_oneline(actual, q.expected(), q.sql())
    assert rparam == params


@pytest.mark.parametrize('q', [
    ExpSql("select /*%if p1*/0/*end*//*%if not p1*/1/*end*/ from a", "select 0 from a"),
    ExpSql("select /*%if not p1*/0/*end*//*%if p1*/1/*end*/ from a", "select 1 from a"),
    ExpSql("select /*%if p1 == 'A'*/0/*end*/ from a", "select 0 from a"),
    ExpSql("select /*%if p1 != 'A'*/0/*end*/ from a", "select  from a"),
    # True/Falseが直接埋め込まれている(普通無い)
    ExpSql("select /*%if True*/0/*end*/ from a", "select 0 from a"),
    ExpSql("select /*%if False*/0/*end*/ from a", "select  from a"),
    # parameterが空判定されるパターン
    ExpSql("select /*%if not p4*/\n0\n/*end*/ from a", "select \n0\n from a"),
    ExpSql("select /*%if not p5*/0/*end*/ from a", "select 0 from a"),
    ExpSql("select /*%if not p6*/0/*end*/ from a", "select 0 from a"),
    ExpSql("select /*%if not p7*/0/*end*/ from a", "select 0 from a"),
    ExpSql("select\n/*%if p4*/\n0\n/*end*/\nfrom a", "select\nfrom a"),
    ExpSql("select /*%if p5*/0/*end*/ from a", "select  from a"),
    ExpSql("select /*%if p6*/0/*end*/ from a", "select  from a"),
    ExpSql("select /*%if p7*/0/*end*/ from a", "select  from a"),
    # TODO: ELSE
])
def test_parse_multicomment_if_no_nest(q):
    params = {'p1': 'A', 'p2': 'B', 'p3': (7, 8, 9), 'p4': None, 'p5': 0, 'p6': {}, 'p7': [],
              'px1': [1, 2, 3], 'px2': {'a': 'ho', 'b': 'ge'},
              'px3': [{'a': 'ho1', 'b': 'ge1'}, {'a': 'ho2', 'b': 'ge2'}, {'a': 'ho3', 'b': 'ge3'}]}
    actual, rparam = twsp.parse_sql(q.sql(), params, False)
    assert_sql_oneline(actual, q.expected(), q.sql())
    assert rparam == params


@pytest.mark.parametrize('q', [
    # ExpSql(input, when_delete_comment_false, when_delete_comment_true)
    # has '--'
    ExpSql("select /*%if not p4*/--\n0--\n/*end*/ from a",    # if not None
           "select --\n0--\n from a", "select \n0\n from a"),
    ExpSql("select /*%if p4*/--\n0--\n/*end*/ from a",    # if None
           "select  from a", "select  from a"),
    # has '--', but no linefeed. = not found '/*end*/'.
    ExpSql("select /*%if not p4*/--0/*end*/ from a",  # if not None
           "select --0/*end*/ from a",
           "select "),
    ExpSql("select /*%if p4*/--0/*end*/ from a",      # if None
           "select "),
    # has '/* normal comment */'
    ExpSql("select /*%if p1*//**com*/0/**ment*//*end*/ from a",     # if 'A'
           "select /**com*/0/**ment*/ from a",
           "select 0 from a"),
    ExpSql("""\
select
  1
  /*%if p1*/
    /*%if p2*/, 2/*end*/
    /*%if p4 is None*/, 3/*end*/
  /*end*/
from a""", """\
select
  1
    , 2
    , 3
from a"""),
])
@pytest.mark.parametrize('delete_comment', DELETE_PATTERN)
def test_parse_multicomment_if_nest(delete_comment, q):
    params = {'p1': 'A', 'p2': 'B', 'p3': (7, 8, 9), 'p4': None, 'p5': 0, 'p6': {}, 'p7': [],
              'px1': [1, 2, 3], 'px2': {'a': 'ho', 'b': 'ge'},
              'px3': [{'a': 'ho1', 'b': 'ge1'}, {'a': 'ho2', 'b': 'ge2'}, {'a': 'ho3', 'b': 'ge3'}]}
    actual, rparam = twsp.parse_sql(q.sql(), params, delete_comment)
    assert_sql_oneline(actual, q.expected(delete_comment), (delete_comment, q.sql()))
    assert rparam == params


@pytest.mark.parametrize('q', [
    # ExpSql(input, when_delete_comment_false, when_delete_comment_true)
    # has '--'
    ExpSql("select 1/*%for a in p7*/--\n, 0--\n/*end*/ from a",  # p7 = []
           "select 1 from a"),
    ExpSql("select 1/*%for a in px1*/--\n, 0--\n/*end*/ from a",  # px1 = [1, 2, 3]
           "select 1--\n, 0--\n--\n, 0--\n--\n, 0--\n from a",
           "select 1\n, 0\n\n, 0\n\n, 0\n from a"),
    ExpSql("select 1/*%for a in px3*/--\n, 0--\n/*end*/ from a",  # px3 = [{'a': 'ho1', 'b': 'ge1'},
           "select 1--\n, 0--\n--\n, 0--\n--\n, 0--\n from a",    # #      {'a': 'ho2', 'b': 'ge2'},
           "select 1\n, 0\n\n, 0\n\n, 0\n from a"),               # #      {'a': 'ho3', 'b': 'ge3'}]
    ExpSql("select 1/*%for k, v in px2.items()*/--\n, 0--\n/*end*/ from a",  # px2 = {'a': 'ho', 'b': 'ge'}
           "select 1--\n, 0--\n--\n, 0--\n from a",
           "select 1\n, 0\n\n, 0\n from a"),
])
@pytest.mark.parametrize('delete_comment', DELETE_PATTERN)
def test_parse_multicomment_for_no_nest_no_param(q, delete_comment):
    params = {'p1': 'A', 'p2': 'B', 'p3': (7, 8, 9), 'p4': None, 'p5': 0, 'p6': {}, 'p7': [],
              'px1': [1, 2, 3], 'px2': {'a': 'ho', 'b': 'ge'},
              'px3': [{'a': 'ho1', 'b': 'ge1'}, {'a': 'ho2', 'b': 'ge2'}, {'a': 'ho3', 'b': 'ge3'}]}
    actual, rparam = twsp.parse_sql(q.sql(), params, delete_comment)
    assert_sql_oneline(actual, q.expected(delete_comment), (delete_comment, q.sql()))


@pytest.mark.parametrize('q', [
    # ExpSql(input, when_delete_comment_false, when_delete_comment_true)
    # has '--'  case 0-2 # p7 = [], px1 = [1, 2, 3]
    ExpSql("select 1/*%for a in p7*/--\n, /*:a*/'xxx'--\n/*end*/ from a",
           "select 1 from a"),
    ExpSql("select 1/*%for a in px1*/--\n, /*:a*/'xxx'--\n/*end*/ from a",
           "select 1--\n, :xxxxx0_0_a--\n--\n, :xxxxx0_1_a--\n--\n, :xxxxx0_2_a--\n from a",
           "select 1\n, :xxxxx0_0_a\n\n, :xxxxx0_1_a\n\n, :xxxxx0_2_a\n from a",
           add_params={'xxxxx0_0_a': 1, 'xxxxx0_1_a': 2, 'xxxxx0_2_a': 3}),
    ExpSql("select 1/*%for a in px1*/--\n, /*$a*/'xxx'--\n/*end*/ from a",
           "select 1--\n, 1--\n--\n, 2--\n--\n, 3--\n from a",
           "select 1\n, 1\n\n, 2\n\n, 3\n from a"),
    # if    case 3-5 # p7 = [], px1 = [1, 2, 3]
    ExpSql("select 1/*%for a in p7*//*%if a % 2 == 1*/--\n, /*:a*/'xxx'--\n/*end*//*end*/ from a",
           "select 1 from a"),
    ExpSql("select 1/*%for a in px1*//*%if a % 2 == 1*/--\n, /*:a*/'xxx'--\n/*end*//*end*/ from a",
           "select 1--\n, :xxxxx0_0_a--\n--\n, :xxxxx0_2_a--\n from a",
           "select 1\n, :xxxxx0_0_a\n\n, :xxxxx0_2_a\n from a",
           add_params={'xxxxx0_0_a': 1, 'xxxxx0_1_a': 2, 'xxxxx0_2_a': 3}),
    ExpSql("select 1/*%for a in px1*//*%if a % 2 == 1*/--\n, /*$a*/'xxx'--\n/*end*//*end*/ from a",
           "select 1--\n, 1--\n--\n, 3--\n from a",
           "select 1\n, 1\n\n, 3\n from a"),
    # case 6-8 # for in for  # px3 = [{'a': 'ho1', 'b': 'ge1'}, {'a': 'ho2', 'b': 'ge2'}, {'a': 'ho3', 'b': 'ge3'}]
    ExpSql("select 1/*%for dct in px3*//*%for k, v in dct.items()*//*%if v in ('ho1', 'ge3')*/"
           ", "
           "/*%if v == 'ho1'*//*:k*/'aaa'/*end*/"
           "/*%if v == 'ge3'*//*$k*/'aaa'/*end*//*end*//*end*//*end*/ from a",
           "select 1, :xxxxx1_0_k, b from a",
           add_params={'xxxxx1_0_k': 'a', 'xxxxx1_1_k': 'b', 'xxxxx2_0_k': 'a', 'xxxxx2_1_k': 'b',
                       'xxxxx3_0_k': 'a', 'xxxxx3_1_k': 'b', }),
    ExpSql("select 1/*%for p1 in px4*//*%for p2 in p1*//*%for p3 in p2*/, /*:p3*/'para3' , /*$p3*/'para3'"
           "/*end*//*end*//*end*/, /*$p1*/'para1' , /*$p2*/'para2' , /*$p3*/'para3' from a",
           "select 1, :xxxxx2_0_p3 , 111, :xxxxx2_1_p3 , 112, :xxxxx3_0_p3 , 121, :xxxxx3_1_p3 , 122"
           ", :xxxxx6_0_p3 , 211, :xxxxx6_1_p3 , 212, :xxxxx7_0_p3 , 221, :xxxxx7_1_p3 , 222"
           ", :xxxx10_0_p3 , 311, :xxxx10_1_p3 , 312, :xxxx11_0_p3 , 321, :xxxx11_1_p3 , 322"
           ", A , B , (7, 8, 9) from a",
           add_params={'xxxxx2_0_p3': 111, 'xxxxx2_1_p3': 112, 'xxxxx3_0_p3': 121, 'xxxxx3_1_p3': 122,
                       'xxxxx6_0_p3': 211, 'xxxxx6_1_p3': 212, 'xxxxx7_0_p3': 221, 'xxxxx7_1_p3': 222,
                       'xxxx10_0_p3': 311, 'xxxx10_1_p3': 312, 'xxxx11_0_p3': 321, 'xxxx11_1_p3': 322}),
    ExpSql("select 1 from x where 1 = 1/*%for k, v in px2.items()*/ and col in (/*:k*/'key', /*:v*/'value')/*end*/",
           "select 1 from x where 1 = 1 and col in (:xxxxx0_0_k, :xxxxx0_0_v) and col in (:xxxxx0_1_k, :xxxxx0_1_v)",
           add_params={'xxxxx0_0_k': 'a', 'xxxxx0_0_v': 'ho', 'xxxxx0_1_k': 'b', 'xxxxx0_1_v': 'ge'})
])
@pytest.mark.parametrize('delete_comment', DELETE_PATTERN)
def test_parse_multicomment_for_nested_param(q, delete_comment):
    params = {'p1': 'A', 'p2': 'B', 'p3': (7, 8, 9), 'p4': None, 'p5': 0, 'p6': {}, 'p7': [],
              'px1': [1, 2, 3], 'px2': {'a': 'ho', 'b': 'ge'},
              'px3': [{'a': 'ho1', 'b': 'ge1'}, {'a': 'ho2', 'b': 'ge2'}, {'a': 'ho3', 'b': 'ge3'}],
              'px4': [[[111, 112], [121, 122]], [[211, 212], [221, 222]], [[311, 312], [321, 322]]],
              }

    with unittest.mock.patch(UUID4PATH, mockid):
        actual, rparam = twsp.parse_sql(q.sql(), params, delete_comment)
    assert_sql_oneline(actual, q.expected(delete_comment), (delete_comment, q.sql()))
    assert_result_param(params, rparam, q.params)


@pytest.mark.parametrize('path, addparams', [
    ('example1_if', {}),
    ('example2_for', {}),
    ('nested_for', {'xxxxx4_0_x': 0, 'xxxxx4_1_x': 1, }),
])
def test_parse_file(path, addparams):
    params = {'table_name': 'TABNAME',
              't_param': True, 'f_param': False,
              'c1': "'ABC'", 'c2': "'IJK'",
              'dct': {'k1': 'v1', 'k2': 'v2'}}
    input_path = absp(f'./data/input/{path}.sql')
    with unittest.mock.patch(UUID4PATH, mockid):
        actual, rparam = twsp.parse_file(input_path, params, False)
    exp = read(absp(f'./data/expected/{path}.sql'))
    assert_sql_oneline(actual, exp, f'{path}.sql')
    assert_result_param(params, rparam, addparams)


def assert_sql_oneline(a: str, e: str, param=None):
    actual = repcrlf(a)
    expected = repcrlf(e)
    if type(param) in (list, tuple):
        fmt_param = tuple([repcrlf(val) for val in param])
    else:
        fmt_param = repcrlf(param)
    assert actual == expected, fmt_param


def assert_result_param(base: dict, result: dict, addparam: dict):
    exp = {**base, **addparam}
    # 全てのキー名を取得して比較
    actual_keys = [k for k in result.keys()]
    expected_keys = [k for k in exp.keys()]
    actual_keys.sort()
    expected_keys.sort()
    assert actual_keys == expected_keys, result

    # キーを順番に格納したdict
    actual, expected = {}, {}
    for k in actual_keys:
        actual[k] = result.get(k)
        expected[k] = exp.get(k)
    assert actual == expected


def repcrlf(val):
    return val.replace('\n', '[n]').replace('\r', '[r]') if type(val) == str else val


def absp(p):
    return os.path.join(DIRNAME, p)


def read(p):
    with open(p, 'r', encoding='utf-8') as f:
        return f.read()


if __name__ == '__main__':
    pytest.main(['--lf'])
