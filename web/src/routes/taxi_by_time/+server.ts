import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';
import postgres from 'postgres';
import dayjs from 'dayjs';
import duration from 'dayjs/plugin/duration';

dayjs.extend(duration);

const sql = postgres({
	host: env.DATABASE_HOST,
	port: 5432,
	database: 'bead',
	username: env.USER,
	password: env.PASSWORD
});

export type HealthData = {
	uptime: number;
	version: string;
	memoryUsage: NodeJS.MemoryUsage;
	message: string;
};

export const GET: RequestHandler = async ({ url }) => {
	const time = parseInt(url.searchParams.get('time') || '');

	const datetimeA = dayjs()
		.subtract(dayjs.duration({ days: 1 }))
		.set('hour', 0)
		.set('minute', 0)
		.set('second', 0)
		.set('millisecond', 0)
		.add(dayjs.duration({ minutes: time }));

	const datetimeB = datetimeA.add(dayjs.duration({ minutes: 1 }));

	const taxi_availability = await sql`
	    SELECT
	        batch_id as b_id,
	        created_at,
	        ST_X(ST_Transform (location, 4326)) AS "lon",
	        ST_Y(ST_Transform (location, 4326)) AS "lat"
	    FROM taxi_availability
	    WHERE created_at >= ${datetimeA} AND created_at < ${datetimeB};
	    `;

	const responseBody = {
		data: taxi_availability,
		message: 'Success',
		sent_at: new Date().toISOString()
	};

	return new Response(JSON.stringify(responseBody));
};
