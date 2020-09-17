--
-- PostgreSQL database dump
--

-- Dumped from database version 12.3
-- Dumped by pg_dump version 12.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE ONLY public.user_photos DROP CONSTRAINT user_photos_user_id_fkey;
ALTER TABLE ONLY public.pass DROP CONSTRAINT pass_passer_fkey;
ALTER TABLE ONLY public.pass DROP CONSTRAINT pass_passee_fkey;
ALTER TABLE ONLY public.message DROP CONSTRAINT message_sender_fkey;
ALTER TABLE ONLY public.message DROP CONSTRAINT message_match_id_fkey;
ALTER TABLE ONLY public.match DROP CONSTRAINT match_user_2_fkey;
ALTER TABLE ONLY public.match DROP CONSTRAINT match_user_1_fkey;
ALTER TABLE ONLY public.create_match DROP CONSTRAINT create_match_matcher_fkey;
ALTER TABLE ONLY public.create_match DROP CONSTRAINT create_match_matchee_fkey;
ALTER TABLE ONLY public."user" DROP CONSTRAINT user_pkey;
ALTER TABLE ONLY public.user_photos DROP CONSTRAINT user_photos_pkey;
ALTER TABLE ONLY public.pass DROP CONSTRAINT pass_pkey;
ALTER TABLE ONLY public.message DROP CONSTRAINT message_pkey;
ALTER TABLE ONLY public.match DROP CONSTRAINT match_pkey;
ALTER TABLE ONLY public.create_match DROP CONSTRAINT create_match_pkey;
ALTER TABLE ONLY public.alembic_version DROP CONSTRAINT alembic_version_pkc;
ALTER TABLE public.user_photos ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public."user" ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.pass ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.message ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.match ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.create_match ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE public.user_photos_id_seq;
DROP TABLE public.user_photos;
DROP SEQUENCE public.user_id_seq;
DROP TABLE public."user";
DROP SEQUENCE public.pass_id_seq;
DROP TABLE public.pass;
DROP SEQUENCE public.message_id_seq;
DROP TABLE public.message;
DROP SEQUENCE public.match_id_seq;
DROP TABLE public.match;
DROP SEQUENCE public.create_match_id_seq;
DROP TABLE public.create_match;
DROP TABLE public.alembic_version;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: create_match; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.create_match (
    id integer NOT NULL,
    matcher integer,
    matchee integer,
    matched boolean
);


--
-- Name: create_match_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.create_match_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: create_match_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.create_match_id_seq OWNED BY public.create_match.id;


--
-- Name: match; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.match (
    id integer NOT NULL,
    user_1 integer,
    user_2 integer,
    "timestamp" timestamp without time zone NOT NULL,
    blocked boolean
);


--
-- Name: match_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.match_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: match_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.match_id_seq OWNED BY public.match.id;


--
-- Name: message; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.message (
    id integer NOT NULL,
    sender integer,
    text text,
    "timestamp" timestamp without time zone,
    match_id integer
);


--
-- Name: message_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.message_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.message_id_seq OWNED BY public.message.id;


--
-- Name: pass; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pass (
    id integer NOT NULL,
    passer integer,
    passee integer
);


--
-- Name: pass_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.pass_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: pass_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.pass_id_seq OWNED BY public.pass.id;


--
-- Name: user; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    username character varying(50),
    email character varying(50),
    password character varying(200),
    age integer,
    gender character varying(15),
    "interested in" character varying(15),
    bio text,
    interest text,
    "pet peeves" text,
    zip character varying(15),
    birthdate timestamp without time zone
);


--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: user_photos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_photos (
    id integer NOT NULL,
    user_id integer,
    photo character varying(100)
);


--
-- Name: user_photos_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_photos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_photos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_photos_id_seq OWNED BY public.user_photos.id;


--
-- Name: create_match id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.create_match ALTER COLUMN id SET DEFAULT nextval('public.create_match_id_seq'::regclass);


--
-- Name: match id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.match ALTER COLUMN id SET DEFAULT nextval('public.match_id_seq'::regclass);


--
-- Name: message id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.message ALTER COLUMN id SET DEFAULT nextval('public.message_id_seq'::regclass);


