CREATE TABLE public.taxi_availability (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    batch_id uuid NOT NULL,
    location geometry(Point, 4326)
);

CREATE TABLE public.districts (
    name text NOT NULL PRIMARY KEY,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    location geometry(MultiPolygon, 4326)
    -- dow text NOT NULL,
    -- time numeric NOT NULL
)

CREATE SCHEMA IF NOT EXIST processed

CREATE TABLE processed.district_taxi_availability (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    batch_id uuid NOT NULL,
    district text NOT NULL,
    available_taxi_count integer NOT NULL,
    dow integer NOT NULL,
    time integer NOT NULL
);