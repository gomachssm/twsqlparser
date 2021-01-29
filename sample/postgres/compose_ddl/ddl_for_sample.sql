CREATE TABLE public.sample_lang (
    id integer NOT NULL
  , name text NOT NULL
  , create_year integer
  , insert_date timestamp(3) without time zone
);
ALTER TABLE public.sample_lang OWNER TO postgres;
CREATE SEQUENCE public.sample_lang_id_seq AS integer START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER TABLE public.sample_lang_id_seq OWNER TO postgres;
ALTER SEQUENCE public.sample_lang_id_seq OWNED BY public.sample_lang.id;
ALTER TABLE ONLY public.sample_lang ALTER COLUMN id SET DEFAULT nextval('public.sample_lang_id_seq'::regclass);
ALTER TABLE ONLY public.sample_lang ADD CONSTRAINT pk_sample_lang PRIMARY KEY (id);
ALTER TABLE ONLY public.sample_lang ADD CONSTRAINT uq_sample_lang0 UNIQUE (name);
