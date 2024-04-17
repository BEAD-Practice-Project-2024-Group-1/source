CREATE TABLE public.taxi_availability (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    location geometry(Point, 4326)
);

CREATE TABLE public.districts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    name text NOT NULL,
    location geometry(Polygon, 4326)
)