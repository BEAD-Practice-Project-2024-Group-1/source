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
)
