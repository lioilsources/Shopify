# Co z ChatShopu přebírá ImageMarket

Fáze 0, krok 2 plánu [02-PLAN-imagemarket.md](../Prompts/02-PLAN-imagemarket.md).
Sepsáno 16. 11. 2026 z kódu (ne z README). Odkazy jsou `soubor:řádek`.

## Ověření tabulky „Základ: ChatShop“ (§2)

| tvrzení plánu | skutečnost v kódu | verdikt |
|---|---|---|
| chat = vyhledávací pole, událost `products` mění galerii | Brain posílá `products` jako první událost, pak `token` a `done` (`services/brain/brain/chat.py:76-90`). Web ale karty kreslí **jen do bubliny chatu** (`apps/web/src/lib/components/Chat.svelte:53`, `:81-97`). Galerie (`apps/web/src/routes/+page.svelte:11`, `:25-32`) o chatu neví a filtry se nemění. | **neplatí**, propojení chat → galerie se musí dopsat |
| RAG | Jen vektorové hledání: kosinová vzdálenost nad `product_embeddings`, top 5 (`rag.py:10-19`). Chat neví o kategorii ani filtrech, fulltext nemá. | platí, ale slabé |
| filtry rostou z katalogu, `filter_schemas` text/range/set/bool per kategorie, atributy v JSONB | `filters.py:22-31` odvozuje druh, `:62-96` zakládá a rozšiřuje schéma. JSONB a GIN index jsou v `models.py:45,53`. SQL nad filtry je v BFF `apps/web/src/routes/api/products/+server.ts:28-50`. Sidebar je `Filters.svelte`. | platí |
| filtry per kategorie vedle společných | Schéma je vždy vázané na `category_id` (`models.py:32`). Společné filtry nejsou, bez vybrané kategorie se filtry nezobrazí (`+page.svelte:70-74`). Schéma jen roste, hodnoty se nemažou (`filters.py:50-59`). | **částečně**, společné filtry chybí |
| ingest: dohledání → extrakce LLM → sloučení schématu → embedding | `ingest.py:66-100` přesně v tomto pořadí. Dohledání je stub `return req.raw_text or req.name` (`ingest.py:44-46`). | platí, místo pro adaptér obrázku je `_lookup` |
| režim bez LLM: stejné rozhraní, odpověď ze šablony a z hledání | Přepínač je prázdné `LLM_BASE_URL` / `EMBEDDINGS_BASE_URL` (`config.py:25-31`). Odpověď ze šablony je v `chat.py:59-66`. „Hledání“ ale je hashový pseudo-embedding (`embeddings.py:18-38`), ne fulltext. Ingest bez LLM bere jen ruční atributy (`ingest.py:50-51`). | platí, ale „hledání“ v mocku je slabé |
| bez SPARKu funguje i se zapnutými embeddingy | Ne. `embed()` při zapnutých embeddingech volá gateway bez fallbacku (`embeddings.py:41-51`), takže když SPARK neběží, `/chat` i `/ingest` spadnou s 500. | **chybí** (R12) |
| SvelteKit PWA + BFF | SvelteKit 2, Svelte 5, adapter-node (`svelte.config.js:1`). BFF v `routes/api/*`: produkty a kategorie čtou DB přímo přes postgres.js (`lib/server/db.ts`), chat a ingest jdou jako proxy na brain. SW kešuje jen statiku (`service-worker.ts:22-27`), manifest má ikonu jen SVG. | platí |
| galerie s velkými obrázky | Mřížka čtvercových karet `aspect-square object-cover` (`ProductCard.svelte:9`). Detail, stránkování ani lazy-loading nejsou (`api/products/+server.ts:56-63` vrací vše). | **neplatí**, ořez na čtverec obrázkům škodí |
| košík v `localStorage` | `cart.svelte.ts:9-46`, položka = produkt × počet a cena `price_czk`. | platí, ale model položky se pro obrázky nehodí |
| admin ingestu | `routes/admin/ingest/+page.svelte` je formulář na jednu položku. Bez autentizace: `/api/ingest` je otevřená proxy (`api/ingest/+server.ts`). | platí, admin je nechráněný |
| AiStack: LLM `shop`, embeddingy `shop-embed` (bge-m3) za gateway | Názvy jsou jen v `.env.example:10,18`. Výchozí hodnoty v kódu jsou staré HF jména (`config.py:18,22`), stejně v `infra/nas/docker-compose.prod.yml:39,42`. `llm_api_key` se posílá jen klientovi OpenAI (`llm.py:13`). Embeddingy jdou přes `httpx` **bez hlavičky Authorization** (`embeddings.py:44-49`). | platí, ale auth k embeddingům chybí |

## Zůstává beze změny

- `filters.py` celý: odvození druhu, rozšiřování schématu. Má testy.
- SSE protokol `products`/`token`/`done` (`chat.py:1-7`) a parser v `Chat.svelte:38-56`.
- Kostra brainu: FastAPI, SQLAlchemy 2, Alembic, pydantic-settings, `.env` z kořene repa (`config.py:5-13`).
- BFF překlad filtrů na SQL nad JSONB (`api/products/+server.ts`), zatím bez stránkování.
- Mock embedding pro testy a vývoj (`embeddings.py:29-38`).
- Rozvržení `apps/web`, `services/brain`, `infra/`.

## Mění se kvůli obrázkům

