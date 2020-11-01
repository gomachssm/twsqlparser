# TWSqlParser (TwoWaySqlParser) #

```text
[English]
The readme for this product is written in Japanese.
If you want to read it in other languages, please use a translation tool.

[Japanese]
このプロダクトのreadmeは日本語で記載されています。
もし別の言語で読みたい場合は、翻訳ツールを使って下さい。
```

## インストール方法

以下のコマンドでインストールを行います。
```shell script
pip install twsqlparser
```

## TWSqlParser とは

TWSqlParser(以下、TWSP)はSQLファイルをベースに動的なSQLを作成するためのモジュールです。
他の2WaySQLライブラリ、フレームワーク用に作成されたSQLファイルとの互換性はありません。
また、TWSPはルールに従って展開を行うだけであるため、入力SQLが誤っている場合は
SQL構文として間違った結果を返却する可能性があります。

以下のSQLを例に概要を説明します。

```oracle-sql
select schemaname, tablename
from pg_tables
where tablename = /*:table_name*/'pg_type';
```

この場合、TWSPを利用すると以下のSQLに変換されます。

```oracle-sql
select schemaname, tablename
from pg_tables
where tablename = :table_name;
```

この仕組みにより、開発時にSQLファイルを直接実行することも、
このSQLファイルを製品コードに埋め込むことも可能になります。

バインドパラメータを直接埋め込んだSQLファイルではSQL開発クライアント上で実行するための
パラメータの置換、もしくはパラメータの設定が必要になるため非効率です。

## 組み合わせて利用可能なモジュール

TWSPではバインドパラメータを次の形式で埋め込むことができます。
SQL実行に利用するモジュールが対応しているか確認した上でTWSPを利用してください。

* `:parameter` 形式

※ バインドパラメータの `?` や `:0` 、 `%s` といった書き方には対応していません。

## 関数の利用方法

このモジュールの呼び出し方は2通りあります。

1: `twsqlparser.parse_file`

|引数|型|必須|初期値|説明|
| :---: | :---: | :---: | :---: | --- |
|file_path|str|*| | 解析対象ファイルの絶対パス<br>絶対パスを指定する必要があります。 |
|query_params|dict| |None|`parse_sql` 参照|
|comment_delete|bool| |True|`parse_sql` 参照|
|encoding|str| |'utf-8'|対象ファイルの文字コード|
|newline|str| |'\n'|対象ファイルの改行コード|

戻り値 は `parse_sql` 参照

2: `twsqlparser.parse_sql`

|引数|型|必須|初期値|説明|
| :---: | :---: | :---: | :---: | --- |
|base_sql|str|*| |解析対象SQL|
|query_params|dict| |None|SQL実行時に利用するパラメータ<br>パラメータを利用しない場合は省略可能|
|comment_delete|bool| |True|True の場合、通常コメントを削除、 False の場合は削除しない|
|newline|str| |'\n'|対象ファイルの改行コード|

* 戻り値 : tuple(str, dict)
  * str : 解析後SQL
  * dict: 解析後パラメータ
    * 解析後SQLを利用するために必要なパラメータです。
      * 解析対象SQLに FOR コメントが含まれない場合は入力と同じ値になります。
      * 解析対象SQLに FOR コメントが含まれる場合、 FOR 用のパラメータが追加されます。
    * この処理は引数 query_params には影響を与えません。

## コメント解析仕様

### 行コメント

* 行コメント `--comment` は通常通り、コメントとして解釈されます。

### 複数行コメント

* 複数行コメント `/*...*/` は書き方に応じて複数の振る舞いをします。
  * `/*:param*/` : バインドパラメータとして埋め込みます。
  * `/*$param*/` : SQLに文字として直接埋め込みます。
  * `/*%if PYTHON_BOOL_STATEMENT*/~/*end*/` : if が True の場合、 if から end に囲まれた文字を出力します。
  * `/*%for VARIABLE in PYTHON_ITERATABLE_STATEMENT*/~/*end*/` : ループ可能な変数を含む場合、 for から end に囲まれた文字を繰り返し出力します。
  * 上記以外は通常通り、コメントとして解釈されます。

#### パラメータとして埋め込み

