select * from sample_lang
where lang_name in (select unnest(/*:lang_names*/('a','b')))