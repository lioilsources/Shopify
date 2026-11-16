<script lang="ts">
	import type { ChatMsg, ProductCard } from '$lib/types';

	let {
		category = null,
		onselect
	}: {
		/** Category selected in the gallery; scopes the chat search. */
		category?: string | null;
		/** Chat results become the gallery selection (ids in relevance order). */
		onselect: (ids: number[], query: string) => void;
	} = $props();

	let messages = $state<ChatMsg[]>([]);
	let input = $state('');
	let busy = $state(false);
	let scroller: HTMLDivElement;

	function scrollDown() {
		requestAnimationFrame(() => scroller?.scrollTo({ top: scroller.scrollHeight }));
	}

	async function send(e: SubmitEvent) {
		e.preventDefault();
		const question = input.trim();
		if (!question || busy) return;
		input = '';
		busy = true;
		messages.push({ role: 'user', content: question });
		messages.push({ role: 'assistant', content: '' });
		// mutovat je nutné proxy z pole, ne původní objekt — jinak se změny nevykreslí
		const assistant = messages[messages.length - 1];
		scrollDown();

		try {
			const res = await fetch('/api/chat', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					messages: messages
						.slice(0, -1)
						.map(({ role, content }) => ({ role, content })),
					category
				})
			});
			if (!res.ok || !res.body) throw new Error(`Chat selhal (${res.status})`);

			const reader = res.body.pipeThrough(new TextDecoderStream()).getReader();
			let buffer = '';
			for (;;) {
				const { done, value } = await reader.read();
				if (done) break;
				buffer += value;
				let sep;
				while ((sep = buffer.indexOf('\n\n')) !== -1) {
					const block = buffer.slice(0, sep);
					buffer = buffer.slice(sep + 2);
					const event = /^event: (.+)$/m.exec(block)?.[1];
					const dataRaw = /^data: (.+)$/m.exec(block)?.[1];
					if (!event || !dataRaw) continue;
					const data = JSON.parse(dataRaw);
					if (event === 'token') assistant.content += data.text;
					else if (event === 'products') {
						assistant.products = data as ProductCard[];
						onselect(assistant.products.map((p) => p.id), question);
					}
					scrollDown();
				}
			}
		} catch (err) {
			assistant.content ||= `Nepodařilo se spojit s asistentem: ${err}`;
		} finally {
			busy = false;
			scrollDown();
		}
	}
</script>

<div class="flex h-full flex-col">
	<div bind:this={scroller} class="flex-1 space-y-3 overflow-y-auto px-4 py-3">
		{#if messages.length === 0}
			<p class="text-sm text-slate-400">
				Zeptejte se na cokoliv ze sortimentu — např. „hledám boty na běhání do 3000 Kč".
			</p>
		{/if}
		{#each messages as msg}
			<div class={msg.role === 'user' ? 'text-right' : 'text-left'}>
				<span
					class={'inline-block max-w-[80%] rounded-2xl px-3 py-2 text-sm whitespace-pre-wrap ' +
						(msg.role === 'user' ? 'bg-sky-600 text-white' : 'bg-slate-100 text-slate-900')}
				>
					{msg.content || (busy ? '…' : '')}
				</span>
				{#if msg.role === 'assistant' && msg.products}
					<p class="mt-1 text-xs text-slate-400">
						{msg.products.length
							? `Výběr v galerii: ${msg.products.length} ${msg.products.length === 1 ? 'položka' : msg.products.length < 5 ? 'položky' : 'položek'}`
							: 'Nic nenalezeno, galerie zůstala beze změny.'}
					</p>
				{/if}
			</div>
		{/each}
	</div>
	<form onsubmit={send} class="flex gap-2 border-t border-slate-200 p-3">
		<input
			bind:value={input}
			disabled={busy}
			placeholder="Napište, co hledáte…"
			class="flex-1 rounded-full border border-slate-300 px-4 py-2 text-sm focus:border-sky-500 focus:outline-none"
		/>
		<button
			type="submit"
			disabled={busy || !input.trim()}
			class="rounded-full bg-sky-600 px-5 py-2 text-sm font-medium text-white hover:bg-sky-700 disabled:opacity-40"
		>
			Odeslat
		</button>
	</form>
</div>
