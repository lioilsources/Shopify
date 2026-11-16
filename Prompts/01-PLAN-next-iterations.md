# Plán dalších iterací

Stav po scaffoldu (2026-07-22): celá aplikace funguje lokálně v mock režimu —
web (SvelteKit PWA, chat + galerie s dynamickými filtry), brain (FastAPI, RAG
chat přes SSE, ingest s merge filter schémat), Postgres+pgvector se seed daty,
deployment konfigurace pro NAS i Spark připravené. Viz ARCHITECTURE.md.

## Iterace 1 — napojení Sparku (HOTOVO 2026-07-22)

Realizováno jinak než původní návrh: Spark už má AiStack (LiteLLM gateway
:8080), takže místo samostatného `infra/spark/docker-compose.llm.yml` vznikl
**Shopify modul přímo v AiStacku** (`deploy/docker-compose.shopify.yaml`):

- `shop` — nvidia/Qwen3-32B-FP4 přes vLLM (port 8015), sdílí HF cache
  s translate; `make up-shopify`.
- `shop-embed` — BAAI/bge-m3, vLLM `--runner pooling` (port 8016);
  `make download-shop-embed`.
- LiteLLM routy `shop` + `shop-embed`, fallback řetězec `shop -> fallback`.
- Brain volá gateway: `LLM_BASE_URL=http://<SPARK_HOST>:8080/v1`
  (chat i embeddings přes jeden endpoint, routing podle `model`).
- `python -m brain.seed --reembed` přepočítá embeddingy po přechodu z mocku.
- Pozn.: `infra/spark/docker-compose.llm.yml` v tomto repu je tím pádem
  jen záložní varianta pro nasazení bez AiStacku.

## Iterace 2 — reálný web lookup v ingest pipeline

- Nasadit SearXNG (kontejner na Sparku nebo NAS), v brainu nahradit
  `_lookup()` stub: dotaz podle názvu/EAN → stažení top výsledků → text pro
  LLM extrakci. Poslední nehotová část původního zadání
  (00-PLAN-manual.md, bod „pipeline na vkládání zboží").
- Admin UI: náhled dohledaných zdrojů + schválení extrahovaných atributů
  před uložením.

## Iterace 3 — deploy na NAS

- Doména → Caddyfile, `.env` na NAS (heslo DB, adresy Sparku),
  `docker compose -f infra/nas/docker-compose.prod.yml up -d --build`.
- Ověřit HTTPS, instalaci PWA na mobilu, chat proti Sparku přes LAN/VPN.

## Iterace 4+ — obchodní funkce

- Objednávky (checkout bez plateb → později platební brána).
- Autentizace zákazníků, historie objednávek.
- Admin: správa produktů (editace, mazání), schvalovací workflow ingestu.
- Vylepšení RAG: hybridní vyhledávání (fulltext + vektory), rerank,
  filtrování doporučení podle skladovosti.
