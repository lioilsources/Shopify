<script lang="ts">
	let form = $state({
		category_slug: 'tricka',
		name: '',
		price_czk: '',
		image_url: '',
		url: '',
		raw_text: '',
		attributes: '{}'
	});
	let result = $state<string | null>(null);
	let error = $state<string | null>(null);
	let busy = $state(false);

	async function submit(e: SubmitEvent) {
		e.preventDefault();
		result = error = null;
		let attributes: Record<string, unknown>;
		try {
			attributes = JSON.parse(form.attributes || '{}');
		} catch {
			error = 'Atributy nejsou validní JSON.';
			return;
		}
		busy = true;
		try {
			const res = await fetch('/api/ingest', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					category_slug: form.category_slug,
					name: form.name,
					price_czk: form.price_czk === '' || form.price_czk == null ? null : Number(form.price_czk),
					image_url: form.image_url,
					url: form.url || null,
					raw_text: form.raw_text || null,
					attributes
				})
			});
			const body = await res.json();
			if (!res.ok) throw new Error(body.detail ?? res.statusText);
			result = JSON.stringify(body, null, 2);
		} catch (err) {
			error = String(err);
		} finally {
			busy = false;
		}
	}
</script>

<svelte:head><title>Admin — vložení zboží</title></svelte:head>

<div class="mx-auto max-w-2xl space-y-4 overflow-y-auto p-6">
	<h1 class="text-xl font-bold">Vložení zboží</h1>
	<p class="text-sm text-slate-500">
		Pipeline dohledá informace o položce, extrahuje atributy (s LLM; bez něj použije ručně zadané)
		a založí ji jako koncept. Veřejná je až po schválení, kdy rozšíří filtry kategorie.
	</p>

	<form onsubmit={submit} class="space-y-3">
		<label class="block text-sm">
			Kategorie (slug)
			<input bind:value={form.category_slug} required class="mt-1 w-full rounded border border-slate-300 px-2 py-1.5" />
		</label>
		<label class="block text-sm">
			Název
			<input bind:value={form.name} required class="mt-1 w-full rounded border border-slate-300 px-2 py-1.5" />
		</label>
		<div class="grid grid-cols-2 gap-3">
			<label class="block text-sm">
				Cena (Kč, nepovinná)
				<input bind:value={form.price_czk} type="number" min="0" step="0.01" class="mt-1 w-full rounded border border-slate-300 px-2 py-1.5" />
			</label>
			<label class="block text-sm">
				URL obrázku
				<input bind:value={form.image_url} class="mt-1 w-full rounded border border-slate-300 px-2 py-1.5" />
			</label>
		</div>
		<label class="block text-sm">
			URL položky (pro web lookup — zatím TODO)
			<input bind:value={form.url} class="mt-1 w-full rounded border border-slate-300 px-2 py-1.5" />
		</label>
		<label class="block text-sm">
			Text o položce (podklad pro LLM extrakci atributů)
			<textarea bind:value={form.raw_text} rows="4" class="mt-1 w-full rounded border border-slate-300 px-2 py-1.5"></textarea>
		</label>
		<label class="block text-sm">
			Atributy ručně (JSON, přepíší extrahované)
			<textarea bind:value={form.attributes} rows="3" class="mt-1 w-full rounded border border-slate-300 px-2 py-1.5 font-mono text-xs"></textarea>
		</label>
		<button
			type="submit"
			disabled={busy}
			class="rounded-lg bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-700 disabled:opacity-40"
		>
			{busy ? 'Zpracovávám…' : 'Vložit položku'}
		</button>
	</form>

	{#if error}<p class="rounded bg-red-50 p-3 text-sm text-red-700">{error}</p>{/if}
	{#if result}<pre class="overflow-x-auto rounded bg-slate-900 p-3 text-xs text-slate-100">{result}</pre>{/if}
</div>
