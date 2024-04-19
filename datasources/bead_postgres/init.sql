CREATE TABLE public.taxi_availability (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    batch_id uuid NOT NULL,
    location geometry(Point, 4326)
);

