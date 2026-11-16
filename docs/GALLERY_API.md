# API galerie FineTuneGallery pro ingest ImageMarketu

Stav kódu `FineTuneGallery` k 16. 11. 2026 (commit `80fa57e`), citace `soubor:řádek`
od kořene toho repa. K plánu `Prompts/02-PLAN-imagemarket.md` (§2, §6). Go + SQLite,
veřejný hostname `finetune.ol1n.com` za Cloudflare Access.

## 1. Přístup a auth

- Server sám uživatele neověřuje. Před ním stojí CF Access se dvěma policy:
  service token appky a SSO vlastníka (`README.md:44-51`).
- Jediná auth v kódu: `workerAuth` (`server/calibration.go:74`) nad celým muxem (`server/main.go:171`).
  - `Authorization: Bearer <WORKER_TOKEN>` otevře jen `POST /api/taxonomy/import`
    a `PUT /api/taxonomy/thresholds` (`server/calibration.go:27-30`), jinde 403.
  - Access service tokeny ve `WORKER_ACCESS_CLIENT_IDS` drží na těch dvou route
    (`server/calibration.go:76-79`); Client ID z claimu `common_name`
    v `Cf-Access-Jwt-Assertion`, bez ověření podpisu (`server/calibration.go:52`).
- Jiný token, který projde Access, smí číst i zapisovat, včetně `PUT …/rating`
  a `DELETE /api/sessions/{id}` (`server/main.go:120-130`). Role „jen čtení“ chybí.

## 2. Endpointy, které ingest použije

| endpoint | co vrací | kód |
|---|---|---|
| `GET /api/images` | `{"items":[…],"nextCursor"}`, `limit` 1–200 (výchozí 60), keyset kurzor přes `(created_at, id)`, řazeno od nejnovějšího | `server/gallery.go:208-281` |
| `GET /api/images/{id}` | detail: `image` (+ `width`, `height`), `node` (seed, sampler, steps, cfg…), `captions`, `parentChain` | `server/gallery.go:348-581` |
| `GET /img/{sha256}` | originální PNG, `?download=1&name=` jako příloha | `server/imgutil.go:22-38` |
| `GET /thumb/{sha256}` | JPEG s delší stranou 384 px, generovaný líně | `server/imgutil.go:16`, `:69-90` |
| `GET /api/images/{id}/similar?limit=24` | `{"items":[{id,sha256,score}]}`, kosinus nad SigLIP | `server/taxonomy.go:1160-1203` |
| `GET /api/images/{id}/taxonomy` | odpovědi hodnotitelů a lidské labely | `server/taxonomy.go:734` |
| `GET /api/sessions` | `[{id,title,modelId,lastIngestedAt,imageCount}]`, bez filtrů | `server/gallery.go:775-805` |
| `GET /api/stats` | součty a hodnocení, pásma neobsahuje | `server/gallery.go:880-930` |

Položka seznamu (`galleryItem`, `server/gallery.go:17-42`): `id`, `sha256`,
`sessionId`, `prompt`, `promptSent`, `modelId`, `loraName`, `styleId`,
`mediumId`, `seed`, `score`, `aspects`, `caption` (jen příznaky druhů),
`isImg2img` (= `parent_id IS NOT NULL`), `origin` a s taxonomií také `taxo`
(`temperature`, `band`, `unsure`; `server/taxonomy.go:901-929`).

## 3. Filtry `/api/images`

Všechny sdílí `galleryFilter` (`server/gallery.go:46-205`), stejně jako Eval a datasety.

- Metadata: `model`, `session` (jen přesná shoda `session_id`,
  `server/gallery.go:59-62`), `style`, `medium` (`none` = bez média),
  `translator`, `lora`, `lora_strength`, `pose`, `aspect`, `score=-1|0|1`,
  `unrated`, `has_critique`, `captioned=0|1`, `from`, `to` (`created_at`).
- Hodnocení: `criterion=<jméno>:1|-1|none`, `judge=<kritérium>:disagree|unrated`
  (`server/gallery.go:136-188`).
