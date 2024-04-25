import type { PageServerLoad } from './$types';
import postgres from 'postgres';
import { env } from '$env/dynamic/private';
import type { Feature } from 'geojson';

const sql = postgres({
	host: env.DATABASE_HOST,
	port: 5432,
	database: 'bead',
	username: env.USER,
	password: env.PASSWORD
});

export const load: PageServerLoad = async () => {
	const districts = (await sql`
			SELECT jsonb_build_object(
				'type', 'Feature',
				'id', name,
				'geometry', st_asgeojson( location )::jsonb ) as geojson
			FROM districts;`) as Array<{ geojson: Feature }>;

	const taxi_availability = await sql`
			SELECT 
				batch_id as b_id,
				created_at,
				ST_X(ST_Transform (location, 4326)) AS "lon",
				ST_Y(ST_Transform (location, 4326)) AS "lat"
			FROM taxi_availability
			WHERE created_at >= date_subtract(now(), '1 day'::interval) AND created_at < now();
	`;

	console.debug('Full Previous Day Data Length:', taxi_availability.length);
	console.debug('All Districts Length:', districts.length);

	return {
		planning_areas: districts.map((q) => q.geojson),
		taxi_availability
	};
};
