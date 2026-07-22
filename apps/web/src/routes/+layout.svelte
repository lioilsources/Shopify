<script lang="ts">
	import '../app.css';
	import { cart } from '$lib/cart.svelte';

	let { children } = $props();
</script>

<div class="flex h-dvh flex-col">
	<header class="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-2">
		<a href="/" class="text-lg font-bold tracking-tight">🛍️ ChatShop</a>
		<nav class="flex items-center gap-4 text-sm">
			<a href="/admin/ingest" class="text-slate-500 hover:text-slate-900">Admin</a>
			<span class="rounded-full bg-slate-900 px-3 py-1 font-medium text-white">
				🛒 {cart.count} ks · {cart.total.toLocaleString('cs')} Kč
			</span>
		</nav>
	</header>
	<main class="min-h-0 flex-1">
		{@render children()}
	</main>
</div>
