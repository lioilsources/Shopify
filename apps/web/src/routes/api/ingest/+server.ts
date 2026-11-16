import { brainAdmin } from '$lib/server/brain';
import type { RequestHandler } from './$types';

// Admin-only; protected by the brain token and, in deployment, by Cloudflare Access.
export const POST: RequestHandler = async ({ request, fetch }) =>
	brainAdmin(fetch, '/ingest', { method: 'POST', body: await request.text() });
