# ImageMarket — use cases a tiskové profily

Příloha k [02-PLAN-imagemarket.md](02-PLAN-imagemarket.md); obsah výlohy řeší
[04-PLAN-showcase.md](04-PLAN-showcase.md). Slouží třikrát:
jako seed tabulky `products` (tiskové profily), jako osnova stránek „Co z toho
můžu mít“ na webu a jako zadání pro tiskový bench (které velikosti se měří).

**Čísla jsou výchozí odhad, ne specifikace.** Než se profil zapne k prodeji,
přepíše se podle specifikace výrobce (POD API, tiskárna): rozměr tiskové plochy,
minimální DPI, spadávka, formát souboru.

## Jak se počítá potřebné rozlišení

- Rozhoduje vzdálenost pohledu, ne plocha: `dpi_min ≈ 90 / vzdálenost_m`
  (mez oka, 1 úhlová minuta), `dpi_cíl = 2 × dpi_min`, strop 300.
- `pixely = rozměr_cm / 2,54 × dpi`.
- Strop masteru je **16 000 px** delší strany (víc dorovná RIP tiskárny a soubor
  by byl zbytečně velký). Profil smí strop přebít, když to výrobce chce.
- Model generuje ~1 Mpx (1024–1344 px delší strana). Všechno nad to je upscale.

## Skupiny

Sloupec **px** je delší strana při `dpi_min–dpi_cíl`. ★ = podle průzkumu teď
roste zájem (viz poznámka o zdrojích dole). Fáze = kdy se profil zapíná (plán 02, §11).

### A. Textil (fáze 4, POD API)

| produkt | plocha | DPI | px | zvláštnosti |
|---|---|---|---|---|
| tričko, mikina (DTG/DTF) | 30×40 cm | 150–300 | 2 400–4 700 | PNG s alfou, bez pozadí |
| ★ DTF nažehlovačky / gang sheet | arch š. 56 cm, délka do 5 m | 300 | podle motivů | víc motivů na arch (nesting), alfa |
| ★ UV DTF (obal na sklenici, tvrdé povrchy) | 24×11 cm | 300 | 2 800 | alfa, bílá podtisková |
| celopotisk (legíny, plavky, dresy) | panely do 90 cm | 150 | 5 300 | bezešvý vzor nebo motiv na střihovou šablonu |
| plátěná taška | 28×30 cm | 150–300 | 1 800–3 500 | alfa |
| výšivka (čepice, polo, nášivka) | do 10×6 cm | vektor | — | ≤ 12 barev nití, digitalizace u partnera |
| sítotisk (náklad 50+ ks) | 30×40 cm | vektor | — | separace 1–6 přímých barev |

### B. Zeď a interiér (fáze 4 POD, velké formáty fáze 5)

| produkt | rozměr | DPI | px | zvláštnosti |
|---|---|---|---|---|
| plakát A3–A0, B1 | 30×42 až 84×119 cm | 150–300 | 3 500–7 000 | spadávka 3 mm |
| fine-art (giclée) | 50×70 cm | 300 | 8 300 | |
| plátno na rámu | 40×60 až 100×150 cm | 100–150 | 2 400–8 900 | zrcadlený ohyb 3–5 cm |
| ★ kov (hliník), akryl, forex, dřevo | 30×45 až 80×120 cm | 150–300 | 2 700–9 000 | |
| ★ plechová cedule | 20×30 cm | 300 | 3 500 | retro motivy, koníčky |
| fototapeta | 2,5–4 × 2,5 m | 72–150 | 8 500–16 000 | pruhy s přesahem |
| ★ samolepicí tapeta se vzorem | dlaždice 60 cm | 150 | 3 500 | bezešvý vzor |
| ★ sklo za kuchyňskou linku | 60 × 200–400 cm | 100–150 | 8 000–16 000 | poměr 1:3 až 1:7, panorama |
| obraz na skle, sprchová zástěna | 50×70 až 90×200 cm | 100–150 | 2 800–11 800 | |
| roleta s potiskem | 100×150 cm | 100 | 5 900 | |
| dveře šatní skříně | 2–3 křídla 100×240 cm | 72–100 | 6 800–9 500 | dělení na křídla |
| garážová vrata | 250–500 × 210 cm | 50–72 | 4 900–14 200 | |
| samolepka na zeď (dětský pokoj) | 60–150 cm | 100–150 | 2 400–8 900 | alfa, ořezová křivka |
| kakemono, tapiserie | 60×90, 150×130 cm | 100–150 | 5 300–7 700 | |
| ★ světelný box (podsvícený textil) | 1–3 m | 100–150 | 3 900–16 000 | sytost pro podsvit |

