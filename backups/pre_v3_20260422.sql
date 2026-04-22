--
-- PostgreSQL database dump
--

\restrict xzwhCS1opHTUNUE7VPxLjCfVmOkscpy9Lb4mHoeP4iwCpY21Y1AL8NQW5TKXjlD

-- Dumped from database version 16.13
-- Dumped by pg_dump version 16.13

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

--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: update_updated_at(); Type: FUNCTION; Schema: public; Owner: mahardika
--

CREATE FUNCTION public.update_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;

$$;


ALTER FUNCTION public.update_updated_at() OWNER TO mahardika;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: action_items; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.action_items (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    csm_meeting_id uuid NOT NULL,
    chapter_id uuid NOT NULL,
    description text NOT NULL,
    assigned_to_member_id uuid,
    assigned_to_name character varying(150),
    due_date date,
    status character varying(20) DEFAULT 'open'::character varying,
    completed_date date,
    notes text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT action_items_status_check CHECK (((status)::text = ANY ((ARRAY['open'::character varying, 'in_progress'::character varying, 'completed'::character varying, 'overdue'::character varying, 'cancelled'::character varying])::text[])))
);


ALTER TABLE public.action_items OWNER TO mahardika;

--
-- Name: activity_log; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.activity_log (
    id uuid NOT NULL,
    chapter_id uuid,
    actor_id uuid,
    action character varying(50) NOT NULL,
    target_type character varying(50),
    target_id uuid,
    data jsonb,
    created_at timestamp without time zone
);


ALTER TABLE public.activity_log OWNER TO mahardika;

--
-- Name: announcements; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.announcements (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    chapter_id uuid NOT NULL,
    meeting_id uuid,
    title character varying(255) NOT NULL,
    content text,
    priority integer DEFAULT 1,
    type character varying(30) DEFAULT 'general'::character varying,
    start_date date DEFAULT CURRENT_DATE,
    expire_date date,
    is_active boolean DEFAULT true,
    created_by uuid,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT announcements_priority_check CHECK (((priority >= 1) AND (priority <= 5))),
    CONSTRAINT announcements_type_check CHECK (((type)::text = ANY ((ARRAY['general'::character varying, 'event'::character varying, 'renewal_reminder'::character varying, 'orientation'::character varying, 'visitor_day'::character varying, 'training'::character varying, 'achievement'::character varying, 'custom'::character varying])::text[])))
);


ALTER TABLE public.announcements OWNER TO mahardika;

--
-- Name: attendance; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.attendance (
    id uuid NOT NULL,
    meeting_id uuid NOT NULL,
    member_id uuid NOT NULL,
    status character varying(20) NOT NULL,
    meta jsonb,
    recorded_at timestamp without time zone
);


ALTER TABLE public.attendance OWNER TO mahardika;

--
-- Name: chapter_content; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.chapter_content (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    chapter_id uuid NOT NULL,
    content_type character varying(50) NOT NULL,
    title character varying(255),
    content jsonb DEFAULT '{}'::jsonb,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT chapter_content_content_type_check CHECK (((content_type)::text = ANY ((ARRAY['core_values'::character varying, 'closing_quote'::character varying, 'branding'::character varying, 'networking_info'::character varying, 'president_intro'::character varying, 'vision_mission'::character varying, 'custom'::character varying])::text[])))
);


ALTER TABLE public.chapter_content OWNER TO mahardika;

--
-- Name: chapter_targets; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.chapter_targets (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    chapter_id uuid NOT NULL,
    period_label character varying(50) NOT NULL,
    period_start date NOT NULL,
    period_end date NOT NULL,
    metric character varying(50) NOT NULL,
    target_value numeric(15,2) NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT chapter_targets_metric_check CHECK (((metric)::text = ANY ((ARRAY['chapter_size'::character varying, 'attendance_rate'::character varying, 'referrals'::character varying, 'one_to_ones'::character varying, 'visitors'::character varying, 'ceu'::character varying, 'tyfcb'::character varying, 'member_growth'::character varying, 'retention'::character varying, 'conversion'::character varying])::text[])))
);


ALTER TABLE public.chapter_targets OWNER TO mahardika;

--
-- Name: chapters; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.chapters (
    id uuid NOT NULL,
    name character varying(100) NOT NULL,
    city character varying(100) NOT NULL,
    region character varying(100),
    meeting_day character varying(10),
    meeting_time character varying(10),
    venue text,
    status character varying(20),
    settings jsonb,
    created_at timestamp without time zone
);


ALTER TABLE public.chapters OWNER TO mahardika;

