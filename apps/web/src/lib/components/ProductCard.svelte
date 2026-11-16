<script lang="ts">
	import type { Product } from '$lib/types';
	import { cart } from '$lib/cart.svelte';

	let { product }: { product: Product } = $props();
</script>

<article class="flex flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
	<img src={product.image_url} alt={product.name} class="aspect-square w-full object-cover" />
	<div class="flex flex-1 flex-col gap-1 p-3">
		<h3 class="font-medium leading-tight">{product.name}</h3>
		<p class="line-clamp-2 text-xs text-slate-500">{product.description}</p>
		<div class="mt-auto flex items-center justify-between pt-2">
			{#if product.price_czk != null}
				<span class="text-lg font-semibold">{product.price_czk.toLocaleString('cs')} Kč</span>
			{:else}
				<span class="text-sm text-slate-500">cena podle provedení</span>
			{/if}
			<button
				disabled={product.price_czk == null}
				onclick={() =>
					cart.add({
						id: product.id,
						name: product.name,
						price_czk: product.price_czk,
						image_url: product.image_url,
						category_slug: product.category_slug
					})}
				class="rounded-lg bg-sky-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-sky-700 disabled:opacity-40"
			>
				Do košíku
			</button>
		</div>
	</div>
</article>