- Styl a prompt: `epoch`, `artist`, `technique` (`server/stylefacets.go:112`),
  `prompt=` slova jako podřetězce v `prompt` i `prompt_sent`, nejvýš 200 B
  (`server/stylefacets.go:137`).
- Taxonomie (`server/taxonomy.go:378-478`): `taxo=uzel:hodnota[,…]`,
  `taxo_src`, `temp_max`, `band=safe[,suggestive]`, `rating_unsure=0|1`,
  `taxo_unsure`, `label_queue=1`, `view=shared|private`.
  Bez `FINETUNE_TAXONOMY=1` vrátí kterýkoli z nich 400 (`server/taxonomy.go:399-401`).

## 4. Obsah: pásma, `view=shared`, blok nezletilých

- Teplota 0–1, pásma `safe | suggestive | nsfw | explicit` (`server/taxonomy.go:131-141`),
  uložená v `image_temperature.band` s `unsure` (`server/db.go:180-190`). Prahy jsou
  v `temperature_bands`, jinak výchozí z YAML (`server/taxonomy.go:150-165`); conformal
  guard posílá hraniční případy do `unsure` (`server/taxonomy.go:145`).
- `view=shared` přidá podmínku `band = 'safe' AND unsure = 0`. Neohodnocené
  obrázky tím vypadnou (`server/taxonomy.go:468-476`). `FINETUNE_PUBLIC_VIEW=1`
  ji vynutí na všech seznamech i blobech (`server/imgutil.go:101-105`,
  `server/taxonomy.go:369-375`) a bez taxonomie server nenastartuje
  (`server/main.go:63-67`).
- Blok nezletilých platí vždy, bez flagu. `minorDecision`
  (`server/taxonomy.go:190-233`) dává `quarantine` nebo `block`, výsledek jde
  do `taxonomy_blocks` (`server/db.go:211`). View `gallery` vyřadí každý
  obrázek se stejným sha256 (`server/db.go:242-257`) a blob vrací 451
  (`server/imgutil.go:95-100`). Hodnoty `child` a `teen` nejdou použít jako
  filtr (`server/taxonomy.go:415-420`). Kontrola běží po každém WD14 captionu
  (`server/captioner.go:167-170`) a při startu (`server/main.go:106-110`).
- Mezera: detail, `…/taxonomy` a `/api/sessions` čtou `gallery` bez podmínky safe
  (`server/gallery.go:352-360`, `server/taxonomy.go:741`), takže i ve veřejném režimu
  vydají metadata neschválených obrázků (bloby ne). `similar` filtruje safe jen
  s `view=shared` nebo ve veřejném režimu (`server/taxonomy.go:1189`).

## 5. Tagy, popisky, embeddingy

- `captions`: vrstvy `auto` (WD14), `human`, `refined`; efektivní human > refined > auto
  (`server/schema.sql:98-108`). Text `auto` = tagy postav, pak obecné podle confidence;
  rating tagy jen v `tags_json` (`server/captioner.go:151-158`). Detail vrací `text`
  a `tagger`, `tags_json` s confidence ne (`server/gallery.go:496-519`).
- SigLIP 2 (`google/siglip2-so400m-patch16-512`, 1152 dim) leží
  v `image_embeddings` jako L2-normovaný float32 BLOB (`server/db.go:192-198`).
  Přichází jen importem z GPU dávky (`server/taxonomy.go:559-563`, `:712-719`), pro
  `similar` se drží v paměti, jen vektory nejčastějšího modelu
  (`server/taxonomy_embed.go:10-60`). Endpoint se samotným vektorem neexistuje.

## 6. Sessions a linie

- `sessions.id` je `ImageSession.id` z appky Ol1nLLM, `title` volný text (`server/schema.sql:5-12`).
  Ingest: `POST /api/ingest/manifest`, `PUT /api/ingest/images/{sha}`, `…/finalize`
  (`server/main.go:115-117`). Značka „pro výlohu“ chybí, `showcase` se v repu nevyskytuje.
