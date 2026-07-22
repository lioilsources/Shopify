# Plán dalších iterací

Stav po scaffoldu (2026-07-22): celá aplikace funguje lokálně v mock režimu —
web (SvelteKit PWA, chat + galerie s dynamickými filtry), brain (FastAPI, RAG
chat přes SSE, ingest s merge filter schémat), Postgres+pgvector se seed daty,
deployment konfigurace pro NAS i Spark připravené. Viz ARCHITECTURE.md.

## Iterace 1 — napojení Sparku (další krok)

1. Na Sparku: `docker compose -f infra/spark/docker-compose.llm.yml up -d`
   (vLLM s Qwen2.5-32B-AWQ na :8001, TEI s bge-m3 na :8002).
2. V `.env`: `LLM_BASE_URL=http://<spark>:8001/v1`,
   `EMBEDDINGS_BASE_URL=http://<spark>:8002`.
3. Přidat `python -m brain.seed --reembed` — přepočet embeddingů existujících
   produktů reálným modelem (mock hash-vektory jsou s bge-m3 nekompatibilní).
4. Ověřit: chat odpovídá modelem a doporučuje správné produkty; ingest bez
   ručních atributů extrahuje strukturované atributy z textu.

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
