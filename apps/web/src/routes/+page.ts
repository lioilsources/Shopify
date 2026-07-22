import type { Category, Product } from '$lib/types';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
	const [categories, products] = await Promise.all([
		fetch('/api/categories').then((r) => r.json() as Promise<Category[]>),
		fetch('/api/products').then((r) => r.json() as Promise<Product[]>)
	]);
	return { categories, products };
};
