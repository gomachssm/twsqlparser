select
    1
  , 'foo' as "f"
  , bar as b
from
    TABNAME
where   1 = 1
    and 2 = 2
    and col1 = :c1
    and col1 = 'ABC'
;