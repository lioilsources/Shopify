<script lang="ts">
	import Chat from '$lib/components/Chat.svelte';
	import Filters from '$lib/components/Filters.svelte';
	import ProductCard from '$lib/components/ProductCard.svelte';
	import type { ActiveFilters, ChatFilters, Product } from '$lib/types';
	import { page } from '$app/state';

	let { data } = $props();

	// ?category=<slug> opens the gallery on one theme (links from the product detail).
	let selectedCategory = $state<string | null>(page.url.searchParams.get('category'));
	let activeFilters = $state<ActiveFilters>({});
	// Selection set by the chat: product ids in relevance order (null = whole catalogue).
	let chatSelection = $state<{ ids: number[]; query: string } | null>(null);
	// Starts from the server-rendered list, then follows category, filters and chat.
	let fetched = $state<Product[] | null>(null);
	const products = $derived(fetched ?? data.products);

	const categoryFilters = $derived(
		selectedCategory
			? (data.categories.find((c) => c.slug === selectedCategory)?.filters ?? [])
			: []
	);

	function selectCategory(slug: string | null) {
		selectedCategory = slug;
		chatCategory = false;
		activeFilters = {};
	}

	// Category chosen by the chat (not by a click); a new query may undo it.
	let chatCategory = false;
	let showFilters = $state(false);

	function onChatQuery() {
		// Every query starts from scratch: earlier chat filters and selection go away.
		if (chatFilterQuery) {
			activeFilters = {};
			chatFilterQuery = null;
		}
		if (chatCategory) {
			selectedCategory = null;
			chatCategory = false;
		}
		chatSelection = null;
	}

	function onChatFilters(found: ChatFilters, query: string) {
		// Filters from the chat replace the current ones; a query of filters only
		// shows every match instead of the chat's top results.
		if (found.category) {
			selectedCategory = found.category;
			chatCategory = true;
		}
		activeFilters = { ...found.filters };
		chatSelection = found.only ? null : chatSelection;
		chatFilterQuery = query;
	}

	let chatFilterQuery = $state<string | null>(null);

	function onChatSelect(ids: number[], query: string) {
		// An empty answer leaves the gallery as it is.
		if (ids.length) chatSelection = { ids, query };
	}

	// Refetch on every change of category, filters or chat selection; filters narrow
	// the chat selection further.
	let requestSeq = 0;
	$effect(() => {
		const params = new URLSearchParams();
		if (selectedCategory) params.set('category', selectedCategory);
		if (Object.keys(activeFilters).length) params.set('filters', JSON.stringify(activeFilters));
		if (chatSelection) params.set('ids', chatSelection.ids.join(','));
		const seq = ++requestSeq;
		fetch(`/api/products?${params}`)
			.then((r) => r.json())
			.then((rows: Product[]) => {
				if (seq === requestSeq) fetched = rows;
			});
	});
</script>

<svelte:head><title>SlopMarket — AI motivy k potisku</title></svelte:head>

<div class="flex h-full flex-col">
	<!-- ~20 % — chat asistent -->
	<section class="h-[30dvh] min-h-44 border-b-2 border-slate-200 bg-white">
		<Chat category={selectedCategory} onselect={onChatSelect} onfilters={onChatFilters} onquery={onChatQuery} />
	</section>

	<!-- ~80 % — galerie s filtry -->
	<section class="flex min-h-0 flex-1 flex-col md:flex-row">
		<!-- On phones the sidebar folds into a toggle above the gallery. -->
		<button
			class="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-2 text-sm font-medium md:hidden"
			onclick={() => (showFilters = !showFilters)}
			aria-expanded={showFilters}
		>
			<span>
				Kategorie a filtry{selectedCategory
					? `: ${data.categories.find((c) => c.slug === selectedCategory)?.name ?? ''}`
					: ''}
			</span>
			<span aria-hidden="true">{showFilters ? '▲' : '▼'}</span>
		</button>
		<aside
			class={(showFilters ? 'block' : 'hidden') +
				' max-h-[45dvh] w-full shrink-0 space-y-5 overflow-y-auto border-b border-slate-200 bg-white p-4 md:block md:max-h-none md:w-60 md:border-r md:border-b-0'}
		>
			<div>
				<h2 class="mb-1.5 text-sm font-semibold text-slate-700">Kategorie</h2>
				<div class="flex flex-col gap-1">
					<button
						class={'rounded px-2 py-1 text-left text-sm ' +
							(selectedCategory === null ? 'bg-sky-100 font-medium text-sky-800' : 'hover:bg-slate-100')}
						onclick={() => selectCategory(null)}
					>
						Vše
					</button>
					{#each data.categories as cat (cat.slug)}
						<button
							class={'rounded px-2 py-1 text-left text-sm ' +
								(selectedCategory === cat.slug
									? 'bg-sky-100 font-medium text-sky-800'
									: 'hover:bg-slate-100')}
							onclick={() => selectCategory(cat.slug)}
						>
							{cat.name}
						</button>
					{/each}
				</div>
			</div>

			{#if categoryFilters.length}
				<Filters schemas={categoryFilters} bind:active={activeFilters} />
			{:else if selectedCategory === null}
				<p class="text-xs text-slate-400">Filtry se zobrazí po výběru kategorie.</p>
			{/if}
		</aside>

		<div class="flex-1 overflow-y-auto p-4">
			{#if chatSelection}
				<div class="mb-3 flex items-center gap-2 text-sm">
					<span class="rounded-full bg-sky-100 px-3 py-1 text-sky-800">
						Výběr z chatu: „{chatSelection.query}“
					</span>
					<button class="text-slate-500 underline hover:text-slate-900" onclick={() => (chatSelection = null)}>
						Zobrazit vše
					</button>
				</div>
			{/if}
			{#if products.length === 0}
				<p class="mt-8 text-center text-slate-400">Žádné produkty neodpovídají filtrům.</p>
			{:else}
				<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
					{#each products as product (product.id)}
						<ProductCard {product} />
					{/each}
				</div>
			{/if}
		</div>
	</section>
</div>