--
-- Name: csm_meetings; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.csm_meetings (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    chapter_id uuid NOT NULL,
    date date NOT NULL,
    location character varying(255),
    attendees jsonb DEFAULT '[]'::jsonb,
    agenda jsonb DEFAULT '[]'::jsonb,
    vp_report jsonb DEFAULT '{}'::jsonb,
    visitor_report jsonb DEFAULT '{}'::jsonb,
    mc_report jsonb DEFAULT '{}'::jsonb,
    education_report jsonb DEFAULT '{}'::jsonb,
    mentor_report jsonb DEFAULT '{}'::jsonb,
    event_report jsonb DEFAULT '{}'::jsonb,
    notes text,
    next_meeting_date date,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.csm_meetings OWNER TO mahardika;

--
-- Name: data_imports; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.data_imports (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    chapter_id uuid NOT NULL,
    source_type character varying(50) NOT NULL,
    filename character varying(255),
    file_path character varying(500),
    raw_data jsonb DEFAULT '[]'::jsonb,
    mapped_data jsonb DEFAULT '[]'::jsonb,
    import_status character varying(20) DEFAULT 'pending'::character varying,
    records_total integer DEFAULT 0,
    records_imported integer DEFAULT 0,
    records_skipped integer DEFAULT 0,
    records_error integer DEFAULT 0,
    error_log jsonb DEFAULT '[]'::jsonb,
    imported_by character varying(100),
    created_at timestamp with time zone DEFAULT now(),
    completed_at timestamp with time zone,
    CONSTRAINT data_imports_import_status_check CHECK (((import_status)::text = ANY ((ARRAY['pending'::character varying, 'processing'::character varying, 'completed'::character varying, 'partial'::character varying, 'failed'::character varying])::text[]))),
    CONSTRAINT data_imports_source_type_check CHECK (((source_type)::text = ANY ((ARRAY['roster_report'::character varying, 'palms_summary'::character varying, 'vp_report'::character varying, 'palms_attendance'::character varying, 'sponsor_report'::character varying, 'dues_report'::character varying, 'power_team_form'::character varying, 'attendance_sheet'::character varying, '7month_review'::character varying, 'csm_minutes'::character varying, 'google_sheet_sync'::character varying, 'manual_entry'::character varying, 'bot_webhook'::character varying, 'zoom_log'::character varying, 'other'::character varying])::text[])))
);


ALTER TABLE public.data_imports OWNER TO mahardika;

--
-- Name: edu_contents; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.edu_contents (
    id uuid NOT NULL,
    chapter_id uuid NOT NULL,
    title character varying(200) NOT NULL,
    slug character varying(100) NOT NULL,
    description text,
    slides jsonb,
    is_published boolean,
    created_by uuid,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.edu_contents OWNER TO mahardika;

--
-- Name: form_responses; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.form_responses (
    id uuid NOT NULL,
    form_id uuid NOT NULL,
    respondent_id uuid,
    respondent_name character varying(150),
    respondent_email character varying(150),
    answers jsonb,
    meta jsonb,
    created_at timestamp without time zone
);


ALTER TABLE public.form_responses OWNER TO mahardika;

--
-- Name: form_templates; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.form_templates (
    id uuid NOT NULL,
    chapter_id uuid NOT NULL,
    name character varying(150) NOT NULL,
    slug character varying(100) NOT NULL,
    description text,
    form_type character varying(30) NOT NULL,
    questions jsonb,
    settings jsonb,
    is_active boolean,
    created_by uuid,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.form_templates OWNER TO mahardika;

--
-- Name: meeting_activity; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.meeting_activity (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    meeting_id uuid NOT NULL,
    member_id uuid NOT NULL,
    referrals_given integer DEFAULT 0,
    referrals_received integer DEFAULT 0,
    referrals_outside integer DEFAULT 0,
    tyfcb_amount numeric(15,2) DEFAULT 0,
    one_to_ones integer DEFAULT 0,
    visitors_brought integer DEFAULT 0,
    ceu_credits integer DEFAULT 0,
    testimonials_given integer DEFAULT 0,
    notes text,
    source character varying(30) DEFAULT 'manual'::character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT meeting_activity_source_check CHECK (((source)::text = ANY ((ARRAY['manual'::character varying, 'bot'::character varying, 'upload'::character varying, 'bni_connect'::character varying, 'zoom_parse'::character varying])::text[])))
);


ALTER TABLE public.meeting_activity OWNER TO mahardika;

--
-- Name: meetings; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.meetings (
    id uuid NOT NULL,
    chapter_id uuid NOT NULL,
    meeting_date date NOT NULL,
    meeting_type character varying(20),
    is_locked boolean,
    meta jsonb,
    created_at timestamp without time zone
);


ALTER TABLE public.meetings OWNER TO mahardika;

--
-- Name: member_achievements; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.member_achievements (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    chapter_id uuid NOT NULL,
    member_id uuid NOT NULL,
    achievement_type character varying(30) NOT NULL,
    title character varying(150),
    description text,
    criteria_snapshot jsonb DEFAULT '{}'::jsonb,
    achieved_at date,
    announced_at timestamp with time zone,
    announced_meeting_id uuid,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT member_achievements_achievement_type_check CHECK (((achievement_type)::text = ANY ((ARRAY['silver_member'::character varying, 'gold_member'::character varying, 'platinum_member'::character varying, 'palladium_member'::character varying, 'diamond_member'::character varying, 'green_member'::character varying, 'notable_networker'::character varying, 'top_referral'::character varying, 'top_tyfcb'::character varying, 'top_121'::character varying, 'top_visitor'::character varying, 'custom'::character varying])::text[])))
);


ALTER TABLE public.member_achievements OWNER TO mahardika;

--
-- Name: member_presentations; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.member_presentations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    member_id uuid NOT NULL,
    version integer NOT NULL,
    title character varying(255),
    focus_product character varying(255),
    description text,
    products_services jsonb DEFAULT '[]'::jsonb,
    looking_for jsonb DEFAULT '[]'::jsonb,
    product_images jsonb DEFAULT '[]'::jsonb,
    is_active boolean DEFAULT true,
    rotation_order integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT member_presentations_version_check CHECK (((version >= 1) AND (version <= 4)))
);


ALTER TABLE public.member_presentations OWNER TO mahardika;

--
-- Name: member_reviews; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.member_reviews (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    chapter_id uuid NOT NULL,
    member_id uuid NOT NULL,
    review_cycle integer DEFAULT 1 NOT NULL,
    scheduled_date date,
    actual_date date,
    pic_member_id uuid,
    score_percentage integer,
    keterangan text,
    solusi text,
    status character varying(20) DEFAULT 'scheduled'::character varying,
    decision character varying(20),
    raw_data jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT member_reviews_decision_check CHECK (((decision)::text = ANY ((ARRAY['renew'::character varying, 'conditional'::character varying, 'exit'::character varying, NULL::character varying])::text[]))),
    CONSTRAINT member_reviews_review_cycle_check CHECK ((review_cycle = ANY (ARRAY[1, 2]))),
    CONSTRAINT member_reviews_score_percentage_check CHECK (((score_percentage >= 0) AND (score_percentage <= 100))),
    CONSTRAINT member_reviews_status_check CHECK (((status)::text = ANY ((ARRAY['scheduled'::character varying, 'completed'::character varying, 'overdue'::character varying, 'waived'::character varying, 'cancelled'::character varying])::text[])))
);


ALTER TABLE public.member_reviews OWNER TO mahardika;

--
-- Name: member_roles; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.member_roles (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    member_id uuid NOT NULL,
    chapter_id uuid NOT NULL,
    role character varying(50) NOT NULL,
    committee character varying(50),
    term_start date,
    term_end date,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT member_roles_role_check CHECK (((role)::text = ANY ((ARRAY['president'::character varying, 'vice_president'::character varying, 'secretary'::character varying, 'treasurer'::character varying, 'secretary_treasurer'::character varying, 'gdc'::character varying, 'ambassador'::character varying, 'visitor_host'::character varying, 'education_coordinator'::character varying, 'events_coordinator'::character varying, 'mc_coordinator'::character varying, 'mentor_coordinator'::character varying, 'growth_coordinator'::character varying, 'mc_qa'::character varying, 'mc_cb'::character varying, 'mc_me'::character varying, 'mc_mr'::character varying, 'social_media_coordinator'::character varying, 'connect_coordinator'::character varying, 'one_to_one_coordinator'::character varying, 'go_green_coordinator'::character varying, 'feature_presentation_coordinator'::character varying, 'member'::character varying])::text[])))
);


ALTER TABLE public.member_roles OWNER TO mahardika;

--
-- Name: members; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.members (
    id uuid NOT NULL,
    chapter_id uuid NOT NULL,
    full_name character varying(150) NOT NULL,
    email character varying(150),
    phone character varying(20),
    bni_classification character varying(150),
    company_name character varying(200),
    membership_status character varying(20),
    role character varying(20),
    join_date date,
    renewal_date date,
    password_hash character varying(255),
    is_activated boolean,
    business_profile jsonb,
    profile_completed boolean,
    meta jsonb,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.members OWNER TO mahardika;

--
-- Name: palms_snapshots; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.palms_snapshots (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    chapter_id uuid NOT NULL,
    member_id uuid NOT NULL,
    period_label character varying(50) NOT NULL,
    period_start date NOT NULL,
    period_end date NOT NULL,
    present_count integer DEFAULT 0,
    absent_count integer DEFAULT 0,
    medical_count integer DEFAULT 0,
    late_count integer DEFAULT 0,
    substitute_count integer DEFAULT 0,
    referrals_given integer DEFAULT 0,
    referrals_received integer DEFAULT 0,
    referrals_outside integer DEFAULT 0,
    visitors_brought integer DEFAULT 0,
    one_to_ones integer DEFAULT 0,
    tyfcb_amount numeric(15,2) DEFAULT 0,
    ceu_credits integer DEFAULT 0,
    raw_data jsonb DEFAULT '{}'::jsonb,
    import_id uuid,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.palms_snapshots OWNER TO mahardika;

--
-- Name: power_teams; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.power_teams (
    id uuid NOT NULL,
    chapter_id uuid NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    target_customer jsonb,
    member_ids jsonb,
    is_active boolean,
    meta jsonb,
    created_at timestamp without time zone
);


ALTER TABLE public.power_teams OWNER TO mahardika;

--
-- Name: referral_needs; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.referral_needs (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    member_id uuid NOT NULL,
    target_description character varying(255) NOT NULL,
    priority integer DEFAULT 1,
    status character varying(20) DEFAULT 'active'::character varying,
    version integer DEFAULT 1,
    fulfilled_date date,
    notes text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT referral_needs_priority_check CHECK (((priority >= 1) AND (priority <= 5))),
    CONSTRAINT referral_needs_status_check CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'fulfilled'::character varying, 'paused'::character varying, 'archived'::character varying])::text[])))
);


