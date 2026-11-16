import { error } from '@sveltejs/kit';
import { brainAdminRaw } from '$lib/server/brain';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ params, fetch }) => {
	if (!/^[0-9a-f]{64}$/.test(params.sha)) error(400, 'invalid sha256');
	return brainAdminRaw(fetch, `/admin/media/${params.sha}`);
};
