export type FilterKind = 'text' | 'range' | 'set' | 'bool';

export interface FilterSchema {
	attr_key: string;
	label: string;
	kind: FilterKind;
	config: { values?: string[]; min?: number; max?: number; unit?: string };
}

export interface Category {
	id: number;
	slug: string;
	name: string;
	filters: FilterSchema[];
}

export interface Product {
	id: number;
	category_slug: string;
	name: string;
	description: string;
	price_czk: number;
	image_url: string;
	attributes: Record<string, unknown>;
}

/** Aktivní hodnoty filtrů: set -> string[], range -> {min,max}, bool -> boolean, text -> string */
export type ActiveFilters = Record<
	string,
	string[] | { min?: number; max?: number } | boolean | string
>;

export interface ProductCard {
	id: number;
	name: string;
	price_czk: number;
	image_url: string;
	category_slug: string;
}

export interface ChatMsg {
	role: 'user' | 'assistant';
	content: string;
	products?: ProductCard[];
}
