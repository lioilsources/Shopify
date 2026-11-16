import { error } from '@sveltejs/kit';
import { BRAIN_URL } from '$lib/server/brain';
import type { RequestHandler } from './$types';

/** Public watermarked preview; brain serves it only for listed products. */
export const GET: RequestHandler = async ({ params, fetch }) => {
	if (!/^[0-9a-f]{64}\.jpg$/.test(params.file)) error(404, 'Náhled nenalezen');
	const upstream = await fetch(`${BRAIN_URL}/media/preview/${params.file}`);
	if (!upstream.ok) error(upstream.status === 404 ? 404 : 502, 'Náhled nenalezen');
	return new Response(upstream.body, {
		headers: {
			'Content-Type': 'image/jpeg',
			'Cache-Control': upstream.headers.get('Cache-Control') ?? 'public, max-age=86400'
		}
	});
};
