create table sample_lang (
  id serial not null
  , name text not null
  , constraint pk_sample_lang primary key (id)
) ;
alter table sample_lang add constraint uq_sample_lang0 unique (name) ;