ALTER TABLE public.referral_needs OWNER TO mahardika;

--
-- Name: referrals; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.referrals (
    id uuid NOT NULL,
    chapter_id uuid NOT NULL,
    giver_id uuid NOT NULL,
    receiver_id uuid NOT NULL,
    status character varying(20),
    data jsonb,
    created_at timestamp without time zone
);


ALTER TABLE public.referrals OWNER TO mahardika;

--
-- Name: scores; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.scores (
    id uuid NOT NULL,
    scope_type character varying(20) NOT NULL,
    scope_id uuid NOT NULL,
    score_type character varying(50) NOT NULL,
    value numeric(10,2),
    details jsonb,
    computed_at timestamp without time zone
);


ALTER TABLE public.scores OWNER TO mahardika;

--
-- Name: sponsorships; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.sponsorships (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    chapter_id uuid NOT NULL,
    sponsor_id uuid NOT NULL,
    sponsored_member_id uuid,
    sponsored_name character varying(150),
    sponsor_date date,
    status character varying(20) DEFAULT 'active'::character varying,
    raw_data jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT sponsorships_status_check CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'resigned'::character varying, 'terminated'::character varying])::text[])))
);


ALTER TABLE public.sponsorships OWNER TO mahardika;

--
-- Name: uploaded_files; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.uploaded_files (
    id uuid NOT NULL,
    filename character varying(255) NOT NULL,
    file_type character varying(50),
    uploaded_by uuid,
    status character varying(20),
    row_count integer,
    parsed_data jsonb,
    import_log jsonb,
    created_at timestamp without time zone
);


ALTER TABLE public.uploaded_files OWNER TO mahardika;

--
-- Name: visitors; Type: TABLE; Schema: public; Owner: mahardika
--

CREATE TABLE public.visitors (
    id uuid NOT NULL,
    chapter_id uuid NOT NULL,
    full_name character varying(150) NOT NULL,
    invited_by_id uuid,
    status character varying(20),
    visit_data jsonb,
    meta jsonb,
    created_at timestamp without time zone
);


ALTER TABLE public.visitors OWNER TO mahardika;

