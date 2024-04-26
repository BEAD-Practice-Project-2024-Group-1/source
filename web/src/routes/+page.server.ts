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

	console.debug('All Districts Length:', districts.length);

	return {
		planning_areas: districts.map((q) => q.geojson)
	};
};
