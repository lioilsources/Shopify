# ChatShop → SlopMarket

<!-- Max 80 řádků. Co se nevejde, jde do docs/ a sem jeden odkaz. Veřejné repo: žádné LAN IP, domovské cesty, ID. -->

## Účel
ChatShop: e-shop s chatem nahoře (RAG, mění výběr) a galerií s filtry, které
rostou z ingestu. První ostrý katalog je **SlopMarket** (pracovně ImageMarket):
tržiště AI obrázků k tisku, viz `Prompts/02-PLAN-imagemarket.md`.

## Build a test
```
# brain (FastAPI)
cd services/brain && python -m venv .venv && .venv/bin/pip install -e '.[dev]'
.venv/bin/pytest -q
# web (SvelteKit)
cd apps/web && npm ci && npm run build && npx svelte-check@4 --threshold error
```
Gate před pushem: obojí výše zeleně. Testy brainu jsou bez DB; mock režim
end-to-end potřebuje Postgres (dev DB na JODĚ, na Macu Docker neběží).

## Mapa
- `apps/web` — SvelteKit PWA + BFF (chat, galerie, košík, admin ingestu)
- `services/brain` — FastAPI: chat SSE, RAG, ingest, filter schémata, alembic
- `infra/` — compose (lokální, NAS); `infra/spark` je zastaralé (mimo broker)
- `docs/` — rozhodnutí, rešerše fáze 0 (REUSE, GALLERY_API, LICENCES, …)
- `Prompts/` — plány; práce chodí jako „implementuj podle plánu“

## Invarianty
- Chat mění výběr v galerii; filtry vznikají z ingestu, nikdy natvrdo ve webu.
- Obchod funguje bez GPU: hledání, filtry, detail a poptávka bez LLM.
- Nic není veřejné bez schválení; výloha jen SFW ze session `showcase/`.
- Výtvory z nahraných fotek soukromé navždy; ve v1 bez lidí na fotkách (výjimka R14: vygenerované demo portréty).
- Klient (web, appka) nenese žádný token.
- Modely do prodeje jen podle `docs/LICENCES.md`.
- SPARK jen přes `sparkctl`; nic na SPARKu neinstaluj, chybějící model = otázka.
- Ceny se nevymýšlejí: náklad výrobce + marže vlastníka, jinak „na poptávku“.

## Odchylky
Žádné.

## Kam dál
- `docs/DECISIONS.md` — odpovědi vlastníka R1–R13
- `docs/REUSE.md` — co z ChatShopu zůstává a co chybí
- `Prompts/02-PLAN-imagemarket.md` §0 — stav fází (aktualizuj po každé fázi)
- `ARCHITECTURE.md`, `README.md`
