# ChatShop — ChatBot-like e-shop

E-shop, kde horních ~20 % obrazovky tvoří chat s LLM (RAG nad položkami shopu,
doporučování relevantních produktů) a dolních ~80 % klasická galerie
s dynamickými filtry podle typu zboží. Součástí je ingest pipeline, která při
vložení položky dohledá informace z webu a odvodí z nich sadu filtrů.

Architektura, datový model a deployment: viz [ARCHITECTURE.md](ARCHITECTURE.md).

## Struktura

```
apps/web        SvelteKit PWA — chat + galerie + admin ingest
services/brain  Python FastAPI — RAG chat, ingest pipeline
infra/          docker-compose (Postgres+pgvector; LLM stack pro DGX Spark)
Prompts/        původní zadání
```

## Rychlý start (dev na Macu)

```bash
# 1. Databáze
cd infra && docker compose up -d

# 2. Brain (FastAPI)
cd services/brain
python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'
.venv/bin/alembic upgrade head
.venv/bin/python -m brain.seed          # demo data (trička, boty, HDD)
.venv/bin/uvicorn brain.main:app --reload --port 8000

# 3. Web (SvelteKit)
cd apps/web
npm install
npm run dev                              # http://localhost:5173
```

Bez nastaveného `LLM_BASE_URL` běží chat v **mock režimu** (odpovídá bez LLM,
produkty doporučuje čistě přes fulltext/vektorové vyhledávání). Pro reálný chat
nastav v `.env` endpoint vLLM na DGX Spark — viz `.env.example` a
[ARCHITECTURE.md](ARCHITECTURE.md#llm-stack-na-dgx-spark).

---

## Investor pitch (English)

**In one sentence:** an e-shop whose top 20 % of the screen is a chat assistant
and whose bottom 80 % is a gallery with filters that generate themselves from
whatever is being sold.

### Problem

Two problems that belong together. Shoppers can't describe what they want in the
language of filters ("under 5,000, for trail running, not too heavy") — and the
shop hands them checkboxes. And the shop operator has to invent and maintain a
set of attributes and filters by hand for every new category; that is why small
shops filter by price and brand and nothing else.

### Solution

A chat-first interface over RAG search across the catalogue (PostgreSQL +
pgvector). The assistant answers and **at the same time changes the selection in
the gallery below it** — the chat isn't a widget beside the product, it *is* the
search field. The other half is an **ingest pipeline**: when an item is added,
the system looks it up on the web, an LLM derives attributes from what it finds
and generates the filter schema for that category. Filters emerge from the
catalogue, not from an administrator's spreadsheet.

### Why it can win

- **The automatic filter is the harder and more valuable half.** Everyone ships
  a conversational widget these days; nobody addresses the fact that the
  catalogue holds no structured data for the chat to lean on. ChatShop solves
  both with one model.
- **Unit economics.** Chat in every session means a per-visit cost on a
  commercial API. On our own DGX Spark (Qwen3-32B-FP4 for chat, BGE-M3 for
  embeddings) it is a fixed hardware cost that does not scale with traffic.
- **Data never leaves the customer's machine.** The application layer
  (SvelteKit PWA + FastAPI + pgvector) runs on a NAS behind Caddy with TLS; the
  GPU layer sits elsewhere and is not exposed to the internet. An argument for
  anyone unwilling to send their price list to someone else's API.

### Status

Scaffold and first iteration, July 2026. The data model, streaming RAG chat,
ingest pipeline and the connection to the production LLM gateway on Spark are in
place. Without `LLM_BASE_URL` set, the chat runs in mock mode. There is no
payment gateway, no order flow and no real catalogue — this is a working core,
not a turnkey shop.

### Next milestones

Orders and payments, a pilot catalogue from a real merchant, and measuring
conversion against a conventional filtered gallery. That last one is the only
number this product stands or falls on.

---

## Investor pitch (česky)

**Jednou větou:** e-shop, jehož horních 20 % obrazovky je chat s asistentem
a spodních 80 % galerie, jejíž filtry se generují samy z toho, co se prodává.

### Problém

Dva problémy, které spolu souvisí. Zákazník neumí popsat, co chce, jazykem
filtrů („do 5000, na běh po lese, ne moc těžké") — a e-shop mu nabízí
zaškrtávátka. A provozovatel e-shopu musí pro každou novou kategorii ručně
vymyslet a udržovat sadu atributů a filtrů; proto malé e-shopy filtrují podle
ceny a značky a nic víc.

### Řešení

Chat-first rozhraní nad RAG vyhledáváním v katalogu (PostgreSQL + pgvector).
Asistent odpovídá a **zároveň mění výběr v galerii pod sebou** — chat není
widget vedle produktu, je to vyhledávací pole. Druhá půlka je **ingest
pipeline**: při vložení položky si systém dohledá informace z webu, LLM z nich
odvodí atributy a vygeneruje schéma filtrů pro danou kategorii. Filtry tedy
vznikají z katalogu, ne z ručníku administrátora.

### Proč to může vyhrát

- **Automatický filtr je ta těžší a cennější polovina.** Konverzační widget
  dnes nabízí kdekdo; nikdo neřeší, že katalog nemá strukturovaná data, o která
  by se chat mohl opřít. ChatShop řeší obojí jedním modelem.
- **Jednotková ekonomika.** Chat v každé session znamená u komerčního API
  náklad na každou návštěvu. Na vlastním DGX Sparku (Qwen3-32B-FP4 pro chat,
  BGE-M3 pro embeddingy) je to fixní náklad na železo, který neroste s
  návštěvností.
- **Data neopouštějí zákazníkův stroj.** Aplikační vrstva (SvelteKit PWA +
  FastAPI + pgvector) běží na NAS za Caddy s TLS; GPU vrstva je jinde a není
  vystavená do internetu. Argument pro každého, kdo nechce posílat ceníky
  do cizího API.

### Stav

Scaffold a první iterace, červenec 2026. Stojí datový model, RAG chat se
streamingem, ingest pipeline a propojení na produkční LLM gateway na Sparku.
Bez nastaveného `LLM_BASE_URL` běží chat v mock režimu. Není tam platební brána,
objednávkový tok ani reálný katalog — je to funkční jádro, ne e-shop na klíč.

### Nejbližší milníky

Objednávky a platby, pilotní katalog reálného prodejce a měření konverze proti
klasické filtrované galerii. To poslední je jediné číslo, na kterém tenhle
produkt stojí nebo padá.
