import { BRAIN_URL } from '$lib/server/brain';
import type { RequestHandler } from './$types';

// Proxy SSE streamu z brain služby (drží DB přístup i LLM na backendu).
export const POST: RequestHandler = async ({ request, fetch }) => {
	const upstream = await fetch(`${BRAIN_URL}/chat`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: await request.text()
	});
	return new Response(upstream.body, {
		status: upstream.status,
		headers: {
			'Content-Type': 'text/event-stream',
			'Cache-Control': 'no-cache'
		}
	});
};