--
-- Data for Name: action_items; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.action_items (id, csm_meeting_id, chapter_id, description, assigned_to_member_id, assigned_to_name, due_date, status, completed_date, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: activity_log; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.activity_log (id, chapter_id, actor_id, action, target_type, target_id, data, created_at) FROM stdin;
37fad221-4527-4011-8f21-b119ac1b5120	fb54dfa8-8cff-4784-9448-bddf257c4d0f	16d9aae1-db0f-4049-b8bf-f4a392db838b	upload_roster_sync	member	\N	{"summary": {"added": 4, "errors": 0, "updated": 1}, "filename": "test_roster.xlsx"}	2026-04-17 04:12:59.840378
6816f194-c9a2-467b-8ead-db34c048fbf9	fb54dfa8-8cff-4784-9448-bddf257c4d0f	16d9aae1-db0f-4049-b8bf-f4a392db838b	upload_roster_sync	member	\N	{"summary": {"added": 1, "errors": 0, "updated": 0}, "filename": "test.xlsx"}	2026-04-17 04:16:44.271884
db4c2234-2ccf-49b0-ab8d-7ed1f00b0d28	fb54dfa8-8cff-4784-9448-bddf257c4d0f	16d9aae1-db0f-4049-b8bf-f4a392db838b	upload_roster_sync	member	\N	{"summary": {"added": 1, "errors": 0, "updated": 0}, "filename": "test_browser.xlsx"}	2026-04-17 04:17:27.349149
2ab7deb9-9b09-437e-8825-a61d93d65621	fb54dfa8-8cff-4784-9448-bddf257c4d0f	16d9aae1-db0f-4049-b8bf-f4a392db838b	upload_roster_sync	member	\N	{"summary": {"added": 0, "errors": 0, "updated": 0}, "filename": "test.xlsx"}	2026-04-17 04:40:51.668888
d2655c89-ec7a-4fcc-8660-5d10c574f923	fb54dfa8-8cff-4784-9448-bddf257c4d0f	16d9aae1-db0f-4049-b8bf-f4a392db838b	upload_roster_sync	member	\N	{"summary": {"added": 0, "errors": 0, "updated": 0}, "filename": "test.xlsx"}	2026-04-17 04:41:56.240711
53a1be9a-0dec-45c1-8345-480f953fce69	fb54dfa8-8cff-4784-9448-bddf257c4d0f	16d9aae1-db0f-4049-b8bf-f4a392db838b	upload_roster_sync	member	\N	{"summary": {"added": 0, "errors": 0, "updated": 0}, "filename": "test.xlsx"}	2026-04-17 04:50:50.282304
ab8429e8-80a9-4eb4-af2e-4f2947921356	fb54dfa8-8cff-4784-9448-bddf257c4d0f	16d9aae1-db0f-4049-b8bf-f4a392db838b	upload_roster_sync	member	\N	{"summary": {"added": 0, "errors": 0, "updated": 0}, "filename": "test.xlsx"}	2026-04-17 05:01:16.722862
20a6a3d3-c19d-4ad2-bc3b-51ab58289a8a	fb54dfa8-8cff-4784-9448-bddf257c4d0f	16d9aae1-db0f-4049-b8bf-f4a392db838b	upload_palms_import	activity	\N	{"summary": {"status": "UPLOADED", "message": "File PALMS diterima dan tersimpan untuk analisis."}, "filename": "Chapter_Summary_PALMS_Report_14-04-2026-21-30.xls"}	2026-04-17 05:17:11.152505
69380d81-cfd4-46be-bac6-d3370eec9e78	fb54dfa8-8cff-4784-9448-bddf257c4d0f	16d9aae1-db0f-4049-b8bf-f4a392db838b	upload_visitor_report	visitor	\N	{"summary": {"status": "UPLOADED", "message": "File Visitor diterima dan tersimpan untuk analisis."}, "filename": "Chapter_Visitor_Report_14-04-2026-21-30.xls"}	2026-04-17 05:17:23.700559
e4c436b8-e190-41b7-b244-461e5fc63245	fb54dfa8-8cff-4784-9448-bddf257c4d0f	16d9aae1-db0f-4049-b8bf-f4a392db838b	upload_visitor_report	visitor	\N	{"summary": {"status": "UPLOADED", "message": "File Visitor diterima dan tersimpan untuk analisis."}, "filename": "Chapter_Visitor_Registration_Report_14-04-2026-21-30.xls"}	2026-04-17 05:17:32.50056
1418042b-63ee-4cdf-80e9-e54d183922c9	fb54dfa8-8cff-4784-9448-bddf257c4d0f	16d9aae1-db0f-4049-b8bf-f4a392db838b	upload_palms_import	activity	\N	{"summary": {"status": "UPLOADED", "message": "File PALMS diterima dan tersimpan untuk analisis."}, "filename": "Chapter_Summary_PALMS_Report_14-04-2026-21-30.xls"}	2026-04-17 05:20:49.343228
\.


--
-- Data for Name: announcements; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.announcements (id, chapter_id, meeting_id, title, content, priority, type, start_date, expire_date, is_active, created_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: attendance; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.attendance (id, meeting_id, member_id, status, meta, recorded_at) FROM stdin;
\.


--
-- Data for Name: chapter_content; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.chapter_content (id, chapter_id, content_type, title, content, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: chapter_targets; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.chapter_targets (id, chapter_id, period_label, period_start, period_end, metric, target_value, created_at) FROM stdin;
\.


--
-- Data for Name: chapters; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.chapters (id, name, city, region, meeting_day, meeting_time, venue, status, settings, created_at) FROM stdin;
fb54dfa8-8cff-4784-9448-bddf257c4d0f	Mahardika	Bandung	Jawa Barat	Wednesday	07:00	\N	active	{}	2026-04-17 04:02:08.982948
\.


--
-- Data for Name: csm_meetings; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.csm_meetings (id, chapter_id, date, location, attendees, agenda, vp_report, visitor_report, mc_report, education_report, mentor_report, event_report, notes, next_meeting_date, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: data_imports; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.data_imports (id, chapter_id, source_type, filename, file_path, raw_data, mapped_data, import_status, records_total, records_imported, records_skipped, records_error, error_log, imported_by, created_at, completed_at) FROM stdin;
\.


--
-- Data for Name: edu_contents; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.edu_contents (id, chapter_id, title, slug, description, slides, is_published, created_by, created_at, updated_at) FROM stdin;
33e2cd82-b17c-458b-8f36-3d1296c5112a	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Kenali Tetangga Bisnis Lo	kenali-tetangga-bisnis	Edu moment tentang pentingnya mengenal detail bisnis sesama member	[{"type": "title", "heading": "Kenali Tetangga Bisnis Lo", "subtext": "Edu Moment — Chapter Mahardika"}, {"body": "Klasifikasi BNI sama: Building Materials. Tapi customer beda. Referral beda. Power Team harusnya beda.", "type": "text", "heading": "Bobby jual besi. Erick jual Alat Teknik."}, {"type": "stat", "number": "20", "caption": "dari 51 member yang kita tahu detail bisnisnya"}, {"body": "Refer ke 'building material' padahal yang dibutuhin alat teknik, bukan besi.", "type": "text", "heading": "Kalau gak kenal bisnis temen, referral nyasar."}, {"body": "1. Produk/jasa paling laku dan paling mahal?\\n2. Customer ideal siapa — spesifik?\\n3. Siapa di chapter yang pasti diajak kalau dapat project?", "type": "text", "heading": "3 pertanyaan. 2 menit."}, {"body": "Siapa serve market yang sama → Power Team\\nSiapa yang belum ada tapi dibutuhkan → Top 10 Wanted\\nSiapa customer terbesar chapter → Top Customers", "type": "text", "heading": "Dari jawaban ini, sistem otomatis tahu:"}, {"type": "cta", "heading": "Scan. Isi. Selesai.", "button_url": "/form/business-profile", "button_text": "Isi Sekarang"}]	t	\N	2026-04-17 04:02:08.993963	2026-04-17 04:02:08.993968
\.


--
-- Data for Name: form_responses; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.form_responses (id, form_id, respondent_id, respondent_name, respondent_email, answers, meta, created_at) FROM stdin;
\.


--
-- Data for Name: form_templates; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.form_templates (id, chapter_id, name, slug, description, form_type, questions, settings, is_active, created_by, created_at, updated_at) FROM stdin;
81dfa65e-b24d-4f78-8a95-2075c9fdb3e1	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Business Profile	business-profile	Kenali bisnis member — 3 pertanyaan, 2 menit	business_profile	[{"key": "q1_products", "hint": "Spesifik. Bukan 'building materials' tapi 'distributor besi beton untuk proyek konstruksi'", "type": "textarea", "label": "Produk/jasa yang paling laku dan paling mahal?", "required": true}, {"key": "q2_customers", "hint": "Bukan 'semua orang' tapi 'owner restoran yang mau buka cabang ke-2'", "type": "textarea", "label": "Customer ideal siapa? (Spesifik)", "required": true}, {"key": "q3_partners", "hint": "Tulis nama member + alasannya", "type": "textarea", "label": "Kalau dapat project, siapa di chapter yang pasti diajak?", "required": true}]	{}	t	\N	2026-04-17 04:02:08.998444	2026-04-17 04:02:08.998449
\.


--
-- Data for Name: meeting_activity; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.meeting_activity (id, meeting_id, member_id, referrals_given, referrals_received, referrals_outside, tyfcb_amount, one_to_ones, visitors_brought, ceu_credits, testimonials_given, notes, source, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: meetings; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.meetings (id, chapter_id, meeting_date, meeting_type, is_locked, meta, created_at) FROM stdin;
\.


--
-- Data for Name: member_achievements; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.member_achievements (id, chapter_id, member_id, achievement_type, title, description, criteria_snapshot, achieved_at, announced_at, announced_meeting_id, created_at) FROM stdin;
\.


--
-- Data for Name: member_presentations; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.member_presentations (id, member_id, version, title, focus_product, description, products_services, looking_for, product_images, is_active, rotation_order, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: member_reviews; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.member_reviews (id, chapter_id, member_id, review_cycle, scheduled_date, actual_date, pic_member_id, score_percentage, keterangan, solusi, status, decision, raw_data, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: member_roles; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.member_roles (id, member_id, chapter_id, role, committee, term_start, term_end, is_active, created_at) FROM stdin;
\.


--
-- Data for Name: members; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.members (id, chapter_id, full_name, email, phone, bni_classification, company_name, membership_status, role, join_date, renewal_date, password_hash, is_activated, business_profile, profile_completed, meta, created_at, updated_at) FROM stdin;
16d9aae1-db0f-4049-b8bf-f4a392db838b	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Lucky Surya	lucky@mierakigai.com	\N	\N	\N	active	admin	2026-04-17	\N	$2b$12$yrEJuK7.yPatwGbVjMnzieQcKS9AKYOz1jt4Oh48viJOaFLjMuWNO	f	{}	f	{}	2026-04-17 04:11:15.147104	2026-04-17 04:11:15.147108
908b52ed-7c89-4e00-bebb-e6f0d526eede	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Awan Santosa	awan@example.com	+6285105226999	Employment Activities > Human Resources > Human Resources	PT. Kinerja Prima Inovasi Indonesia	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 04:12:59.822109	2026-04-17 05:11:27.633373
68cdcc5b-2b93-43a8-8885-f0d676ddff42	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Marcella Alke	\N	08998080606	Retail > Home Furnishings > Home Furnishings	MariGold	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640519	2026-04-17 05:11:27.640524
7e7a3179-d6ab-4b69-9a9c-050dacbf02b1	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Faradina Angelica	\N	081220844119	Advertising & Marketing > Marketing Consultant > Marketing Consultant	CV Fine Creative Agency	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.64053	2026-04-17 05:11:27.64053
9b4396c0-7148-475c-9887-27a3a366212a	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Elbert Asaria Kosasih	\N	08170769487	Advertising & Marketing > Printer > Printer	Borobudur Digital Printing	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640534	2026-04-17 05:11:27.640535
53a771e3-1147-4fcc-a063-56c0e38bc2d4	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Iwan Bambang	\N	087884603889	Construction > Construction Project Management > Construction Project Management	PT Dunia Konstruksi Mandiri	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640538	2026-04-17 05:11:27.640539
d748b7a6-35e4-49f4-b2ab-8b219b0b3c82	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Marcel Budyanto	\N	082167795000	Manufacturing > Apparel > Apparel	PT. Gemilang Putera 500	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640542	2026-04-17 05:11:27.640543
35adeb93-e806-4e37-9d2b-063463535e7e	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Jovian Hartanto Chandra	\N	+628122046560	Manufacturing > Manufacturing (Other) > -	Pt Takara Jaya Nirwasita	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640546	2026-04-17 05:11:27.640547
19202c0b-6134-4f41-abba-9228cf4fdb30	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Kevin Christian	\N	089666593351	Advertising & Marketing > Media Services > Media Services	AIM Production House	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.64055	2026-04-17 05:11:27.64055
fa931f78-3111-44d6-9f42-8f97b4ea29e9	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Michelle Febriani Chusmayadi	\N	081295772568	Food-Beverage Products	PT. Segar Manis Jaya	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640555	2026-04-17 05:11:27.640555
9ddc1a2f-c814-4767-8a8b-4933538b35ca	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Christianus Michael Ciputra	\N	+6287777765111	Manufacturing > Apparel > Apparel	JunMissoni Konveksi	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640559	2026-04-17 05:11:27.640559
66fd0683-0303-47bd-a34d-fe494d203bec	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Stella Clarissa	\N	+628122312123	Manufacturing > Packaging > Packaging	CV Sinar Surya Utama	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640562	2026-04-17 05:11:27.640563
b7e5777a-ed6d-47ef-824a-18bf0754b3cb	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Shaun Clement	\N	082121999288	Food & Beverage > Food Service > Food Service	Bakso Sapi Cihampelas	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640566	2026-04-17 05:11:27.640566
f0a33cc5-b5e8-4c44-8a6a-ce0ab90aea6d	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Josefa Dhea Ariella	\N	081214958988	Manufacturing > Textiles > Textiles	Josefa Bakery	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.64057	2026-04-17 05:11:27.64057
fa912ac5-c35b-4e61-b306-09ae72e91a6f	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Eunike Eriko	\N	+6281809193536	Legal & Accounting > Notary > Notary	Notaris / PPAT	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640573	2026-04-17 05:11:27.640574
c5cf0a73-542c-4cc7-9664-915366811e55	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Ray Grimaldi Erwin	\N	+62 815-7270-0999	Construction > Builder/General Contractor > Builder/General Contractor	Excellera Build	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640577	2026-04-17 05:11:27.640577
790a782e-cb46-424c-819b-11e79f71b8c4	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Anton Ganda Cahyadi	\N	08179993727	Advertising & Marketing > Digital Marketing > Digital Marketing	Social Bread	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.64058	2026-04-17 05:11:27.640581
c78c475a-6995-48da-9ef8-986fa654ca49	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Glenn Grimaldi Erwin	\N	08112333555	Finance & Insurance > Health Insurance > Health Insurance	Prudential Life Assurance (Legacy Inc.)	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640584	2026-04-17 05:11:27.640584
97b5cbc0-32ee-4173-827f-6eafb2153d5a	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Zabdi Hagai	\N	+6285860131988	Computer & Programming > IT & Networks > IT & Networks	Entrust Digital	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640588	2026-04-17 05:11:27.640588
3bc2e52b-3e08-440c-b364-020ed604fbaa	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Harisendi Harisendi	\N	08122333066	Food & Beverage > Cater > Cater	Ayin Catering	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640591	2026-04-17 05:11:27.640591
3452351d-9714-4929-8891-3e581589beed	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Bobby Hartanto	\N	+62-815-6000-188	Retail > Building Materials > Building Materials	PT. Cahaya Multi Jaya Abadi	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640595	2026-04-17 05:11:27.640595
0a98dcff-7d1e-4847-b16e-fb3b39afaed5	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Lucky Surya Haryadi	\N	082218255795	Car & Motorcycle > Auto/Car Sales > Auto/Car Sales	PT Otomobil Multi Artha	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640598	2026-04-17 05:11:27.640599
b4f80c42-2709-4eaa-94b6-3be9a589f1e1	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Ma'ruf Hasanudin	\N	082123423481	Apparel	Lily and Clark	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640602	2026-04-17 05:11:27.640602
b892db14-398e-4c86-bde3-ef21774d3314	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Denny Hendradi Hussen	\N	08122037249	Car & Motorcycle > Auto/Car Repair > Auto/Car Repair	CV. Bintang Lestari	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640605	2026-04-17 05:11:27.640606
80a769c6-5f0f-4016-bc90-69e1c32f0762	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Willy Hono	\N	0818606161	Food & Beverage > Beverage Service > Beverage Service	Toserda	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640609	2026-04-17 05:11:27.640609
543746b7-01e2-4897-bef1-122baaf11090	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Wawan Irawan	\N	081320778333	Manufacturing > Packaging > Packaging	Kiwi Pratama Sentosa	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640612	2026-04-17 05:11:27.640613
1763e629-0e80-4b6f-a6e7-67697319196e	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Jonathan Japputra	\N	+6287817000038	Construction > Glass > Glass	CV Sumber Jaya Maxima	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640616	2026-04-17 05:11:27.640616
673f19f5-76fd-48e7-b535-b68b88fb8839	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Yohanes Martin	\N	085733575859	Food-Beverage Products	Nata Jelly	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.64062	2026-04-17 05:11:27.64062
fdb93820-1adb-4ec7-994d-0fcf6efe695a	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Martina Misella	\N	+6287822888814	Real estate services > Property Management > Property Management	Discovery Property	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640623	2026-04-17 05:11:27.640624
204d8cc5-8c5e-4b10-8f92-f03b7c7a371d	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Ricky Mountero	\N	081802020808	Retail > Electrical Equipment > Electrical Equipment	PT Kilat Teguh Lestari, Mechanical Electrical	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640627	2026-04-17 05:11:27.640627
f015a2b3-091c-4f53-bedc-2b14d002f18c	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Kiki Mulyono	\N	+6281220071891	Architecture & Engineering > Architect > Architect	Legacy Design House	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640631	2026-04-17 05:11:27.640631
12cac5cb-b207-4118-8e1b-378c351de409	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Shiane Natasha	\N	082219981811	Personal Services > Dry Cleaning/Laundry > Dry Cleaning/Laundry	Wash n Co	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640642	2026-04-17 05:11:27.640642
5bfd95bc-3f90-4837-9f92-542b8a8f20e7	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Philippe Nathanael	\N	+62 859-7492-8556	Manufacturing > Computer, Electronics & Optical > Computer, Electronics & Optical	LED Master	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640646	2026-04-17 05:11:27.640646
b1c821a5-29e1-413a-9ae5-a259aa9788b5	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Gracia Permatasari	\N	+6282217259977	Manufacturing > Food Products > Food Products	Palasari	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640649	2026-04-17 05:11:27.640649
a6b1ea80-6946-4567-b56e-7739470c1f87	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Awalia Rahmi	\N	082198888569	Sports & Leisure > Sports & Leisure (Other) > Sports Facilities	Mhorfitness	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640653	2026-04-17 05:11:27.640653
beaa2f92-88fb-45db-a47e-9d3b04ca4881	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Johanes wijaya Salim	\N	+6287729691349	Computer Sales	PT. Pusat gadget indonesia	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640657	2026-04-17 05:11:27.640657
5172b298-8069-4230-a269-8b81b6f874a3	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Henny Setiadi	\N	+628122011100	Manufacturing > Manufacturing (Other) > -	PT. Venamon	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.64066	2026-04-17 05:11:27.64066
84265880-c589-428d-a87f-dbb059999f5a	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Theophillus Setianto	\N	+62226015719	Retail > Building Materials > Building Materials	CV Sejati Jatayu Mandiri	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640664	2026-04-17 05:11:27.640664
d7e8471b-1062-4c58-b220-147c2279ced2	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Temmy Setiawan	\N	0895341582939	Advertising & Marketing > Marketing Consultant > Marketing Consultant	Dr. Printing Sublime	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640667	2026-04-17 05:11:27.640668
3b00c680-7662-46e0-8ab7-6be3cb5dc95a	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Agus Setiawan	\N	+62 81573000590	Retail > Building Materials > Building Materials	Toko Baut Sinar Terang	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640671	2026-04-17 05:11:27.640671
0393c52a-aa77-48fb-93d9-db00aeae3ea0	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Ricardo Jeffry Setiawan Wijaya	\N	+62 812-2011-528	Advertising & Marketing > Sign Company > Sign Company	SIGNIDEA INDONESIA	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640674	2026-04-17 05:11:27.640675
6b2ced27-2a37-4b45-a337-13a82a09d1dd	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Evan Sudharmanto	\N	08992444525	Construction > Builder/General Contractor > Builder/General Contractor	ATRIA CV Anugrah Tritunggal Abadi	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640678	2026-04-17 05:11:27.640678
f73f753e-0d0e-4e66-97a9-70f0f9076c2a	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Richard Tandri Setiawan	\N	08172314037	Architecture & Engineering > Architect > Architect	Richard TS Architect	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640681	2026-04-17 05:11:27.640682
942c78f8-6d64-4135-b6c0-8ebfdb24c748	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Satrio Budiarjo Wibowo	\N	+628116887777	Computer & Programming > Data Security > Data Consultant	Mandalab	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640685	2026-04-17 05:11:27.640685
b64d0bff-9cc4-4ee3-a721-8bf2c26f05e2	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Indah Widyaningsih	\N	+62 82112600280	Manufacturing > Manufacturing (Other) > Scales	PT. Indoscale Sukses Mandiri	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640689	2026-04-17 05:11:27.640689
50eb3e8c-4fc5-48e4-b89b-2f3161f8bbc5	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Rosy Wihardja	\N	+628170288789	Health & Wellness > Medical Services > Medical Services	Oratio Group	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640692	2026-04-17 05:11:27.640692
b0024141-030a-4640-8cb5-6b69ed7b82a7	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Albhert Wijaya	\N	+62225400622	Manufacturing > Chemical Products > Chemical Products	CV. Yasindo Muti Pratama	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640696	2026-04-17 05:11:27.640696
69808f08-71c5-464a-9995-fa298d1ae256	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Benny Wijaya	\N	0226062683	Retail > Office Supplies > Office Supplies	CV Lushan Jaya Abadi	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640699	2026-04-17 05:11:27.6407
e47ae7da-c674-4541-8451-b5d342582092	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Williyanto Williyanto	\N	08122377000	Consulting > Business Consultant > Business Consultant	konsultan proses air	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640703	2026-04-17 05:11:27.640703
7fbc7a81-b1b4-48d2-8787-fc2e9e84942e	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Wilsary Wilsary	\N	+62 812-8775-0847	Legal & Accounting > Accounting Services > Accounting Services	Kantor Jasa Akuntan Wilsary	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640706	2026-04-17 05:11:27.640707
93a19b0f-2850-41b0-90e0-696139c0bef3	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Andy Winata	\N	0816604845	Architecture & Engineering > Interior Architecture > Interior Architecture	Likha Interior	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.64071	2026-04-17 05:11:27.64071
5bcb741f-b4f3-4a7b-9e66-ff8e329a09bf	fb54dfa8-8cff-4784-9448-bddf257c4d0f	Erick Winata	\N	081322300025	Retail > Building Materials > Building Materials	CV Kairos Kerta Karya	active	member	\N	\N	\N	f	{}	f	{}	2026-04-17 05:11:27.640713	2026-04-17 05:11:27.640714
\.


--
-- Data for Name: palms_snapshots; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.palms_snapshots (id, chapter_id, member_id, period_label, period_start, period_end, present_count, absent_count, medical_count, late_count, substitute_count, referrals_given, referrals_received, referrals_outside, visitors_brought, one_to_ones, tyfcb_amount, ceu_credits, raw_data, import_id, created_at) FROM stdin;
\.


--
-- Data for Name: power_teams; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.power_teams (id, chapter_id, name, description, target_customer, member_ids, is_active, meta, created_at) FROM stdin;
\.


--
-- Data for Name: referral_needs; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.referral_needs (id, member_id, target_description, priority, status, version, fulfilled_date, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: referrals; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.referrals (id, chapter_id, giver_id, receiver_id, status, data, created_at) FROM stdin;
\.


--
-- Data for Name: scores; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.scores (id, scope_type, scope_id, score_type, value, details, computed_at) FROM stdin;
\.


--
-- Data for Name: sponsorships; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.sponsorships (id, chapter_id, sponsor_id, sponsored_member_id, sponsored_name, sponsor_date, status, raw_data, created_at) FROM stdin;
\.


--
-- Data for Name: uploaded_files; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.uploaded_files (id, filename, file_type, uploaded_by, status, row_count, parsed_data, import_log, created_at) FROM stdin;
\.


--
-- Data for Name: visitors; Type: TABLE DATA; Schema: public; Owner: mahardika
--

COPY public.visitors (id, chapter_id, full_name, invited_by_id, status, visit_data, meta, created_at) FROM stdin;
\.


--
-- Name: action_items action_items_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.action_items
    ADD CONSTRAINT action_items_pkey PRIMARY KEY (id);


--
-- Name: activity_log activity_log_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.activity_log
    ADD CONSTRAINT activity_log_pkey PRIMARY KEY (id);


--
-- Name: announcements announcements_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.announcements
    ADD CONSTRAINT announcements_pkey PRIMARY KEY (id);


--
-- Name: attendance attendance_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_pkey PRIMARY KEY (id);


--
-- Name: chapter_content chapter_content_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.chapter_content
    ADD CONSTRAINT chapter_content_pkey PRIMARY KEY (id);


--
-- Name: chapter_targets chapter_targets_chapter_id_period_start_period_end_metric_key; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.chapter_targets
    ADD CONSTRAINT chapter_targets_chapter_id_period_start_period_end_metric_key UNIQUE (chapter_id, period_start, period_end, metric);


--
-- Name: chapter_targets chapter_targets_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.chapter_targets
    ADD CONSTRAINT chapter_targets_pkey PRIMARY KEY (id);


--
-- Name: chapters chapters_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.chapters
    ADD CONSTRAINT chapters_pkey PRIMARY KEY (id);


--
-- Name: csm_meetings csm_meetings_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.csm_meetings
    ADD CONSTRAINT csm_meetings_pkey PRIMARY KEY (id);


--
-- Name: data_imports data_imports_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.data_imports
    ADD CONSTRAINT data_imports_pkey PRIMARY KEY (id);


--
-- Name: edu_contents edu_contents_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.edu_contents
    ADD CONSTRAINT edu_contents_pkey PRIMARY KEY (id);


--
-- Name: edu_contents edu_contents_slug_key; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.edu_contents
    ADD CONSTRAINT edu_contents_slug_key UNIQUE (slug);


--
-- Name: form_responses form_responses_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.form_responses
    ADD CONSTRAINT form_responses_pkey PRIMARY KEY (id);


--
-- Name: form_templates form_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.form_templates
    ADD CONSTRAINT form_templates_pkey PRIMARY KEY (id);


--
-- Name: form_templates form_templates_slug_key; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.form_templates
    ADD CONSTRAINT form_templates_slug_key UNIQUE (slug);


--
-- Name: meeting_activity meeting_activity_meeting_id_member_id_key; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.meeting_activity
    ADD CONSTRAINT meeting_activity_meeting_id_member_id_key UNIQUE (meeting_id, member_id);


--
-- Name: meeting_activity meeting_activity_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.meeting_activity
    ADD CONSTRAINT meeting_activity_pkey PRIMARY KEY (id);


--
-- Name: meetings meetings_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.meetings
    ADD CONSTRAINT meetings_pkey PRIMARY KEY (id);


--
-- Name: member_achievements member_achievements_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.member_achievements
    ADD CONSTRAINT member_achievements_pkey PRIMARY KEY (id);


--
-- Name: member_presentations member_presentations_member_id_version_key; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.member_presentations
    ADD CONSTRAINT member_presentations_member_id_version_key UNIQUE (member_id, version);


--
-- Name: member_presentations member_presentations_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.member_presentations
    ADD CONSTRAINT member_presentations_pkey PRIMARY KEY (id);


--
-- Name: member_reviews member_reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.member_reviews
    ADD CONSTRAINT member_reviews_pkey PRIMARY KEY (id);


--
-- Name: member_roles member_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.member_roles
    ADD CONSTRAINT member_roles_pkey PRIMARY KEY (id);


--
-- Name: members members_email_key; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.members
    ADD CONSTRAINT members_email_key UNIQUE (email);


--
-- Name: members members_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.members
    ADD CONSTRAINT members_pkey PRIMARY KEY (id);


--
-- Name: palms_snapshots palms_snapshots_chapter_id_member_id_period_start_period_en_key; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.palms_snapshots
    ADD CONSTRAINT palms_snapshots_chapter_id_member_id_period_start_period_en_key UNIQUE (chapter_id, member_id, period_start, period_end);


--
-- Name: palms_snapshots palms_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.palms_snapshots
    ADD CONSTRAINT palms_snapshots_pkey PRIMARY KEY (id);


--
-- Name: power_teams power_teams_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.power_teams
    ADD CONSTRAINT power_teams_pkey PRIMARY KEY (id);


--
-- Name: referral_needs referral_needs_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.referral_needs
    ADD CONSTRAINT referral_needs_pkey PRIMARY KEY (id);


--
-- Name: referrals referrals_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.referrals
    ADD CONSTRAINT referrals_pkey PRIMARY KEY (id);


--
-- Name: scores scores_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.scores
    ADD CONSTRAINT scores_pkey PRIMARY KEY (id);


--
-- Name: sponsorships sponsorships_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.sponsorships
    ADD CONSTRAINT sponsorships_pkey PRIMARY KEY (id);


--
-- Name: uploaded_files uploaded_files_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.uploaded_files
    ADD CONSTRAINT uploaded_files_pkey PRIMARY KEY (id);


--
-- Name: visitors visitors_pkey; Type: CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.visitors
    ADD CONSTRAINT visitors_pkey PRIMARY KEY (id);


--
-- Name: idx_achievements_member; Type: INDEX; Schema: public; Owner: mahardika
--

CREATE INDEX idx_achievements_member ON public.member_achievements USING btree (member_id);


--
-- Name: idx_achievements_unannounced; Type: INDEX; Schema: public; Owner: mahardika
--

CREATE INDEX idx_achievements_unannounced ON public.member_achievements USING btree (announced_at) WHERE (announced_at IS NULL);


--
-- Name: idx_action_items_csm; Type: INDEX; Schema: public; Owner: mahardika
--

CREATE INDEX idx_action_items_csm ON public.action_items USING btree (csm_meeting_id);


--
-- Name: idx_action_items_status; Type: INDEX; Schema: public; Owner: mahardika
--

CREATE INDEX idx_action_items_status ON public.action_items USING btree (status);


--
-- Name: idx_announcements_active; Type: INDEX; Schema: public; Owner: mahardika
--

CREATE INDEX idx_announcements_active ON public.announcements USING btree (is_active, start_date, expire_date);


--
-- Name: idx_chapter_content; Type: INDEX; Schema: public; Owner: mahardika
--

CREATE INDEX idx_chapter_content ON public.chapter_content USING btree (chapter_id, content_type);


--
-- Name: idx_imports_chapter; Type: INDEX; Schema: public; Owner: mahardika
--

CREATE INDEX idx_imports_chapter ON public.data_imports USING btree (chapter_id);


--
-- Name: idx_imports_status; Type: INDEX; Schema: public; Owner: mahardika
--

CREATE INDEX idx_imports_status ON public.data_imports USING btree (import_status);


--
-- Name: idx_meeting_activity_meeting; Type: INDEX; Schema: public; Owner: mahardika
--

CREATE INDEX idx_meeting_activity_meeting ON public.meeting_activity USING btree (meeting_id);


--
-- Name: idx_meeting_activity_member; Type: INDEX; Schema: public; Owner: mahardika
--

CREATE INDEX idx_meeting_activity_member ON public.meeting_activity USING btree (member_id);


--
-- Name: idx_member_roles_active; Type: INDEX; Schema: public; Owner: mahardika
--

CREATE INDEX idx_member_roles_active ON public.member_roles USING btree (is_active, chapter_id);


--
-- Name: idx_member_roles_member; Type: INDEX; Schema: public; Owner: mahardika
--

CREATE INDEX idx_member_roles_member ON public.member_roles USING btree (member_id);


--
-- Name: idx_palms_member; Type: INDEX; Schema: public; Owner: mahardika
--

CREATE INDEX idx_palms_member ON public.palms_snapshots USING btree (member_id);


--
-- Name: idx_palms_period; Type: INDEX; Schema: public; Owner: mahardika
--

CREATE INDEX idx_palms_period ON public.palms_snapshots USING btree (period_start, period_end);


--
-- Name: idx_presentations_member; Type: INDEX; Schema: public; Owner: mahardika
--

CREATE INDEX idx_presentations_member ON public.member_presentations USING btree (member_id);


--
-- Name: idx_referral_needs_member; Type: INDEX; Schema: public; Owner: mahardika
--

CREATE INDEX idx_referral_needs_member ON public.referral_needs USING btree (member_id);


--
-- Name: idx_reviews_member; Type: INDEX; Schema: public; Owner: mahardika
--

CREATE INDEX idx_reviews_member ON public.member_reviews USING btree (member_id);


--
-- Name: idx_reviews_status; Type: INDEX; Schema: public; Owner: mahardika
--

CREATE INDEX idx_reviews_status ON public.member_reviews USING btree (status);


--
-- Name: idx_sponsorships_sponsor; Type: INDEX; Schema: public; Owner: mahardika
--

CREATE INDEX idx_sponsorships_sponsor ON public.sponsorships USING btree (sponsor_id);


--
-- Name: action_items trg_updated_at; Type: TRIGGER; Schema: public; Owner: mahardika
--

CREATE TRIGGER trg_updated_at BEFORE UPDATE ON public.action_items FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();


--
-- Name: announcements trg_updated_at; Type: TRIGGER; Schema: public; Owner: mahardika
--

CREATE TRIGGER trg_updated_at BEFORE UPDATE ON public.announcements FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();


--
-- Name: chapter_content trg_updated_at; Type: TRIGGER; Schema: public; Owner: mahardika
--

CREATE TRIGGER trg_updated_at BEFORE UPDATE ON public.chapter_content FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();


--
-- Name: meeting_activity trg_updated_at; Type: TRIGGER; Schema: public; Owner: mahardika
--

CREATE TRIGGER trg_updated_at BEFORE UPDATE ON public.meeting_activity FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();


--
-- Name: member_presentations trg_updated_at; Type: TRIGGER; Schema: public; Owner: mahardika
--

CREATE TRIGGER trg_updated_at BEFORE UPDATE ON public.member_presentations FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();


--
-- Name: member_reviews trg_updated_at; Type: TRIGGER; Schema: public; Owner: mahardika
--

CREATE TRIGGER trg_updated_at BEFORE UPDATE ON public.member_reviews FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();


--
-- Name: referral_needs trg_updated_at; Type: TRIGGER; Schema: public; Owner: mahardika
--

CREATE TRIGGER trg_updated_at BEFORE UPDATE ON public.referral_needs FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();


--
-- Name: action_items action_items_csm_meeting_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.action_items
    ADD CONSTRAINT action_items_csm_meeting_id_fkey FOREIGN KEY (csm_meeting_id) REFERENCES public.csm_meetings(id) ON DELETE CASCADE;


--
-- Name: attendance attendance_meeting_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_meeting_id_fkey FOREIGN KEY (meeting_id) REFERENCES public.meetings(id);


--
-- Name: attendance attendance_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_member_id_fkey FOREIGN KEY (member_id) REFERENCES public.members(id);


--
-- Name: edu_contents edu_contents_chapter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.edu_contents
    ADD CONSTRAINT edu_contents_chapter_id_fkey FOREIGN KEY (chapter_id) REFERENCES public.chapters(id);


--
-- Name: edu_contents edu_contents_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.edu_contents
    ADD CONSTRAINT edu_contents_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.members(id);


--
-- Name: form_responses form_responses_form_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.form_responses
    ADD CONSTRAINT form_responses_form_id_fkey FOREIGN KEY (form_id) REFERENCES public.form_templates(id);


--
-- Name: form_responses form_responses_respondent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.form_responses
    ADD CONSTRAINT form_responses_respondent_id_fkey FOREIGN KEY (respondent_id) REFERENCES public.members(id);


--
-- Name: form_templates form_templates_chapter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.form_templates
    ADD CONSTRAINT form_templates_chapter_id_fkey FOREIGN KEY (chapter_id) REFERENCES public.chapters(id);


--
-- Name: form_templates form_templates_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.form_templates
    ADD CONSTRAINT form_templates_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.members(id);


--
-- Name: meetings meetings_chapter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.meetings
    ADD CONSTRAINT meetings_chapter_id_fkey FOREIGN KEY (chapter_id) REFERENCES public.chapters(id);


--
-- Name: members members_chapter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.members
    ADD CONSTRAINT members_chapter_id_fkey FOREIGN KEY (chapter_id) REFERENCES public.chapters(id);


--
-- Name: power_teams power_teams_chapter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.power_teams
    ADD CONSTRAINT power_teams_chapter_id_fkey FOREIGN KEY (chapter_id) REFERENCES public.chapters(id);


--
-- Name: referrals referrals_chapter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.referrals
    ADD CONSTRAINT referrals_chapter_id_fkey FOREIGN KEY (chapter_id) REFERENCES public.chapters(id);


--
-- Name: referrals referrals_giver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.referrals
    ADD CONSTRAINT referrals_giver_id_fkey FOREIGN KEY (giver_id) REFERENCES public.members(id);


--
-- Name: referrals referrals_receiver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.referrals
    ADD CONSTRAINT referrals_receiver_id_fkey FOREIGN KEY (receiver_id) REFERENCES public.members(id);


--
-- Name: visitors visitors_chapter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.visitors
    ADD CONSTRAINT visitors_chapter_id_fkey FOREIGN KEY (chapter_id) REFERENCES public.chapters(id);


--
-- Name: visitors visitors_invited_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mahardika
--

ALTER TABLE ONLY public.visitors
    ADD CONSTRAINT visitors_invited_by_id_fkey FOREIGN KEY (invited_by_id) REFERENCES public.members(id);


--
-- PostgreSQL database dump complete
--

\unrestrict xzwhCS1opHTUNUE7VPxLjCfVmOkscpy9Lb4mHoeP4iwCpY21Y1AL8NQW5TKXjlD

