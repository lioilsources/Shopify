import { brainAdmin } from '$lib/server/brain';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request, fetch }) =>
	brainAdmin(fetch, '/admin/products/status', { method: 'POST', body: await request.text() });
