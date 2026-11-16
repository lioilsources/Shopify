# Export kolekce z FineTuneGallery (kontrakt)

Tento kontrakt čte brain (`brain/gallery_client.py`, `brain/gallery_import.py`). Ve FineTuneGallery ho implementuje část A plánu [05](../Prompts/05-PLAN-curation.md). Než bude v galerii hotový, testuje se proti fixtuře v `services/brain/tests/test_gallery_import_db.py`.

## Přístup

- Hlavičky každého požadavku:
  - `Authorization: Bearer <GALLERY_EXPORT_TOKEN>`
  - `CF-Access-Client-Id` a `CF-Access-Client-Secret` (vlastní service token pro shop)
- Token je jen ke čtení a platí jen pro `/api/export/*`. Není to `WORKER_TOKEN` galerie ani token dávky ze SPARKu.

## `GET /api/export/collections/{slug}?since=<kurzor>&cursor=<stránka>`

```json
{
  "items": [
    {
      "imageId": "…",
      "sha256": "64 hex znaků",
      "theme": "animals | dinosaurs | machines | plush | landscapes | pets",
      "caption": "česky nebo anglicky",
      "prompt": "…",
      "params": { "model": "qwen-image", "…": "…" },
      "style": "akvarel",
      "subject": "liška",
      "tags": ["fox", "forest"],
      "rootNodeId": "…",
      "width": 1536,
      "height": 1024,
      "band": "safe",
      "addedAt": "RFC3339",
      "revoked": false
    }
  ],
  "next": "kurzor další stránky, nebo null",
  "until": "kurzor pro příští běh (`since`)"
}
```

- **Bezpečnostní podmínky vynucuje galerie.** Do `items` jde jen obrázek s `band='safe'`, `unsure=0` a `lineage=text`.
- **Bezpečnostní stažení.** Obrázek, který podmínky přestal splňovat nebo byl zablokovaný, přijde s `revoked: true`. Shop ho skryje.
- **Odebrání z kolekce se neexportuje** (K4). Shop ho ignoruje.
- **Volitelná pole:**
  - `style` a `subject` (zadání showcase, plán 04). Bez nich zůstanou filtry stylu a námětu prázdné.
  - `tags` (WD14), podle kterých brána označí obrázky k ruční kontrole.
- **Oproti plánu 05 přibylo:** `tags`, `style`, `subject` a `revoked`.

## `GET /api/export/img/{sha256}`

- Vrací bajty originálu. Shop ověří sha256 a uloží originál k sobě (K3).
- Vydá jen obrázek, který v exportu skutečně je. Na ostatní odpoví 404.

## Co s položkou udělá shop

| situace | výsledek |
|---|---|
| nová položka | `draft` se `source_key = gallery:<imageId>`, bez ceny, kategorie podle `theme` |
| znovu přijde | aktualizuje se. Stav zůstane, kromě skrytí při blokujícím důvodu. |
| model mimo [LICENCES.md](LICENCES.md) | důvod `licence` (blokuje zveřejnění) |
| nepodařilo se stáhnout originál | důvod `original` (blokuje). Příští běh ho zkusí znovu. |
| rizikový tag (nápis, podpis, logo, člověk, dítě…) | důvod `review`, jen upozornění k ruční kontrole |
| `revoked: true` | `hidden` s důvodem `revoked` |
| neznámé téma | přeskočeno |

Model, prompt, tagy a linie se ukládají do `products.source_meta` a nikdy se z nich nestanou veřejné filtry. Model se zákazníkovi neukazuje (plán 02, §6).
