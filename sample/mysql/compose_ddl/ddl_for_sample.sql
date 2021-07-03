CREATE TABLE sample_lang (
    id integer NOT NULL AUTO_INCREMENT PRIMARY KEY
  , lang_name text NOT NULL
  , create_year integer
  , insert_date datetime
  , index(id)
);
ALTER TABLE sample_lang ADD UNIQUE(lang_name(30));
