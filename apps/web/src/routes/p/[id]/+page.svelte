<script lang="ts">
	import type { FitnessGrade } from '$lib/types';

	let { data } = $props();
	const product = $derived(data.product);

	const GRADE: Record<FitnessGrade, { icon: string; label: string; cls: string }> = {
		ok: { icon: '✅', label: 'jde hned', cls: 'text-emerald-700' },
		upscale: { icon: '⬆', label: 'po zvětšení', cls: 'text-sky-700' },
		caveat: { icon: '⚠', label: 's výhradou', cls: 'text-amber-700' },
		no: { icon: '✖', label: 'nehodí se', cls: 'text-slate-400' }
	};

	// Public attributes worth showing; the "suits" list is the table below.
	const LABELS: Record<string, string> = {
		styl: 'Styl',
		namet: 'Námět',
		orientace: 'Orientace',
		pomer_stran: 'Poměr stran'
	};
	const facts = $derived(
		Object.entries(LABELS)
			.filter(([k]) => product.attributes[k] != null)
			.map(([k, label]) => [label, String(product.attributes[k])])
	);
	const offered = $derived(data.fitness.filter((f) => f.grade !== 'no'));
	const notOffered = $derived(data.fitness.filter((f) => f.grade === 'no'));

	const cm = (v: [number, number]) => `${Math.round(v[0])} × ${Math.round(v[1])} cm`;
</script>

<svelte:head>
	<title>{product.name} · SlopMarket</title>
	<meta name="description" content={product.description || product.name} />
</svelte:head>

<div class="h-full overflow-y-auto">
	<div class="mx-auto grid max-w-6xl gap-8 p-4 sm:p-6 lg:grid-cols-[3fr_2fr]">
		<div class="space-y-2">
			<img src={product.image_url} alt={product.name} class="w-full rounded-xl bg-slate-100 object-contain" />
			<p class="text-xs text-slate-500">
				Obrázek vytvořila umělá inteligence. Náhled je zmenšený a s vodoznakem; tisková data jsou bez něj.
			</p>
		</div>

		<div class="space-y-6">
			<div>
				<a href={`/?category=${product.category_slug}`} class="text-sm text-sky-700 hover:underline">
					{product.category_name}
				</a>
				<h1 class="mt-1 text-2xl font-bold leading-tight">{product.name}</h1>
				{#if product.description && product.description !== product.name}
					<p class="mt-2 text-slate-600">{product.description}</p>
				{/if}
			</div>

			{#if facts.length}
				<dl class="grid grid-cols-2 gap-x-4 gap-y-1 text-sm">
					{#each facts as [label, value] (label)}
						<dt class="text-slate-500">{label}</dt>
						<dd>{value}</dd>
					{/each}
				</dl>
			{/if}

			<section>
				<h2 class="mb-2 font-semibold">Na co se hodí</h2>
				{#if !data.fitness.length}
					<p class="text-sm text-slate-500">Vhodnost se zatím nepodařilo načíst.</p>
				{:else}
					<table class="w-full text-sm">
						<tbody>
							{#each offered as f (f.profile_id)}
								<tr class="border-t border-slate-100">
									<td class="py-1.5 pr-2">{f.label_cs}</td>
									<td class={'py-1.5 pr-2 whitespace-nowrap ' + GRADE[f.grade].cls}>
										{GRADE[f.grade].icon} {GRADE[f.grade].label}
									</td>
									<td class="py-1.5 text-right whitespace-nowrap text-slate-600">
										{f.max_cm ? `až ${cm(f.max_cm)}` : ''}
									</td>
								</tr>
								{#if f.note}
									<tr><td colspan="3" class="pb-1.5 text-xs text-slate-400">{f.note}</td></tr>
								{/if}
							{/each}
						</tbody>
					</table>
					{#if notOffered.length}
						<p class="mt-2 text-xs text-slate-400">
							Nehodí se: {notOffered.map((f) => f.label_cs).join(', ')}.
						</p>
					{/if}
				{/if}
			</section>

			<div class="rounded-xl bg-slate-50 p-4 text-sm">
				<p class="font-medium">Chci tohle na…</p>
				<p class="mt-1 text-slate-500">
					Poptávka přijde v dalším kroku. Cena se počítá podle provedení a rozměru.
				</p>
			</div>
		</div>
	</div>
</div>
