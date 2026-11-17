# 06 — Předávka: stránka SlopMarket na olin.now (MacBook)

Pro session `olin.now-Macbook`. Screenshoty dělá MacBook, repo `ol1n.now`.
Posílá se až po splnění podmínek níže.

## Podmínky odeslání (hlídá Shopify session)

1. V katalogu je demo dávka `demo/batch-01.yaml` (50 obrázků z L40S,
   příznak `demo`), importovaná přes `python -m brain.demo_import … --hide-legacy`.
   Staré vzorky ChatShopu (boty, disky, trička) jsou tím skryté.
2. Běží instance dostupná z MacBooku: web a brain na M2 vystavené do LAN
   (`--host 0.0.0.0`), později nasazení (krok 7). Adresu pošle Shopify
   session ve zprávě, do repa nepatří.
3. Tvář a lidé: v dávce nejsou (pravidlo v1). Restyler se nefotí, dokud
   to Olin výslovně nepovolí.

Olin 17. 11. 2026: „handoff MacBook z toho udělá screenshoty a deployne
na olin.now“. Merge a deploy stránky jsou tedy schválené pro tuhle stránku.

## Úkol

V `ol1n.now` založit `apps/slopmarket/` podle vzoru `apps/terrareality`
(webová aplikace bez stažení):

- `meta.md`: `slug: slopmarket`, `name: SlopMarket`,
  `repo: lioilsources/Shopify`, `desktop: Web`, `mobile:`, `langs: cs`
  (angličtina přijde s krokem 4b), `featured: false`. `order` je na tobě.
- `icon.png` 512×512. Logo zatím neexistuje, proto se nejdřív zeptej Olina.
  Nevymýšlej ho sám.
- Screenshoty `screenshots/raw/desktop/web/` (1440×900) a
  `screenshots/raw/mobile/web/` (390×844) z běžící instance:
  1. Úvod: chat nahoře s odpovědí a štítky filtrů, například na dotaz
     „krajina na plakát“, pod ním galerie.
  2. Galerie s vybranou kategorií a zapnutými filtry (Hodí se na, Orientace).
  3. Detail obrázku: náhled s vodoznakem, tabulka „Hodí se na“, označení AI.
  4. Výsledek dotazu jen z filtrů, například „na hrnek“.

  Admin (`/admin/review`) nefotit, není veřejný.
- `make screenshots && make build`, kontrola v `dist/`, PR do `ol1n.now`,
  merge a `make deploy` (Olin to schválil, viz výše). Gate repa `ol1n.now`
  musí projít.
- Na screenshotech je štítek „Demo“. Nezakrývat ho a v textu stránky
  napsat, že katalog je zatím ukázkový.

## Text stránky (návrh, česky)

Tagline: *Obrázky z vlastního AI ateliéru k tisku: plakát, hrnek, tričko i tapeta.*

Popis (krátce, bez slibů, které obchod zatím neplní):

- Katalog AI obrázků (zvířata, dinosauři, stroje, plyšáci, krajiny, psi
  a kočky), každý s tabulkou, na co se hodí a do jaké velikosti.
- Chat nahoře mění výběr v galerii. Funguje i bez jazykového modelu:
  „liška akvarel na hrnek“ nastaví filtry.
- Všechny obrázky jsou generované AI a jsou tak označené. Ve v1 nejsou
  na obrázcích lidé.
- Objednávka je zatím na poptávku. Nepsat nic o platbě kartou, dopravě ani
  cenách, dokud to obchod neumí (fáze 4).

## Zakázáno

- Ve screenshotech nesmí být adresy LAN, tokeny, admin ani `.env`.
- Neopisovat do textu tvrzení z repa, která nejsou hotová. Stav je
  v `Prompts/02-PLAN-imagemarket.md` §0.
