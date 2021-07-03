insert into sample_lang (lang_name, create_year, insert_date)
values
/*%for i, lang_name, year, dt in langs*/
/*%if i > 0*/, /*end*/( /*:lang_name*/'sample' , /*:year*/1995 , /*:dt*/'2020-04-01 10:20:30.456+900' )
/*end*/
;