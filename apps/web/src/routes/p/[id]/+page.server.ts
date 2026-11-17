import { error } from '@sveltejs/kit';
import { sql } from '$lib/server/db';
import { BRAIN_URL } from '$lib/server/brain';
import type { FitnessRow, ProductDetail } from '$lib/types';
import type { PageServerLoad } from './$types';

// Rendered on the server so that catalogue pages are indexable (plan 02 §6).
export const load: PageServerLoad = async ({ params, fetch }) => {
	const id = Number(params.id);
	if (!Number.isInteger(id) || id <= 0) error(404, 'Produkt nenalezen');

	const [product] = await sql<ProductDetail[]>`
		SELECT p.id, c.slug AS category_slug, c.name AS category_name, p.name, p.description,
			p.price_czk::float AS price_czk, p.image_url, p.attributes, p.demo
		FROM products p JOIN categories c ON c.id = p.category_id
		WHERE p.id = ${id} AND p.status = 'listed'
	`;
	if (!product) error(404, 'Produkt nenalezen');

	let fitness: FitnessRow[] = [];
	try {
		const res = await fetch(`${BRAIN_URL}/products/${id}/fitness`);
		if (res.ok) fitness = (await res.json()).items;
	} catch {
		// Brain down: the page still renders without the fitness table.
	}
	return { product, fitness };
};