### C. Domov, dárky, doplňky (fáze 4, POD API)

| produkt | plocha | DPI | px | zvláštnosti |
|---|---|---|---|---|
| hrnek | 20×9 cm | 300 | 2 400 | poměr 2,2:1 |
| ★ termohrnek (tumbler, sublimace) | 23,5×21 cm | 300 | 2 800 | kónický rozvin |
| polštář | 40–50 cm | 150–200 | 2 400–3 900 | |
| ★ deka (sherpa, fleece) | 150×200 cm | 75–100 | 5 900–7 900 | měkký materiál, detail se ztrácí |
| povlečení, osuška, sprchový závěs | 140×200 cm | 72–100 | 5 700–7 900 | |
| puzzle 500–2000 dílků | 68×48 cm | 200–300 | 5 400–8 000 | |
| kalendář, fotokniha, přání, oznámení | A5–A3 | 300 | 2 500–5 000 | text jako vektorová vrstva |
| obal na mobil | 9×18 cm | 300 | 2 100 | šablona s výřezem |
| skin na notebook, konzoli | 36×25 cm | 300 | 4 300 | ořez podle šablony |
| podložka pod myš | 25×21 cm | 200–300 | 2 000–3 000 | |
| ★ herní podložka XXL (desk mat) | 90×40 cm | 150–200 | 5 300–7 100 | poměr 2,25:1 |
| ★ playmat pro karetní hry | 61×35,5 cm | 200–300 | 4 800–7 200 | |
| hrací a sběratelské karty | 63×88 mm + 3 mm | 300 | 1 100 | nativně; série chce jednotný styl |
| ★ samolepky (die-cut, archy) | 5–10 cm | 300 | 600–1 200 | nativně; alfa + ořezová křivka |
| placky, odznaky | 25–58 mm | 300 | 700 | smaltovaný odznak: vektor, ≤ 6 barev |
| ★ akrylový stojánek, klíčenka | 5–15 cm | 300 | 600–1 800 | alfa, ořez, bílá podtisková, zrcadlení |
| dakimakura | 50×150 cm | 150 | 8 900 | poměr 1:3, dvě strany |
| dočasné tetování | 5–15 cm | 300 | 600–1 800 | zrcadlit |
| etiketa (víno, pivo, svíčka) | 9×12 cm | 300 | 1 400 | text vektorem |
| balicí papír, látka v metráži | dlaždice 30–60 cm | 150 | 1 800–3 500 | bezešvý vzor |
| jedlý papír na dort | A4, kruh 20 cm | 300 | 2 400 | potravinářský tisk u partnera |
| skateboard, snowboard, SUP | 20×80 až 30×300 cm | 100–300 | 4 700–11 800 | poměr 1:4 až 1:10 |

### D. Reklama a velký formát (fáze 5, poptávka u partnera)

| produkt | rozměr | DPI | px | zvláštnosti |
|---|---|---|---|---|
| citylight | 118,5×175 cm | 100–150 | 6 900–10 300 | |
| billboard (euro, bigboard) | 5,1×2,4 až 9,6×3,6 m | 15–40 | 4 000–9 500 | návrh v měřítku 1:10 |
| banner, plachta PVC | 3×1 m a víc | 50–72 | 5 900–8 500 | oka, svary: bezpečná zóna |
| mesh na lešení, fasádu | 10×8 m | 10–25 | 3 900–9 800 | |
| roll-up | 85×200 cm | 100–150 | 7 900–11 800 | spodních 15 cm v kazetě |
| vlajka, beachflag | 150×100, 80×300 cm | 72–100 | 4 300–11 800 | |
| výloha, podlahová grafika | podle místa | 72–100 | — | děrovaná fólie (one-way) |
| veletržní stěna | 3×2,3 m | 72–100 | 8 500–11 800 | dělení na panely |
| polep auta (bok, kapota, celopolep) | bok 4,5×1,4 m | 50–72 | 8 900–12 800 | šablona vozu, panely š. 137/152 cm |
| ★ itasha (anime polep) | jako polep auta | 50–72 | 8 900–12 800 | pozor na cizí postavy (plán 02, §12) |
| ★ dodávka, food truck, obytný vůz | bok 3–6 × 2 m | 40–72 | 9 500–16 000 | okna, dveře, lišty |
| kamion: plachta návěsu | 13,6×2,7 m | 20–40 | 10 700–16 000 | poměr 5:1, panorama |
| kamion: zadní dveře | 2,45×2,6 m | 40–72 | 4 100–7 400 | |
| autobus, tramvaj | 12–18 × 2,5 m | 20–40 | 9 500–16 000 | okna: děrovaná fólie |
| loď, člun, helma, motorka | individuálně | 72–150 | — | 3D tvar, vždy s partnerem |

