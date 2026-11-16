# 05 — Kurátorství v galerii a export do shopu

Cíl: Olin vybírá fotky pro SlopMarket přímo ve FineTuneGallery a shop si vybrané fotky sám převezme. Galerie rozhoduje, **co** se smí prodávat. Shop rozhoduje, **jak** se to prodává (cena, provedení, zveřejnění).

Navazuje na plán 02, fázi 1, krok 2 (adaptér obrázků). Předpoklad: jsou mergnuté PR galerie #13 (lineage) a #15 (`view=shared` všude) a v galerii jsou importovaná taxonomická data.

## Co galerie umí dnes (origin/main 3d84131)

- **Datasety** (`datasets` + `dataset_items`): přidat a odebrat obrázek přes API, naplnit podle filtru, detail. Jsou ale stavěné na LoRA: trigger word, repeats, tempMax a build kohya balíku.
- **UI:** obrázky jdou do datasetu přidat jen podle filtru. Jednotlivý obrázek z detailu ani z mřížky přidat nejde.
- **Exportní endpoint pro shop:** žádný. Nejblíž jsou `GET /api/images` a `GET /api/images/{id}` (prompt, params, parentChain).
- **Rozměry obrázku:** v DB nejsou, `width`/`height` chybí.
- **`WORKER_TOKEN`:** je záměrně zúžený na import taxonomie. Pro shop se nepoužije.
- **PR #14 (`session_prefix=showcase/`):** vybírá celé session, ne jednotlivé obrázky. Slouží výloze z generování (plán 04), kurátorský výběr nenahrazuje.

## Rozhodnutí (Olin, 16. 11. 2026)

| # | Otázka | Rozhodnutí |
|---|---|---|
| K1 | Čím fotky značit | **Nový koncept „kolekce“** (`collections`), oddělený od LoRA datasetů. |
| K2 | Jedna kolekce, nebo jedna na téma | **Jedna kolekce `shop`**, téma (R13) je štítek u položky. |
| K3 | Kde budou soubory obrázků | **Shop si originál zkopíruje k sobě** při importu, aby neběžel na galerii. |
| K4 | Co se stane s fotkou odebranou z kolekce | **V shopu nic.** Kolekce jen přivádí nové fotky, prodej je neexkluzivní a viditelnost řídí shop. Skrytí vynutí jen bezpečnost: fotka přestane být `safe`, nebo je zablokovaná. |

## Část A — FineTuneGallery (jeden PR)

1. **Migrace:**
   - `collections(id, slug UNIQUE, title, created_at)`
   - `collection_items(collection_id, image_id, theme, note, added_at, removed_at)`
   - Odebrání nastaví `removed_at`. Shop to nepřebírá (K4), slouží jen pro historii v galerii.
2. **API (admin, za CF Access jako zbytek UI):**
   - `GET /api/collections`
   - `POST /api/collections`
   - `POST /api/collections/{slug}/items` s tělem `{add:[{imageId, theme}], remove:[imageId]}`
   - `POST /api/collections/{slug}/items/from-filter?…` se stejnými parametry jako galerie
3. **UI:**
   - V detailu i v mřížce klávesa `S` přidá obrázek do kolekce nebo ho z ní odebere. Výběr tématu ze seznamu R13.
   - Odznak „v shopu“ na náhledu.
   - Filtr galerie `collection=shop`, aby šlo procházet už vybrané.
4. **Rozměry:**
   - Nové obrázky dostanou `width`/`height` při ingestu.
   - Stávající doplní jednorázový backfill z PNG hlavičky. Stačí CPU, SPARK není potřeba.
5. **Export:** `GET /api/export/collections/{slug}?since=<RFC3339>`
   - Vynucený `view=shared` (`band='safe' AND unsure=0`) a `lineage=text`. Volající to nemůže vypnout. Položka, která tyhle podmínky přestane splňovat, se vrátí jako `revoked` (bezpečnostní stažení).
   - Pole: `imageId`, `sha256`, `theme`, `caption`, `prompt`, `params`, `rootNodeId`, `width`, `height`, `band`, `addedAt`, `revoked`.
   - Stránkování kurzorem. `since` vrací jen změny, takže import je přírůstkový.
6. **Soubory přes export:** `GET /api/export/img/{sha256}` vydá jen obrázek, který v exportu skutečně je.
7. **Auth:**
   - Vlastní read-only bearer `SHOP_EXPORT_TOKEN` plus vlastní CF service token, platný jen pro `/api/export/*`.
   - Není to worker token ani token dávky ze SPARKu.
8. **Testy:**
   - Export nikdy nevrátí obrázek mimo `safe`, `unsure` ani `upload`.
   - Bez tokenu vrací 401. Token neotevře nic mimo `/api/export/*`.
   - Bezpečnostní stažení (`revoked`) se propíše, odebrání z kolekce ne.

## Část B — Shopify (krok 2 fáze 1)

1. `services/brain/brain/gallery_import.py` plus příkaz `python -m brain.gallery_import`.
   - Stáhne změny od posledního běhu. Kurzor uloží do tabulky `import_state`.
2. **Každá položka:**
   - `upsert_product` se `source_key = gallery:<imageId>`, stav `draft`, kategorie podle `theme`, bez ceny.
   - Do `attributes` jde téma, rozměry a `rootNodeId`.
   - Originál se zkopíruje do úložiště shopu (K3).
3. **`revoked`:** `set_status(hidden)`. Odebrání z kolekce se v shopu neprojeví (K4). Stáhnout produkt z prodeje jde jen v `/admin/review`.
4. **Zveřejnění:** Olin zveřejňuje v `/admin/review` jako dnes. Galerie vybírá, shop schvaluje.
5. **Konfigurace v `.env`:** `GALLERY_URL`, `GALLERY_EXPORT_TOKEN`, CF client id a secret. Nic z toho se necommituje.
6. **Testy:**
   - Import nad fixturou exportu.
   - Opakovaný import nic nezduplikuje.
   - `revoked` produkt skryje, odebrání z kolekce ho nechá být.

## Postup kurátora (Olin)

1. V galerii nastav filtr: téma, `safe`, vysoké skóre. Projdi mřížku a klávesou `S` označ fotky.
2. Pro hromadný výběr: „přidat podle filtru“, pak ručně vyhoď, co se nehodí.
3. Spusť import v Shopify (později cron). Nové fotky se objeví jako koncepty v `/admin/review`.
4. Ve schvalování doplň provedení a zveřejni.

## Pořadí

1. Merge galerie #13 a #15, pak import taxonomie (zvlášť, s kontrolou karantén).
2. Část A jako jeden PR ve FineTuneGallery.
3. Část B jako jeden PR tady.
4. Ověření: 10 fotek v kolekci, import, schválení, viditelné v chatu a v galerii shopu. Zablokování jedné fotky v galerii ji v shopu skryje.
