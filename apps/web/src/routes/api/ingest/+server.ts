import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

const BRAIN_URL = env.BRAIN_URL ?? 'http://localhost:8000';

export const POST: RequestHandler = async ({ request, fetch }) => {
	const upstream = await fetch(`${BRAIN_URL}/ingest`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: await request.text()
	});
	return new Response(await upstream.text(), {
		status: upstream.status,
		headers: { 'Content-Type': 'application/json' }
	});
};