### E. Kreativní sady a hobby (fáze 6, většinou bez GPU)

Tady není potřeba upscale, ale **převod**: obrázek se zjednoduší do podoby, kterou
jde vyrobit. Převody běží na CPU na JODĚ.

| produkt | výstup | převod |
|---|---|---|
| ★ malování podle čísel 40×50 cm | PDF s konturami, čísly a legendou | kvantizace na 24–36 barev, vektorové kontury |
| ★ diamantové malování 40×50 cm | mřížka 160×200, legenda | paleta DMC 30–50 barev, bez ditheringu |
| křížková výšivka | mřížka ~150×200 křížků | paleta DMC |
| mozaika ze stavebnice | mřížka 48–96 bodů | paleta dílků 5–40 barev |
| omalovánky | A4, čárová kresba | line-art 1 bit → vektor |
| ★ laserové gravírování (dřevo, břidlice, kůže) | 1 bit nebo stupně šedi, 254–508 dpi | dithering podle materiálu |
| litofanie | STL | výšková mapa z jasu |
| ★ 3D figurka | STL / GLB | už umí UGCFactory (`/v1/fc`) a Ol1nLLM (Trellis2) |
| ★ LED neon | SVG křivky, 1–3 barvy | kontura, zjednodušení |
| ★ tufting koberec | šablona 80×120 cm | ≤ 10 barev, velké plochy |
| vykrajovátko, razítko | STL / SVG | kontura → 3D tisk |

### F. Digitální (fáze 2 a 6)

| produkt | rozměr | poznámka |
|---|---|---|
| tisková data ke stažení + licence | podle profilu | nejjednodušší první prodej (plán 02, R3) |
| tapeta na mobil, plochu, hodinky | 1290×2796, 3840×2160, 5120×1440 | |
| avatar, profilovka | 1024² | |
| ★ profesionální portrét (headshot) | 2048² | tvář z vlastní fotky |
| obal alba, náhled videa, banner kanálu | 3000², 1280×720, 2560×1440 | |
| ★ balíček stickerů (Telegram, WhatsApp), emotes | 512² WebP s alfou; 112/56/28 px | viz HandWritenStickers |
| portrét a token pro stolní RPG | 1024², kruh 512 px | |
| živá tapeta, digitální rám | krátký klip | „Rozhýbat“ z Ol1nLLM (Wan) |

### G. Děti, školy a školky (fáze 4 a 6)

Motivy z kolekcí pro děti a školy (plán 04, §4). Text, čísla a písmena sází
appka vektorem; model je nekreslí.

| produkt | rozměr | DPI | px | zvláštnosti |
|---|---|---|---|---|
| plakát do třídy, do pokoje | A2–A1 | 150–200 | 3 500–6 600 | popisky vektorem |
| ★ růstový metr | 30×150 cm | 150 | 8 900 | poměr 1:5, stupnice vektorem |
| sada kartiček | 7×10 cm, 30–50 ks | 300 | 1 200 | nativně; jednotný styl sady |
| pexeso | 6×6 cm, 32 dvojic | 300 | 700 | nativně; rub vzorem |
| omalovánky | A4 | 300 | 3 500 | čárová kresba, vektor |
| ★ odměnové samolepky | 3–5 cm, arch A5 | 300 | 600 | ořezová křivka |
| diplom, pochvala, rozvrh hodin | A4 | 300 | 3 500 | text vektorem |
| záložka, obal na sešit, jmenovky | 5×18 cm, A4 | 300 | 2 100–3 500 | |
| dětské puzzle, kostky s obrázky | 30×40 cm | 200–300 | 3 100–4 700 | |
| batůžek, lahev, svačinový box | podle výrobce | 150–300 | 1 800–3 500 | POD |