* 記述方法
  * `/*:パラメータ名*/` を記述することで、パラメータを埋め込むことができます。
  * また、コメントの直後に連続して文字が続く場合、その値はダミー値として扱われます。
    * ダミー値として扱う文字は `*/` の直後から以下の文字を見つけるまでです。
        * スペース ` `、タブ `\t`、改行 `\r` `\n` `\r\n`。
        * ``'!#$%&)-=^~|@`;+:*]},./<>?_`` ※ `[{('"\` 以外の記号
        * パラメータコメントの直後が `'` や `"` の場合、クォートに囲まれた文字列をダミー値として識別します。
        * パラメータコメントの直後が `(` や `[` 、 `{` の場合、それに対応する閉じ括弧までを
          ダミー値として識別します。
    * `/*:a*/'foo'` の場合、解析結果には `foo` は含まれず、 `:a` のみが残ります。
    * `/*:a*/123` や `/*:a*/table.column`  の場合も同様です。
    * 利用するライブラリの仕様に依存しますが、 `in` 句やListの比較を行う場合、
      ダミー値は `in /*:params*/(0, 1, 2)` のように書く必要があります。<br>
      `params = ('cond1', 'con2')`
      * ライブラリ依存で対応が難しい場合、「直接埋め込み」の利用を検討してください。
  * パラメータ名に利用可能な文字は、半角英数字とアンダースコアのみ(正規表現パターン `[a-zA-Z0-9_]+` )です。
  * 次のいずれかの場合、正しく解析されず、通常コメントとして扱われる、またはエラーが発生します。
    * `/*` の直後が `:` ではない
    * `/*` と `*/` の間にスペース ` ` など変数として利用できない文字が存在する

* 利用例

```oracle-sql input.sql
select /*:param*/'dummy value' from xxx
```

* 解析後

```oracle-sql output.sql
select :param from xxx
```

#### 直接埋め込み

* 記述方法
  * 例として、次のパラメータを受け取った場合の例を記載します。
    * `{'a': 'str_a', 'params': '(7, 8, 9)'}`
  * `/*$パラメータ名*/` を記述することで、パラメータ名に該当する値を直接埋め込むことができます。
    * 文字として埋め込みたい場合、パラメータは `'any'` のようにクォートで囲む必要があります。
  * また、コメントの直後に連続して文字が続く場合、その値はダミー値として扱われます。
    * ダミー値として扱う文字は `*/` の直後から以下の文字を見つけるまでです。
        * スペース ` `、タブ `\t`、改行 `\r` `\n` `\r\n`。
        * ``'!#$%&)-=^~|@`;+:*]},./<>?_`` ※ `[{('"\` 以外の記号
        * パラメータコメントの直後が `'` や `"` の場合、クォートに囲まれた文字列をダミー値として識別します。
        * パラメータコメントの直後が `(` や `[` 、 `{` の場合、それに対応する閉じ括弧までを
          ダミー値として識別します。
    * `/*$a*/'foo'` の場合、解析結果には `foo` は含まれず、 パラメータ `a` の値が出力されます。
    * `/*$a*/123` や `/*$a*/table.column`  の場合も同様です。
    * 利用するライブラリの仕様に依存しますが、 `in` 句やListの比較を行う場合、
      ダミー値は `in /*$params*/(0, 1, 2)` のように書く必要があります。<br>
      `params = "('cond1', 'con2')"`
  * パラメータ名に利用可能な文字は、半角英数字とアンダースコアのみ(正規表現パターン `[a-zA-Z0-9_]+` )です。
  * 次のいずれかの場合、正しく解析されず、通常コメントとして扱われる、またはエラーが発生します。
    * `/*` の直後が `$` ではない
    * `/*` と `*/` の間にスペース ` ` など変数として利用できない文字が存在する

:warning: : 直接埋め込みはSQLインジェクションが行われる可能性がある為、実装には十分注意してください。
  可能な限り直接埋め込みを避け、パラメータとして埋め込む方法を検討する必要があります。
  特に、利用者が変更可能な値を直接埋め込みすることは避ける必要があります。どうしても必要な場合は十分な入力値検証が必要です。

* 利用例

```oracle-sql input.sql
select /*$p*/'dummy value' from xxx
```

```python input_parameter
{'p': "'Parameter is output directly.'"}
```

* 解析後

```oracle-sql output.sql
select 'Parameter is output directly.' from xxx
```

#### IF分岐

