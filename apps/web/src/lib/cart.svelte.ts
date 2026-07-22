import { browser } from '$app/environment';
import type { ProductCard } from './types';

export interface CartItem {
	product: ProductCard;
	qty: number;
}

const STORAGE_KEY = 'chatshop-cart';

function load(): CartItem[] {
	if (!browser) return [];
	try {
		return JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '[]');
	} catch {
		return [];
	}
}

class Cart {
	items = $state<CartItem[]>(load());

	#save() {
		if (browser) localStorage.setItem(STORAGE_KEY, JSON.stringify(this.items));
	}

	add(product: ProductCard) {
		const existing = this.items.find((i) => i.product.id === product.id);
		if (existing) existing.qty += 1;
		else this.items.push({ product, qty: 1 });
		this.#save();
	}

	remove(productId: number) {
		this.items = this.items.filter((i) => i.product.id !== productId);
		this.#save();
	}

	get count() {
		return this.items.reduce((sum, i) => sum + i.qty, 0);
	}

	get total() {
		return this.items.reduce((sum, i) => sum + i.qty * i.product.price_czk, 0);
	}
}

export const cart = new Cart();
