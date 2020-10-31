select
    1
  , 'foo' as "f"
  , bar as b
from
    /*$table_name*/xxxxxxxx
where   1 = 1
    and 2 = 2
    /*%if t_param*/
    and col1 = /*:c1*/'col1_value'
    /*end*/
    /*%if f_param*/
    and col2 = /*:c2*/'col2_value'
    /*end*/
    /*%if t_param*/
    and col1 = /*$c1*/'col1_value'
    /*end*/
    /*%if f_param*/
    and col2 = /*$c2*/'col2_value'
    /*end*/
;