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
	/** sample from a demo batch, labelled on the web */
	demo?: boolean;
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

/** Filters the brain recognised in a chat query (rule based, no LLM). */
export interface ChatFilters {
	filters: Record<string, string[]>;
	matches: { key: string; label: string; value: string }[];
	/** true = the query was only filters; the gallery shows every match */
	only: boolean;
	total: number | null;
}

export interface ChatMsg {
	role: 'user' | 'assistant';
	content: string;
	products?: ProductCard[];
	filters?: ChatFilters;
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

export type FitnessGrade = 'ok' | 'upscale' | 'caveat' | 'no';

export interface FitnessRow {
	profile_id: string;
	label_cs: string;
	group: string;
	grade: FitnessGrade;
	/** [short, long] in cm, null when the profile is not offered */
	max_cm: [number, number] | null;
	note: string;
}

export interface ProductDetail extends Product {
	category_name: string;
}
