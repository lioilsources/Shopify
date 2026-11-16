<script lang="ts">
	import type { AdminProduct, ProductStatus } from '$lib/types';

	const PAGE = 50;
	const LABELS: Record<ProductStatus, string> = {
		draft: 'Ke schválení',
		listed: 'Ve výloze',
		hidden: 'Skryté'
	};

	let status = $state<ProductStatus>('draft');
	let offset = $state(0);
	let items = $state<AdminProduct[]>([]);
	let total = $state(0);
	let counts = $state<Record<ProductStatus, number>>({ draft: 0, listed: 0, hidden: 0 });
	let selected = $state<Set<number>>(new Set());
	let error = $state<string | null>(null);
	let busy = $state(false);

	async function load() {
		error = null;
		const res = await fetch(`/api/admin/products?status=${status}&limit=${PAGE}&offset=${offset}`);
		const body = await res.json();
		if (!res.ok) {
			error = body.detail ?? res.statusText;
			items = [];
			return;
		}
		items = body.items;
		total = body.total;
		counts = body.counts;
		selected = new Set();
	}

	$effect(() => {
		void status;
		void offset;
		load();
	});

	function toggle(id: number) {
		const next = new Set(selected);
		if (next.has(id)) next.delete(id);
		else next.add(id);
		selected = next;
	}

	function toggleAll() {
		selected = selected.size === items.length ? new Set() : new Set(items.map((p) => p.id));
	}

	async function setStatus(target: ProductStatus) {
		if (!selected.size) return;
		busy = true;
		try {
			const res = await fetch('/api/admin/products/status', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ ids: [...selected], status: target })
			});
			const body = await res.json();
			if (!res.ok) throw new Error(body.detail ?? res.statusText);
			await load();
		} catch (err) {
			error = String(err);
		} finally {
			busy = false;
		}
	}
</script>

<svelte:head><title>Admin — schvalování</title></svelte:head>

<div class="h-full space-y-4 overflow-y-auto p-6">
	<div class="flex flex-wrap items-center gap-2">
		<h1 class="mr-4 text-xl font-bold">Schvalování</h1>
		{#each Object.entries(LABELS) as [key, label] (key)}
			<button
				class={'rounded-full px-3 py-1 text-sm ' +
					(status === key ? 'bg-slate-900 text-white' : 'bg-slate-100 hover:bg-slate-200')}
				onclick={() => {
					status = key as ProductStatus;
					offset = 0;
				}}
			>
				{label} ({counts[key as ProductStatus]})
			</button>
		{/each}
	</div>

	<p class="text-sm text-slate-500">
		Nic není veřejné, dokud to tady někdo neschválí. Filtry kategorie rostou až ze schválených položek.
	</p>

	<div class="flex flex-wrap items-center gap-2">
		<button class="rounded border border-slate-300 px-3 py-1 text-sm" onclick={toggleAll} disabled={!items.length}>
			{selected.size === items.length && items.length ? 'Zrušit výběr' : 'Vybrat vše na stránce'}
		</button>
		<span class="text-sm text-slate-500">vybráno {selected.size}</span>
		{#if status !== 'listed'}
			<button
				class="rounded bg-emerald-600 px-3 py-1 text-sm font-medium text-white disabled:opacity-40"
				disabled={busy || !selected.size}
				onclick={() => setStatus('listed')}>Schválit do výlohy</button
			>
		{/if}
		{#if status !== 'hidden'}
			<button
				class="rounded bg-slate-600 px-3 py-1 text-sm font-medium text-white disabled:opacity-40"
				disabled={busy || !selected.size}
				onclick={() => setStatus('hidden')}>Skrýt</button
			>
		{/if}
		{#if status !== 'draft'}
			<button
				class="rounded border border-slate-300 px-3 py-1 text-sm disabled:opacity-40"
				disabled={busy || !selected.size}
				onclick={() => setStatus('draft')}>Vrátit ke schválení</button
			>
		{/if}
	</div>

	{#if error}<p class="rounded bg-red-50 p-3 text-sm text-red-700">{error}</p>{/if}

	{#if !items.length && !error}
		<p class="text-slate-400">Nic tu není.</p>
	{:else}
		<div class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
			{#each items as p (p.id)}
				<button
					class={'overflow-hidden rounded-lg border-2 bg-white text-left ' +
						(selected.has(p.id) ? 'border-emerald-500' : 'border-slate-200')}
					onclick={() => toggle(p.id)}
				>
					{#if p.image_url}
						<img src={p.image_url} alt={p.name} class="w-full object-contain" loading="lazy" />
					{/if}
					<div class="space-y-0.5 p-2">
						<p class="line-clamp-2 text-xs font-medium">{p.name}</p>
						<p class="text-xs text-slate-400">{p.category_slug} · #{p.id}</p>
					</div>
				</button>
			{/each}
		</div>
		<div class="flex items-center gap-3 text-sm">
			<button disabled={offset === 0} class="disabled:opacity-30" onclick={() => (offset = Math.max(0, offset - PAGE))}>← předchozí</button>
			<span class="text-slate-500">{offset + 1}–{Math.min(offset + PAGE, total)} z {total}</span>
			<button disabled={offset + PAGE >= total} class="disabled:opacity-30" onclick={() => (offset += PAGE)}>další →</button>
		</div>
	{/if}
</div>