- Uzel má `parent_id` (null = kořen), `source_image_id` (zdroj img2img) a `origin`
  `generated | upload` (`server/schema.sql:14-21`). Chybějící `origin` se při ingestu
  uloží jako `generated` (`server/ingest.go:113`).
- Seznam ukáže jen `origin` vlastního uzlu a `isImg2img` (`server/gallery.go:241`).
  Detail vrací `parentChain` (nodeId, imageId, sha256, prompt), nejvýš 50 kroků
  (`server/gallery.go:521-566`): bez `origin` předků a končí u předka bez blobu,
  takže kořen může chybět. Bránu „žádný předek `upload`“ to spolehlivě neověří.

## 7. Počty podle pásma

Z repa bez přihlášení (`Prompts/01-PLAN-uc25-spark-kalibrace.md:14`, stav
13. 11. 2026, ensemble nad 19 918 řádky manifestu):

| safe | suggestive | nsfw | explicit | unsure |
|---|---|---|---|---|
| 3 209 | 1 691 | 3 145 | 11 873 | 30,5 % ze všech |

Kolik `safe` je zároveň `unsure`, a tedy projde `view=shared`, dokumenty
neuvádějí. Podle téhož plánu (ř. 18) neproběhl import do galerie a
`FINETUNE_TAXONOMY` je v produkci vypnutý. Dokud se to nezmění, vrací
`band`/`view=shared` 400 a `similar` 404. Lokální DB v repu není.

Jak čísla získat bez produkčních tokenů: agregát `stats.json` z eval běhu na SPARKu
(`taxo-data/private/eval/`), když ho vlastník zpřístupní. Po importu read-only dotaz
na kopii DB:
`SELECT band, unsure, COUNT(*) FROM image_temperature it JOIN gallery g ON g.id = it.image_id GROUP BY 1, 2;`
API počty nevrací, šlo by jen stránkovat `?band=…&limit=200` (viz PR 5).

## 8. Co ingestu chybí: navržené PR do FineTuneGallery

Každý PR samostatně a bez stavu zveřejnění. Ten žije v ImageMarketu (§6 plánu).

1. **Kořen a čistota linie.** Do seznamu i detailu přidat `rootNodeId`,
   `rootOrigin` a `lineageHasUpload`, počítané rekurzivním CTE přes `nodes`
   (ne přes obrázky s blobem). K tomu filtr `lineage=text` (žádný předek
   `upload`) a `origin` v každé položce `parentChain`.
2. **Hromadný export.** `GET /api/export?<filtry galleryFilter>&cursor=`
   jako NDJSON: metadata položky, rozměry, `tags_json` (WD14 s confidence),
   efektivní popisek, pásmo, teplota, `unsure` a volitelně `embedding`
   (model, dim, base64 f32). Vždy přes view `gallery`, tedy bez blokovaných.
3. **Větší náhled.** `GET /thumb/{sha}?w=768|1024|1536` (pevná sada velikostí,
   cache na disku jako dnes) nebo `/preview/{sha}`. Stejné `blobVisible`.
4. **Výběr session pro výlohu.** Filtr `session_prefix=showcase/` nad
   `sessions.title`, nebo sloupec či tag session nastavovaný při ingestu
   (rozhodne vlastník). Totéž v `GET /api/sessions` spolu s `view=shared`.
5. **Počty pásem.** `GET /api/stats` rozšířit o `byBand` (band × unsure × blokované).
6. **Sdílený pohled všude.** Detail, `…/taxonomy`, `/api/sessions` a `similar`
   respektují `view=shared` a veřejný režim jako seznam (díra z §4).
7. **Token jen pro čtení.** Třída Access service tokenu (např.
   `READER_ACCESS_CLIENT_IDS`), které server povolí jen `GET` na
   `/api/images*`, `/api/export`, `/img`, `/thumb`, a to s vynuceným
   `view=shared`. Bez něj má token ImageMarketu i práva zápisu a mazání.

Předpoklad: import taxonomie do produkce a `FINETUNE_TAXONOMY=1` (UC25, plán 01 galerie).
