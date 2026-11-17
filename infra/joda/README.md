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

## Aplikace (brain + web) na JODĚ

`docker-compose.app.yml`, projekt `shopify-app`: veřejně na https://slop.ol1n.com
přes vlastní tunel `slopmarket`, v LAN i na portu 8099. `/admin`, `/api/admin`
a `/api/ingest` jsou za Cloudflare Access (aplikace `slopmarket-admin`).

Nasazení jedním příkazem z Macu: `infra/joda/deploy.sh` (tunel a DNS založí
při prvním běhu na JODĚ). Ruční postup níže.

1. Synchronizace z Macu (z kořene repa):
   ```
   rsync -a --delete --exclude node_modules --exclude .svelte-kit --exclude build --exclude .venv --exclude __pycache__ \
     services/brain joda:deploy/Shopify/src/services/
   rsync -a --delete --exclude node_modules --exclude .svelte-kit --exclude build apps/web joda:deploy/Shopify/src/apps/
   rsync -a infra/joda/docker-compose.app.yml joda:deploy/Shopify/
   rsync -a run/media/ joda:deploy/Shopify/media/      # originály a cache náhledů
   ```
2. `~/deploy/Shopify/.env` doplnit o `ADMIN_TOKEN` (vygenerovat na JODĚ),
   `WEB_BIND` (LAN adresa JODY) a `WEB_PORT=8099`.
3. `docker compose -p shopify-app -f docker-compose.app.yml up -d --build`

Brain při startu sám spustí `alembic upgrade head`. Zastavovat jen `stop <služba>`.
