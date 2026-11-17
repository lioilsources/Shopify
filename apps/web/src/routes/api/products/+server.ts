import { json } from '@sveltejs/kit';
import { sql } from '$lib/server/db';
import type { ActiveFilters } from '$lib/types';
import type { RequestHandler } from './$types';

/**
 * GET /api/products?category=<slug>&filters=<url-encoded JSON ActiveFilters>&ids=<1,2,3>
 *
 * Only listed products are public. `ids` is the chat selection: the result
 * keeps the order given by the chat (search relevance).
 *
 * Překlad aktivních filtrů na SQL nad JSONB `attributes`:
 *  - price_czk je sloupec, ostatní klíče jdou do attributes
 *  - set:   hodnota je string NEBO pole stringů -> průnik s vybranými
 *  - range: (attributes->>key)::numeric v mezích
 *  - bool:  (attributes->>key)::boolean
 *  - text:  ILIKE přes název, popis i atributy
 */
export const GET: RequestHandler = async ({ url }) => {
	const category = url.searchParams.get('category');
	let filters: ActiveFilters = {};
	try {
		filters = JSON.parse(url.searchParams.get('filters') ?? '{}');
	} catch {
		// neplatný JSON ignorujeme
	}

	const ids = (url.searchParams.get('ids') ?? '')
		.split(',')
		.map((v) => Number.parseInt(v, 10))
		.filter((v) => Number.isInteger(v) && v > 0)
		.slice(0, 200);

	const conditions = [sql`p.status = 'listed'`];
	if (category) conditions.push(sql`c.slug = ${category}`);
	if (ids.length) conditions.push(sql`p.id = ANY(${ids})`);

	for (const [key, value] of Object.entries(filters)) {
		if (value == null) continue;
		if (Array.isArray(value)) {
			if (value.length === 0) continue;
			conditions.push(
				sql`(p.attributes->>${key} = ANY(${value}) OR p.attributes->${key} ?| ${value})`
			);
		} else if (typeof value === 'boolean') {
			conditions.push(sql`(p.attributes->>${key})::boolean = ${value}`);
		} else if (typeof value === 'string') {
			const like = `%${value}%`;
			conditions.push(
				sql`(p.name ILIKE ${like} OR p.description ILIKE ${like} OR p.attributes::text ILIKE ${like})`
			);
		} else {
			const { min, max } = value;
			const expr =
				key === 'price_czk' ? sql`p.price_czk` : sql`(p.attributes->>${key})::numeric`;
			if (key !== 'price_czk') conditions.push(sql`p.attributes ? ${key}`);
			if (min != null) conditions.push(sql`${expr} >= ${min}`);
			if (max != null) conditions.push(sql`${expr} <= ${max}`);
		}
	}

	const where = conditions
		.slice(1)
		.reduce((acc, c) => sql`${acc} AND ${c}`, sql`WHERE ${conditions[0]}`);
	const order = ids.length ? sql`array_position(${ids}::int[], p.id)` : sql`p.id`;

	const rows = await sql`
		SELECT p.id, c.slug AS category_slug, p.name, p.description,
			p.price_czk::float AS price_czk, p.image_url, p.attributes, p.demo
		FROM products p
		JOIN categories c ON c.id = p.category_id
		${where}
		ORDER BY ${order}
	`;
	return json(rows);
};