- **`_lookup` → adaptér galerie** (`ingest.py:44-46`): řádek z galerie, zadání showcase, popis od VLM. Přesné hodnoty ze zadání mají přednost před LLM. Dnes je to obráceně: ruční atributy přebijí extrahované (`ingest.py:74`).
- **`EXTRACT_PROMPT`** (`ingest.py:25-30`) je psaný pro zboží (velikost, kapacita). Pro obrázky potřebuje schéma tématu.
- **`SYSTEM_PROMPT`** (`chat.py:25-30`) tlačí název a cenu. U obrázku se cena určuje podle provedení, takže kontext chatu musí obsahovat tiskové profily.
- **`price_czk` je povinné všude**: model (`models.py:51`), migrace (`0001_initial.py:50`), `IngestRequest` (`ingest.py:36`), filtr ceny (`filters.py:18-19,70-71`), karty a košík. Pro obrázky musí být volitelné, cena patří k variantě.
- **Ingest není idempotentní**: každé volání založí nový produkt (`ingest.py:76-85`). Plán chce idempotenci podle sha256.
- **Galerie**: zachovat poměr stran, přidat detail a SSR stránky katalogu. Dnešní `+page.ts` je universal load přes `/api`, SSR tedy běží, ale nic se nekešuje.
- **Košík**: položka (obrázek nebo výtvor) × varianta × rozměr místo `product × qty`.
- **Popisky filtrů** se generují z klíče (`filters.py:84`), bez cs/en.
- **Embedding nenese jméno modelu**. Smíchat mock a reálné vektory jde potichu, jediná pojistka je ruční `seed --reembed` (`seed.py:112-123`).
- Rozměr vektoru je zadrátovaný v migraci (`0001_initial.py:18`), nezávisle na `EMBEDDING_DIM`.

## Chybí úplně

- Propojení chat → galerie (výsledky chatu nastaví výběr nebo filtry). Chat nezná vybranou kategorii ani filtry.
- Fulltext (`tsvector`) a hybridní hledání. Cesta embeddingu dotazu bez SPARKu.
- Stav produktu `draft/listed/hidden` a brána zveřejnění. Dnes `/api/products` vrací všechno.
- Autentizace adminu a ingestu, účty, objednávky, platby, fronta jobů, S3.
- Testy nad DB a nad API (oba testové soubory jsou čistě jednotkové), lint, CI.
- Skript `check` ve webu (svelte-check není v závislostech).
- Detail produktu, stránkování, i18n.

## Zastaralé v infrastruktuře

- **Caddy na 80/443 s vlastním TLS** (`infra/nas/docker-compose.prod.yml:9-20`, `infra/nas/Caddyfile:1-5`, placeholder doména). Nahradit tunelem a Caddy bez portů na hostu (§5).
- **Databáze v compose**: lokální `infra/docker-compose.yml` a služba `db` v prod compose (`docker-compose.prod.yml:48-62`). Obojí s výchozím heslem `chatshop` a s publikovaným portem 5432 (`infra/docker-compose.yml:10-11`). Podle plánu má být Postgres na JODĚ a porty podle registru.
- **Fallback heslo v connection stringu** (`config.py:15`, `apps/web/src/lib/server/db.ts:5`, prod compose `${POSTGRES_PASSWORD:-chatshop}`). V produkci má chybějící heslo shodit start.
- **`infra/spark/docker-compose.llm.yml`**: vlastní vLLM a TEI na SPARKu, obrazy `:latest`, `restart: unless-stopped`. Odporuje pravidlu „jen přes broker a gateway“. Plán 01 ho sám označuje za záložní, smazat.
- **CORS** jen pro `localhost:5173/4173` (`main.py:9-14`). Pro BFF to nevadí, appka bude potřebovat jinou cestu.
- Výchozí jména modelů v kódu a compose (viz tabulka) neodpovídají aliasům gateway.
- `Dockerfile` brainu pouští `alembic upgrade head` při každém startu (`services/brain/Dockerfile:10`). Při více replikách je to riziko.
- README a ARCHITECTURE popisují NAS + Caddy + lokální compose. Až se změní infra, aktualizovat je.

## Úniky do veřejného repa

- **Natvrdo zapsaná LAN adresa gateway SPARKu** v `.env.example:6,9,17` a v `Prompts/01-PLAN-next-iterations.md:19`. Nahradit placeholderem (`SPARK_HOST`). Adresa už je v historii gitu.
- Veřejná doména gateway v `.env.example:6`. Zvážit, jestli ji v repu chceme.
- V kódu (`apps/`, `services/`, `infra/`) žádné IP, domovské cesty, e-maily ani tokeny nejsou.

## Spuštění bez Dockeru (ověřeno 16. 11. 2026)

- Brain: `python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'` v `services/brain` (Python 3.14, projde). `uvicorn brain.main:app` naběhne a `/health` vrátí `{"llm":"mock","embeddings":"mock"}`. **`/chat` vrací 500**, protože na Macu neběží Postgres na `localhost:5432` (Docker neběží, Postgres není nainstalovaný). Mock režim tedy bez DB nejede. Potřebuje dev databázi na JODĚ (pgvector, dataset zakládá vlastník) a pak `alembic upgrade head && python -m brain.seed`.
- Web: `npm ci && npm run build` projde (adapter-node). `npx svelte-check@4` hlásí 0 chyb a 1 varování: `state_referenced_locally` v `+page.svelte:11`.

## Gate (do CLAUDE.md)

```
cd services/brain && .venv/bin/pytest -q          # 7 passed
cd apps/web && npm ci && npm run build && npx svelte-check@4 --threshold error
```

Doporučení: přidat do `package.json` skript `"check": "svelte-kit sync && svelte-check"` a `svelte-check` do devDependencies. Gate pak bude `npm run check && npm run build`.
