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
