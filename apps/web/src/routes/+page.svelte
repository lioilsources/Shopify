<script lang="ts">
	import Chat from '$lib/components/Chat.svelte';
	import Filters from '$lib/components/Filters.svelte';
	import ProductCard from '$lib/components/ProductCard.svelte';
	import type { ActiveFilters, Product } from '$lib/types';

	let { data } = $props();

	let selectedCategory = $state<string | null>(null);
	let activeFilters = $state<ActiveFilters>({});
	let products = $state<Product[]>(data.products);

	const categoryFilters = $derived(
		selectedCategory
			? (data.categories.find((c) => c.slug === selectedCategory)?.filters ?? [])
			: []
	);

	function selectCategory(slug: string | null) {
		selectedCategory = slug;
		activeFilters = {};
	}

	// Refetch při každé změně kategorie nebo filtrů.
	$effect(() => {
		const params = new URLSearchParams();
		if (selectedCategory) params.set('category', selectedCategory);
		if (Object.keys(activeFilters).length) params.set('filters', JSON.stringify(activeFilters));
		fetch(`/api/products?${params}`)
			.then((r) => r.json())
			.then((rows: Product[]) => (products = rows));
	});
</script>

<svelte:head><title>ChatShop</title></svelte:head>

<div class="flex h-full flex-col">
	<!-- ~20 % — chat asistent -->
	<section class="h-[30dvh] min-h-44 border-b-2 border-slate-200 bg-white">
		<Chat />
	</section>

	<!-- ~80 % — galerie s filtry -->
	<section class="flex min-h-0 flex-1">
		<aside class="w-60 shrink-0 space-y-5 overflow-y-auto border-r border-slate-200 bg-white p-4">
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
