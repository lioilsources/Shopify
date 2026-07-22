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
