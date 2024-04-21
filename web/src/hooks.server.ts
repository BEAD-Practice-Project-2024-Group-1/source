import { Kafka } from 'kafkajs';
import { nanoid } from 'nanoid';
import { env } from '$env/dynamic/private';

import { building } from '$app/environment';
import { GlobalThisWSS } from '$lib/server/webSocketUtils';
import type { Handle } from '@sveltejs/kit';
import type { ExtendedGlobal, ExtendedWebSocket } from '$lib/server/webSocketUtils';
import type { TaxiAvailability } from '$lib/Map/index.svelte';

/** Required Env Vars  */
if (!env.KAFKA_BROKER_ADDR) {
	throw 'KAFKA_BROKER_ADDR must be defined.';
}

if (!env.USER) {
	throw 'USER must be defined.';
}

if (!env.PASSWORD) {
	throw 'PASSWORD must be defined.';
}

if (!env.DATABASE_HOST) {
	throw 'DATABASE_HOST must be defined.';
}

/** Web Sockets */
let wssInitialized = false;
let cachedTaxis: Array<TaxiAvailability> = [];

const startupWebsocketServer = () => {
	if (wssInitialized) return;
	console.debug('[wss:kit] setup');
	const wss = (globalThis as ExtendedGlobal)[GlobalThisWSS];
	if (wss !== undefined) {
		wss.on('connection', (ws: ExtendedWebSocket, _request) => {
			console.debug(
				`[wss:kit] client connected (${ws.socketId}), Cache Length: ${cachedTaxis.length}`
			);

			ws.send(JSON.stringify(cachedTaxis)); // send cache to new client whenever they connect

			ws.on('close', () => {
				console.log(`[wss:kit] client disconnected (${ws.socketId})`);
			});
		});
		wssInitialized = true;
	}
};

export const handle = (async ({ event, resolve }) => {
	startupWebsocketServer();

	// Skip WebSocket server when pre-rendering pages
	if (!building) {
		const wss = (globalThis as ExtendedGlobal)[GlobalThisWSS];
		if (wss !== undefined) {
			event.locals.wss = wss;
		}
	}

	const response = await resolve(event, {
		filterSerializedResponseHeaders: (name) => name === 'content-type'
	});

	return response;
}) satisfies Handle;

const kafka = new Kafka({
	clientId: nanoid(),
	brokers: [env.KAFKA_BROKER_ADDR]
});

const consumer = kafka.consumer({ groupId: 'bead-web' });

await consumer.connect();
await consumer.subscribe({ topic: 'availTaxis' });

await consumer.run({
	eachMessage: async ({ message }) => {
		const wss = (globalThis as ExtendedGlobal)[GlobalThisWSS];

		if (!message || !message.value) {
			console.warn('message or message.value, aborting wss message broadcast');
			return;
		}

		const msg = message?.value?.toString();
		const data = JSON.parse(msg);

		if (cachedTaxis && cachedTaxis.length > 0 && cachedTaxis[0].b_id != data.b_id) {
			cachedTaxis = []; // reset cache when batch changes
		}

		cachedTaxis.push(data);

		if (!wss || !msg) {
			console.warn('wss or msg not defined, aborting wss message broadcast');
			return;
		}

		wss.clients.forEach((c) => {
			console.log('Sending ', msg);
			c.send(msg);
		});
	}
});
