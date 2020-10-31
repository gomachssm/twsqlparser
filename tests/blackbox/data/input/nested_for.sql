select * from xxx
where 1 = 1
/*%for i in range(2)*/
  and current_loop_is = /*$i*/999
  /*%for j in range(2) */
    and nested_/*$j*/999 = /*$i*/999
  /*end*/
/*end*/
/*%for x in range(2)*/
  and current_loop_is = /*$x*/999
  /*%for y in range(2) */
    and nested_/*$y*/999 = /*:x*/999
  /*end*/
/*end*/
;