### H. Z vlastní fotky (fáze 3, tvorba v appce)

Výstup pak jde na kterýkoli produkt ze skupin A–G.

| co | čím | pozor |
|---|---|---|
| portrét ve stylu (olej, akvarel, anime, epocha) | restyl + zachování tváře | hlavní případ |
| párový, rodinný, týmový portrét | restyl, víc tváří | víc tváří není změřené |
| ★ portrét mazlíčka | restyl bez tváře | InstantID/PuLID čte jen lidské tváře; změřit cestu přes hloubku/Kontext |
| auto, dům, motorka, loď jako obraz | restyl bez tváře | bez osobních údajů, snadný start |
| ★ plyšák nebo hračka dítěte jako hrdina plakátu | restyl bez tváře | bez fotky dítěte; dobrý dárek |
| karikatura, „já jako rytíř / astronaut“ | restyl + prompt z nabídky | jen předvolby, žádný volný prompt ve v1 |
| svatební oznámení, přání, výročí | restyl + textová vrstva | text sází appka, ne model |
| úprava detailu (pozadí, oblečení, vlasy) | inpaint s maskou | |
| ★ dětská knížka s dítětem jako hrdinou | série se stejnou postavou | fotky dětí: mimo v1, rozhodnutí R10 |
| návrh tetování | čárová kresba | |
| pamětní portrét (blízký, mazlíček) | restyl | citlivé, bez automatického zveřejnění |

## „Co si můžu dovolit“ — vhodnost obrázku k tisku

Každý obrázek dostane pro každý profil jednu ze čtyř známek. Web je ukazuje na
detailu obrázku, filtr „Hodí se na“ podle nich hledá a stránka use casu říká,
co známka znamená.

| známka | význam | pravidlo |
|---|---|---|
| ✅ hotovo | jde hned | nativní rozlišení ≥ `dpi_min` profilu |
| ⬆ po zvětšení | připravíme tisková data | potřebné zvětšení ≤ strop třídy obrázku z benche |
| ⚠ s výhradou | jde, ale s kompromisem | ořez 15–35 % nebo dopočet okrajů (panorama), nebo zvětšení nad strop třídy |
| ✖ nehodí se | nenabízet | poměr stran mimo dosah, motiv nejde oddělit od pozadí, příliš barev pro vektor |

Vstupy pravidla: rozměr a poměr stran obrázku, **třída zvětšení** (z tiskového
benche, podle stylu: plochá kresba snese víc než fotorealistická tvář), jestli
jde motiv oddělit od pozadí, a profil. Dokud bench nedoběhl, počítá se
s opatrným stropem 4× a známka ⬆ nese poznámku „orientačně“.

## Tvar profilu (seed)

```yaml
- id: tshirt-dtg
  group: textile
  label: {cs: Tričko, en: T-shirt}
  area_cm: [30, 40]          # tisková plocha, delší strana druhá
  aspect: free               # free | fixed | panorama
  view_distance_m: 0.5
  dpi: {min: 150, target: 300}
  max_px: 4800
  output: {format: png, alpha: true, icc: sRGB}
  bleed_mm: 0
  derive: [remove-background]
  fulfilment: pod            # pod | partner | digital
  phase: 4
  trending: false
```

## Zdroje a jistota

- Rozměry a DPI: běžná praxe tisku, sepsáno z hlavy 16. 11. 2026, **neověřeno
  u výrobců**. Ověření je krok fáze 0 (plán 02, §11, `docs/FULFILMENT.md`).
- Hvězdičky: průzkum webu 16. 11. 2026 našel jen texty prodejců a POD platforem
  (Gelato, Printify, Customily, prodejci DTF), žádná nezávislá čísla. Shodují se
  na prémiových a personalizovaných produktech (termohrnky, deky, kov a akryl,
  AI motivy na dárcích) a na DTF/UV DTF archách. Zbytek hvězdiček je odhad
  autora plánu. Brát jako nápovědu k pořadí, ne jako průzkum trhu.
