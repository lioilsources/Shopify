# Dev databáze na JODĚ

Na Macu Docker neběží, proto má ChatShop dev Postgres (pgvector, pg17) na JODĚ,
stejně jako ostatní projekty: vlastní kontejner v `~/deploy/Shopify`, port jen
na LAN adrese JODY, heslo jen v `.env` na JODĚ a na Macu.

| co | hodnota |
|---|---|
| projekt compose | `shopify-dev` |
| databáze / uživatel | `chatshop_dev` / `chatshop` |
| port | 5436 (registr portů v DevConventions) |
| data | `~/deploy/Shopify/data/dev/db`, po založení datasetu `pool-shopify` |

## Nasazení (jednou)

1. Na JODĚ vytvořit `~/deploy/Shopify/init` a nakopírovat tam
   `infra/joda/docker-compose.db.yml` a `infra/init/01-extensions.sql` (do `init/`).
2. `~/deploy/Shopify/.env` s `POSTGRES_PASSWORD`, `DB_BIND` (LAN adresa JODY),
   `DB_PORT=5436`, `DB_DIR=./data/dev/db`.
3. `docker compose -p shopify-dev -f docker-compose.db.yml up -d`

## Napojení z Macu

V kořenovém `.env` (gitignorovaný):
`DATABASE_URL=postgresql+psycopg://chatshop:<heslo>@<JODA>:5436/chatshop_dev`

```
cd services/brain
.venv/bin/alembic upgrade head
.venv/bin/python -m brain.seed
.venv/bin/uvicorn brain.main:app --reload
```

Zastavovat jen službu `db` příkazem `stop`; mazání svazku s daty jen se
souhlasem vlastníka.