--
-- Name: pass id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pass ALTER COLUMN id SET DEFAULT nextval('public.pass_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Name: user_photos id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_photos ALTER COLUMN id SET DEFAULT nextval('public.user_photos_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
7d585732ed37
\.


--
-- Data for Name: create_match; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.create_match (id, matcher, matchee, matched) FROM stdin;
2	2	1	f
1	2	1	t
3	1	2	t
5	1	6	f
4	6	1	f
7	9	1	t
8	1	9	t
10	7	6	f
9	7	2	t
11	2	7	t
\.


--
-- Data for Name: match; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.match (id, user_1, user_2, "timestamp", blocked) FROM stdin;
1	1	2	2020-08-05 15:52:14.984519	f
3	1	9	2020-09-07 12:56:12.79134	f
4	2	7	2020-09-16 13:24:18.307903	f
\.


--
-- Data for Name: message; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.message (id, sender, text, "timestamp", match_id) FROM stdin;
1	2	hi	2020-08-13 10:45:26.214597	1
2	1	hello	2020-08-13 11:20:42.912226	1
3	2	miss u, ass face	2020-08-13 15:16:32.881338	1
4	1	thanks bro	2020-08-25 14:46:59.478312	1
5	2	Did you know that particles can become quantum entangled across the universe and any change made to the direction of one of them immediately changes the direction of the other??	2020-09-01 14:06:30.172253	1
6	2	Did you know that particles can become quantum entangled across the universe and any change made to the direction of one of them immediately changes the direction of the other??	2020-09-01 14:09:56.210256	1
7	2	Hi Bailey, I like to read about murders and aliens	2020-09-16 13:24:50.431746	4
8	7	Hi, I prefer to read about Soviet-era Russia	2020-09-16 13:25:58.661328	4
\.


--
-- Data for Name: pass; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.pass (id, passer, passee) FROM stdin;
1	6	5
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."user" (id, username, email, password, age, gender, "interested in", bio, interest, "pet peeves", zip, birthdate) FROM stdin;
3	Siggy	siggy@email.com	123	\N	\N	\N	\N	\N	\N	\N	\N
4	Siggy	siggy@test.com	123	2	women	\N	\N	\N	\N	48103	\N
5	Violet	violet@emial.com	123	3	women	\N	\N	\N	\N	30308	\N
8	Cooper	cooper@email.com	123	6	women	\N	\N	\N	\N	\N	\N
9	Flannel	flannel@email.com	123	18	women	\N	\N	\N	\N	30308	2019-04-01 00:00:00
1	Henry	henry@gmail.com	123	3	women	women	I'm a little shit ;)	naps, pets, eating mom's food	loud noises	30308	2017-11-08 00:00:00
7	Bailey	bailey@email.com	123	14	men	\N	\N	\N	\N	30308	2007-02-27 00:00:00
6	Mini	mini@email.com	123	6	women	\N	Hi, I'm Mini. I like to get up early in the morning (but not too early) and demand eye contact from my mom until she takes me on a walk. I am also very particular with my treats and am kind of a monster. I'm so sweet and cute, though, so I can get away with being a terror ;)	\N	\N	30308	\N
2	Millie	test2@gmail.com	123	4	women	women	Evil genius	swimming, cuddles, meeting new people	rules, being alone, when things don't go exactly my way	30308	2017-01-08 00:00:00
\.


--
-- Data for Name: user_photos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_photos (id, user_id, photo) FROM stdin;
1	4	user-images/4/IMG-0169.JPG
2	4	user-images/4/Screen_Shot_2020-08-21_at_6.00.16_PM.png
3	1	user-images/1/IMG_0875.jpeg
4	1	user-images/1/IMG_1453.jpeg
5	1	user-images/1/59034094479__0424DFAB-F087-4EE5-96B2-1D9CB02F29FE.jpg
6	2	user-images/2/IMG_4426.jpeg
7	2	user-images/2/IMG_2246.jpeg
8	2	user-images/2/IMG_2270.jpeg
9	5	user-images/5/tan_and_white_pit_bull_x1.jpg
10	6	user-images/6/IMG_6184.jpeg
11	7	user-images/7/600_SaintBernard1_header.jpg
12	9	user-images/9/german-shepherd-dog-breed-info.jpg
\.


--
-- Name: create_match_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.create_match_id_seq', 11, true);


--
-- Name: match_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.match_id_seq', 4, true);


--
-- Name: message_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.message_id_seq', 8, true);


--
-- Name: pass_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.pass_id_seq', 1, true);


--
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.user_id_seq', 9, true);


--
-- Name: user_photos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.user_photos_id_seq', 12, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: create_match create_match_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.create_match
    ADD CONSTRAINT create_match_pkey PRIMARY KEY (id);


--
-- Name: match match_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.match
    ADD CONSTRAINT match_pkey PRIMARY KEY (id);


--
-- Name: message message_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.message
    ADD CONSTRAINT message_pkey PRIMARY KEY (id);


--
-- Name: pass pass_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pass
    ADD CONSTRAINT pass_pkey PRIMARY KEY (id);


--
-- Name: user_photos user_photos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_photos
    ADD CONSTRAINT user_photos_pkey PRIMARY KEY (id);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: create_match create_match_matchee_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.create_match
    ADD CONSTRAINT create_match_matchee_fkey FOREIGN KEY (matchee) REFERENCES public."user"(id);


--
-- Name: create_match create_match_matcher_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.create_match
    ADD CONSTRAINT create_match_matcher_fkey FOREIGN KEY (matcher) REFERENCES public."user"(id);


--
-- Name: match match_user_1_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.match
    ADD CONSTRAINT match_user_1_fkey FOREIGN KEY (user_1) REFERENCES public."user"(id);


--
-- Name: match match_user_2_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.match
    ADD CONSTRAINT match_user_2_fkey FOREIGN KEY (user_2) REFERENCES public."user"(id);


--
-- Name: message message_match_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.message
    ADD CONSTRAINT message_match_id_fkey FOREIGN KEY (match_id) REFERENCES public.match(id);


--
-- Name: message message_sender_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.message
    ADD CONSTRAINT message_sender_fkey FOREIGN KEY (sender) REFERENCES public."user"(id);


--
-- Name: pass pass_passee_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pass
    ADD CONSTRAINT pass_passee_fkey FOREIGN KEY (passee) REFERENCES public."user"(id);


--
-- Name: pass pass_passer_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pass
    ADD CONSTRAINT pass_passer_fkey FOREIGN KEY (passer) REFERENCES public."user"(id);


--
-- Name: user_photos user_photos_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_photos
    ADD CONSTRAINT user_photos_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- PostgreSQL database dump complete
--

