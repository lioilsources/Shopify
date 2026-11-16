import { env } from '$env/dynamic/private';

export const BRAIN_URL = env.BRAIN_URL ?? 'http://localhost:8000';

/** Calls a protected brain endpoint; the admin token never leaves the server. */
export async function brainAdmin(fetchFn: typeof fetch, path: string, init: RequestInit = {}) {
	const headers = new Headers(init.headers);
	headers.set('X-Admin-Token', env.ADMIN_TOKEN ?? '');
	if (init.body) headers.set('Content-Type', 'application/json');
	const upstream = await fetchFn(`${BRAIN_URL}${path}`, { ...init, headers });
	return new Response(await upstream.text(), {
		status: upstream.status,
		headers: { 'Content-Type': 'application/json' }
	});
}

/** Streams a protected binary (e.g. a private original) without exposing the token. */
export async function brainAdminRaw(fetchFn: typeof fetch, path: string) {
	const upstream = await fetchFn(`${BRAIN_URL}${path}`, {
		headers: { 'X-Admin-Token': env.ADMIN_TOKEN ?? '' }
	});
	return new Response(upstream.body, {
		status: upstream.status,
		headers: {
			'Content-Type': upstream.headers.get('Content-Type') ?? 'application/octet-stream',
			'Cache-Control': 'private, max-age=3600'
		}
	});
}
