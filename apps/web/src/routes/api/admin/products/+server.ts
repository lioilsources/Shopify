import { brainAdmin } from '$lib/server/brain';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ url, fetch }) =>
	brainAdmin(fetch, `/admin/products?${url.searchParams}`);
