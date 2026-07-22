import { json } from '@sveltejs/kit';
import { sql } from '$lib/server/db';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async () => {
	const rows = await sql`
		SELECT c.id, c.slug, c.name,
			COALESCE(
				json_agg(
					json_build_object(
						'attr_key', f.attr_key, 'label', f.label,
						'kind', f.kind, 'config', f.config
					) ORDER BY f.attr_key
				) FILTER (WHERE f.id IS NOT NULL),
				'[]'
			) AS filters
		FROM categories c
		LEFT JOIN filter_schemas f ON f.category_id = c.id
		GROUP BY c.id
		ORDER BY c.name
	`;
	return json(rows);
};