* 記述方法
  * 例として、次のパラメータを受け取った場合の例を記載します。
    * `{'a': 'foo'}`
  * `/*%if PYTHON_BOOL_STATEMENT*/any/*end*/` を記述することで、 PYTHON_BOOL_STATEMENT が True
    になる場合に any が SQL に埋め込まれます。
    * PYTHON_BOOL_STATEMENT は、 Python の `if` 構文で記述可能な書式が利用可能です。
      * 例えば `/*%if a == 'foo'*/` や `/*%if a != 'bar'*/` 、 `/*%if a*/` など。
    * if から end に挟まれた箇所は、通常の SQL や、 TWSP で解析可能なコメントのネストが可能です。
      * 半角スペースや改行を含む場合、それらはトリムされません。
      * 例外的に、 1 行の記載が `/*%if PYTHON_BOOL_STATEMENT*/` または `/*end*/` のみの場合に限り、
        解析後の結果から該当行を削除します。(利用例、解析後を参照)
  * 次のいずれかの場合、正しく解析されず、通常コメントとして扱われる、またはエラーが発生します。
    * `/*` の直後が `%if ` ではない
      * `if` の直後には 1 つ以上の半角スペースが必要
    * PYTHON_BOOL_STATEMENT が真偽値を返す式ではない
    * `/*end*/` が存在しない
    * `/*end*/` コメントの中に半角スペース ` ` など、関係のない文字が含まれる

* 利用例

```oracle-sql input.sql
select
  /*%if a == 'foo'*/
    'dummy value'
  /*end*/
from xxx
```

```python input_parameter
{'a': 'foo'}
```

* 解析後

```oracle-sql input.sql
select
    'dummy value'
from xxx
```

#### FORループ

* 記述方法
  * 例として、次のパラメータを受け取った場合の例を記載します。
    * `{'arr': ['col1', 'col2', 'col3'], 'dct': {'k1': 'v1', 'k2': 'v2'}}`
  * `/*%for VARIABLE in PYTHON_ITERATABLE_STATEMENT*/any/*end*/` を記述することで、PYTHON_ITERATABLE_STATEMENT
    がループ可能な回数分、 any が SQL に埋め込まれます。
    * PYTHON_ITERATABLE_STATEMENT は Python の `for` 構文で記述可能な書式が利用可能です。
      * 例えば `/*%for x in arr*/` や `/*%for i, kv in enumerate(dct.items())*/`
      * VARIABLE は `for` から `end` に囲まれたスコープの間でのみ有効です。
    * if から end に挟まれた箇所は、通常の SQL や、 TWSP で解析可能なコメントのネストが可能です。
      * 半角スペースや改行を含む場合、それらはトリムされません。
      * 例外的に、 1 行の記載が `/*%for VARIABLE in PYTHON_ITERATABLE_STATEMENT*/` または `/*end*/` のみの場合に限り、
        解析後の結果から該当行を削除します。(利用例、解析後を参照)
  * 次のいずれかの場合、正しく解析されず、通常コメントとして扱われる、またはエラーが発生します。
    * `/*` の直後が `%for ` ではない
      * `for` の直後には 1 つ以上の半角スペースが必要
    * PYTHON_ITERATABLE_STATEMENT がループ可能な式ではない
    * PYTHON_ITERATABLE_STATEMENT の結果を VARIABLE に代入できない
    * `/*end*/` が存在しない
    * `/*end*/` コメントの中に半角スペース ` ` など、関係のない文字が含まれる

* 利用例

```oracle-sql input.sql
select * from xxx
where 1 = 1
/*%for i, v in enumerate(values)*/
  and col/*$i*/999 in /*:v*/'foo'
/*end*/
```

```python input_parameter
{'values': ['valueA', 'valueB']}
```

* 解析後

```oracle-sql output.sql
select * from xxx
where 1 = 1
  and col0 in :5a124b33-b25f-44e8-8d4b-144f3ef376dc_0_v
  and col1 in :5a124b33-b25f-44e8-8d4b-144f3ef376dc_1_v
```

```python output_parameter
{
    'values': ['valueA', 'valueB'],
    '5a124b33-b25f-44e8-8d4b-144f3ef376dc_0_v': 'valueA',
    '5a124b33-b25f-44e8-8d4b-144f3ef376dc_1_v': 'valueB'
}
```

## ライセンス

Apache License, Version 2.0

## その他

このライブラリを使った感想があれば、twitterやブログに投稿をお願いします。
その時、 `twsqlparser` の単語を含めていただけると
作者のモチベーション向上や不具合改修、機能追加に繋がります。
twitterに投稿する場合は、ハッシュタグ `#twsqlparser` で投稿して頂きたいです。

機能追加、改善要望、バグ報告はtwitterまたはissueに投稿をお願いします。

バグ、機能追加など、いずれも作者が開発可能なペースで進みます。
素早い対応は期待しないようお願いします。
