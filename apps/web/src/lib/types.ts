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
	/** null = priced per variant ("na poptávku") */
	price_czk: number | null;
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
	price_czk: number | null;
	image_url: string;
	category_slug: string;
}

export interface ChatMsg {
	role: 'user' | 'assistant';
	content: string;
	products?: ProductCard[];
}

export type ProductStatus = 'draft' | 'listed' | 'hidden';

export interface GateReason {
	code: string;
	detail: string;
	blocking: boolean;
}

export interface AdminProduct extends Product {
	status: ProductStatus;
	source_key: string | null;
	image_sha256: string | null;
	gate_reasons: GateReason[];
	created_at: string | null;
	reviewed_at: string | null;
}
