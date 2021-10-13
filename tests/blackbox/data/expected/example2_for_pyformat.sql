-- {'dct': {'k1': 'v1', 'k2': 'v1'}}
select * from xxx
where 1 = 1
  and col0 in ('k1', 'v1')
  and col1 in ('k2', 'v2')
;