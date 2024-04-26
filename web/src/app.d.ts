// See https://kit.svelte.dev/docs/types#app

import type { ExtendedWebSocket } from '$lib/server/webSocketUtils';

// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		interface Locals {
			wss: Server<ExtendedWebSocket>;
		}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}

		type HTTPResponseBody<T> = {
			data?: T;
			message: string;
			sent_at: ISO8601Date;
			errors?: Array<Error>;
		};
	}
}

export {};
