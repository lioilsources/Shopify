<script lang="ts">
	import type { ActiveFilters, FilterSchema } from '$lib/types';

	let {
		schemas,
		active = $bindable()
	}: { schemas: FilterSchema[]; active: ActiveFilters } = $props();

	function toggleSetValue(key: string, value: string) {
		const current = (active[key] as string[] | undefined) ?? [];
		const next = current.includes(value)
			? current.filter((v) => v !== value)
			: [...current, value];
		if (next.length === 0) delete active[key];
		else active[key] = next;
	}

	function setRange(key: string, bound: 'min' | 'max', raw: string) {
		const current = { ...((active[key] as { min?: number; max?: number }) ?? {}) };
		if (raw === '') delete current[bound];
		else current[bound] = Number(raw);
		if (current.min == null && current.max == null) delete active[key];
		else active[key] = current;
	}
</script>

<div class="space-y-5">
	{#each schemas as schema (schema.attr_key)}
		<fieldset>
			<legend class="mb-1.5 text-sm font-semibold text-slate-700">{schema.label}</legend>

			{#if schema.kind === 'set'}
				<div class="flex flex-wrap gap-1.5">
					{#each schema.config.values ?? [] as value}
						{@const selected = ((active[schema.attr_key] as string[]) ?? []).includes(value)}
						<button
							type="button"
							onclick={() => toggleSetValue(schema.attr_key, value)}
							class={'rounded-full border px-2.5 py-0.5 text-xs ' +
								(selected
									? 'border-sky-600 bg-sky-600 text-white'
									: 'border-slate-300 bg-white text-slate-700 hover:border-sky-400')}
						>
							{value}
						</button>
					{/each}
				</div>
			{:else if schema.kind === 'range'}
				<div class="flex items-center gap-2 text-sm">
					<input
						type="number"
						placeholder={String(schema.config.min ?? '')}
						onchange={(e) => setRange(schema.attr_key, 'min', e.currentTarget.value)}
						class="w-24 rounded border border-slate-300 px-2 py-1 text-sm"
					/>
					<span class="text-slate-400">–</span>
					<input
						type="number"
						placeholder={String(schema.config.max ?? '')}
						onchange={(e) => setRange(schema.attr_key, 'max', e.currentTarget.value)}
						class="w-24 rounded border border-slate-300 px-2 py-1 text-sm"
					/>
					{#if schema.config.unit}<span class="text-xs text-slate-500">{schema.config.unit}</span>{/if}
				</div>
			{:else if schema.kind === 'bool'}
				<label class="flex items-center gap-2 text-sm text-slate-700">
					<input
						type="checkbox"
						checked={active[schema.attr_key] === true}
						onchange={(e) => {
							if (e.currentTarget.checked) active[schema.attr_key] = true;
							else delete active[schema.attr_key];
						}}
					/>
					Ano
				</label>
			{:else}
				<input
					type="search"
					placeholder="Hledat…"
					value={(active[schema.attr_key] as string) ?? ''}
					onchange={(e) => {
						const v = e.currentTarget.value.trim();
						if (v) active[schema.attr_key] = v;
						else delete active[schema.attr_key];
					}}
					class="w-full rounded border border-slate-300 px-2 py-1 text-sm"
				/>
			{/if}
		</fieldset>
	{/each}
</div>
