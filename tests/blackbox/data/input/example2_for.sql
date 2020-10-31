-- {'dct': {'k1': 'v1', 'k2': 'v1'}}
select * from xxx
where 1 = 1
/*%for i, kv in enumerate(dct.items())*/
  and col/*$i*/999 in /*$kv*/(0,1)
/*end*/
;