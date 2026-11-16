import { brainAdmin } from '$lib/server/brain';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ fetch }) =>
	brainAdmin(fetch, '/admin/import/gallery', { method: 'POST' });
