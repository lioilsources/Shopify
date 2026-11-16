# ImageMarket — plán

Tržiště obrázků k tisku postavené na modelu ChatShopu: nahoře chat, který mění
výběr v galerii, pod ním galerie, jejíž filtry rostou samy z toho, co se
prodává. Katalog jsou obrázky z FineTune gallery; zákazník si může nahrát
i vlastní fotku a upravit ji (restyl, zachování tváře, styly, inpaint). Mobilní
appka slouží k tvorbě a objednávce.

Staví se **v tomto repu** jako první ostrý katalog ChatShopu (rozhodnuto
16. 11. 2026). Navazuje na [01-PLAN-next-iterations.md](01-PLAN-next-iterations.md)
a rozpracovává jeho Iterace 2–4+. Obecné věci (objednávky, účty, platby,
schvalování ingestu, hledání) se dělají tak, aby je mohl použít i jiný katalog.

Zadání pro implementaci: „implementuj podle plánu“, vždy jednu fázi (§11).
Přílohy: [03-USE-CASES.md](03-USE-CASES.md) (produkty a tiskové profily),
[04-PLAN-showcase.md](04-PLAN-showcase.md) (co vygenerovat do výlohy).

## 0. Stav

| fáze | stav | poznámka |
|---|---|---|
| 0 rešerše a rozhodnutí | hotovo 16. 11. 2026 | `docs/DECISIONS.md`, `REUSE.md`, `GALLERY_API.md`, `LICENCES.md`, `FULFILMENT.md`, `CONTENT_POLICY.md`, `CLAUDE.md` |
| S showcase (souběžně) | — | plán 04; začíná srovnáním schnell × dev × Qwen; potřebuje okna GPU přes broker |
| T tiskový bench (souběžně) | — | potřebuje okno ComfyUI přes broker |
| 1 katalog a výloha | — | |
| 2 tisková data | — | |
| 3 mobilní appka | — | |
| 4 platby a výroba přes POD | — | |
| 5 velký formát | — | |
| 6 rozšíření | — | |

Každá session po sobě tuhle tabulku aktualizuje. Plán napsán 16. 11. 2026
z průzkumu rep, téhož dne přepsán na základ ChatShop. Co ověřeno není: §14.

## 1. Zadání vlastníka

- Nabízí se, co je v FineTune gallery (`finetune.ol1n.com`), s filtry.
  Vlastník si tam hraje i s NSFW motivy; do výlohy smí jen to, co pro ni
  vzniklo (showcase, plán 04).
- Zákazník může nahrát vlastní obrázek; Restyler, zachování tváře, styly
  a inpaint jsou součástí.
- Mobilní appka na zadání objednávky.
- Web „ve stylu Shopify“ = **ChatShop, tedy tento repozitář**,
  zaměřený na obrázky, tagy a styly. Vlastník ho má za pokročilejší model
  e-shopu než RobloxMarket; **RobloxMarket se jako základ nepoužívá.**
- Use casy na webu, „ať lidi ví, co si můžou dovolit“: u každého obrázku je
  vidět, na co a do jaké velikosti ho jde vytisknout (03-USE-CASES.md).

## 2. Z čeho se staví

Fáze 0 ověří každý řádek čtením kódu a zapíše do `docs/REUSE.md`, co se
přebírá a jak.

### Základ: ChatShop

| co ChatShop má | kde | jak to použije ImageMarket |
|---|---|---|
| chat jako vyhledávací pole: odpověď + událost `products`, která mění galerii | `services/brain` (FastAPI, RAG, SSE), `apps/web` | beze změny principu; kontext jsou atributy obrázku a tiskové profily („chci něco na plachtu kamionu“) |
| filtry, které rostou z katalogu: `filter_schemas` (text, range, set, bool) per kategorie, atributy v JSONB | ingest v brainu, sidebar ve webu | kategorie = téma (zvířata, dinosauři, krajiny…); každé téma si vypěstuje vlastní filtry (druh, prostředí, období) vedle společných (styl, technika, barvy, orientace, hodí se na, pro koho) |
| ingest pipeline: dohledání → extrakce atributů LLM → sloučení schématu filtrů → embedding | brain | krok „dohledání na webu“ se nahradí **adaptérem pro obrázek**: metadata z galerie, zadání showcase a popis od VLM |
| režim bez LLM (mock): stejné rozhraní, odpověď ze šablony a z hledání | brain | povinný provozní režim, ne jen vývojový (§5, R12) |
| web: SvelteKit PWA + BFF, galerie s velkými obrázky, košík v `localStorage`, admin ingestu | `apps/web` | základ výlohy; přibude detail, stránky use casů a stylů, poptávka |
| modul v AiStacku: LLM `shop` a embeddingy `shop-embed` (bge-m3) za gateway | AiStack | použít; spouštění jen přes broker |

Co ChatShop **nemá** a postaví se tady (jeho vlastní „Iterace 2–4+“): schvalování
ingestu v adminu, hybridní hledání (fulltext + vektory), objednávky, účty,
platby, produkční nasazení. Jeho návody na nasazení jsou z července 2026, před
brokerem a dnešními pravidly infrastruktury; srovnat podle §5.

### Ostatní zdroje

| potřeba | odkud | co tam je |
|---|---|---|
| zdroj obrázků | `FineTuneGallery` | `/api/images` s filtry (session, model, styl, médium, skóre, taxonomie), `/img/{sha256}`, `/thumb/{sha256}` 384 px, WD14 tagy, popisky, SigLIP 2 embeddingy a `/similar`, pásma obsahu safe až explicit, `view=shared`, trvalý blok nezletilých |
| obsah výlohy | `Ol1nLLM` (lab, registr 310 stylů), `DuolingoCards` (Lexify: 750 námětů s popisem obrázku a názvy v 17 jazycích) | plán 04 |
| tvorba z fotky | `MangaPrompts`, worktree restyler (`tgbot/`, `AUTH_MODE=app`) | backend Restyleru: `POST /api/render` s plánem kroků, fronta na ComfyUI, kvóta, NudeNet na každém výstupu |
| katalogy pro appku | `Restyler/packages/tsumiki_shared` | 300 stylů restylu, masky, parsování tváře na telefonu |
| editor masky, inpaint | `Ol1nLLM` | FLUX Fill grafy a editor masky |
| fronta jobů v Go, ověření účtenek z obchodů | `Webtoon-shop` | Postgres `SKIP LOCKED`; StoreKit 2 a Google Play |
| 3D figurka, stickery | `UGCFactory`, `HandWritenStickers` | až fáze 6 |

## 3. Zásady (invarianty)

1. **Model ChatShopu se zachová.** Chat mění výběr v galerii a filtry vznikají
   z ingestu, ne z ručně psaného číselníku. Kdo přidává filtr natvrdo do kódu
   webu, dělá to špatně.
2. **Veřejný klient nenese žádné tajemství.** Web ani appka neznají token ke
   galerii, ComfyUI ani k enginu. CI hledá v buildu vzory tokenů.
3. **Nic není veřejné, dokud to někdo neschválil.** Ingest zakládá drafty.
   Výtvory z nahraných fotek jsou soukromé navždy (jiná tabulka, jiný bucket).
4. **Výloha je jen SFW a jen ze showcase.** Ingest bere jen session označené
   pro výlohu, a i u nich jen pásmo `safe` a jisté.
5. **Obchod funguje i bez GPU.** Hledání, filtry, detail a poptávka nesmí
   záviset na tom, jestli zrovna běží LLM nebo ComfyUI (SPARK je sdílený
   a velký LLM s ComfyUI neběží současně).
6. **JODA = web, API, fronta, data. SPARK = výpočet přes broker.** API na GPU
   nikdy nečeká synchronně. L40S jen pro SFW měření showcase (rozhodnuto
   16. 11. 2026), ne pro provoz obchodu ani pro data zákazníků.
7. **Tvrzení o tisku se opírají o měření**, ne o odhad (bench, §7).
8. **Verdikt nad obrázky dělá vlastník.** Automat třídí a připravuje archy;
   nic sám nevyřazuje ani neschvaluje.
9. **Ceny se nevymýšlejí.** Cena = náklad od výrobce + pravidlo marže od
   vlastníka. Jinak „na poptávku“.
10. **Placený prodej až po právní kontrole** textů.
11. Platí globální pravidla: SPARK jen přes `sparkctl`, modely a custom nody
    jen se souhlasem vlastníka, žádné LAN adresy ani cesty ve veřejném repu,
    jeden požadavek = jeden PR, o merge a nasazení rozhoduje vlastník.

## 4. Rozhodnutí vlastníka

Opus se zeptá ve fázi 0 naráz a odpovědi zapíše do `docs/DECISIONS.md`.

| # | otázka | doporučení |
|---|---|---|
| R1 | Kde se staví? | **Rozhodnuto 16. 11. 2026: v tomto repu, nové repo nevzniká.** Obecné věci (objednávky, účty, platby, schvalování ingestu, hybridní hledání) jdou do jádra; obrázkové věci (adaptér ingestu, tiskové profily, tisková data, tvorba z fotky, appka) do vlastních modulů. |
| R2 | Kde budou účty, objednávky, platby a fronta jobů? | Nová Go služba `services/shop` vedle brainu (výchozí stack, hotové vzory fronty a nahrávání). Brain zůstane na LLM, ingest a práci s obrázky v Pythonu, BFF na UI. Cena: tři běhová prostředí. Alternativa: vše do brainu. |
| R3 | Co se prodává jako první? | (a) poptávka bez platby, vyřizuje vlastník; (b) tisková data ke stažení; (c) tisk přes POD API; (d) velký formát přes partnera. Fáze 1 končí u (a). |
| R4 | Platí se za tvorbu z fotky? | Ne. Zdarma s denní kvótou, náklad nese marže tisku. Kredity by v iOS appce musely jít přes nákup v aplikaci. |
| R5 | Který výrobce pro malé formáty? | Po rešerši `docs/FULFILMENT.md` a zkušební objednávce. Kandidáti: Gelato, Printful, Prodigi, Printify. |
| R6 | Partneři pro velký formát? | Vlastník dodá 1–3 tiskárny; do té doby jen poptávka. |
| R7 | Které modely smí do prodeje? | Podle `docs/LICENCES.md`. V pořádku jsou FLUX.1-schnell a Qwen-Image (generování na Qwenu ověřil vlastník 16. 11. 2026). FLUX.1-dev a odvozené (manga, Kontext, Fill) ven; FLUX.1-dev slouží jen jako laťka ve srovnání modelů (plán 04, §3) a případný nákup licence se rozhodne podle něj. **Zachování tváře** (InstantID, PuLID, FaceID) stojí na modelech InsightFace, které jsou podle všeho jen pro nekomerční výzkum; do vyjasnění se placená tvorba z fotky nespouští (§8). |
| R8 | Jména umělců ve stylech na webu? | Jen u autorů mimo ochranu (registr má rok); jinak popisný název stylu. |
| R9 | Veřejný název a doména? | Na vlastníkovi. Pracovně ImageMarket; zaznělo i „ChatMarket“. Repo je veřejné. |
| R10 | Fotky lidí: co je dovoleno? | Dospělí se souhlasem, žádné děti ve v1, výtvory soukromé, smazání na žádost i po lhůtě (návrh 30 dní bez objednávky). |
| R11 | Kdo fakturuje, DPH, země doručení? | Vlastník; start ČR + SK. |
| R12 | GPU pro veřejnost: chat potřebuje LLM, tisk a tvorba ComfyUI, a ty spolu neběží. | Fáze 1: obchod plně použitelný bez LLM (hybridní hledání, filtry), chat se zapne, když LLM běží. Tisková data dávkově se slibem „do 24 h“. Po prvních číslech rozhodnout: malý LLM vedle ComfyUI v rámci paměťového rozpočtu, nebo cloudové API pro chat. |
| R13 | Která témata do výlohy a v jakém pořadí? | Plán 04, §1: zvířata, dinosauři, stroje a vozidla, plyšáci, krajiny, psi a kočky. |

## 5. Architektura

```
prohlížeč ─► web (SvelteKit PWA + BFF) ─┬─► brain (FastAPI): chat SSE, ingest, práce s obrázky
appka (Flutter) ────────────────────────┤        └─ LLM a embeddingy přes gateway na SPARKu, nebo režim bez LLM
admin (za CF Access) ───────────────────┴─► shop (Go): účty, objednávky, platby, výroba, nahrávání, fronta
                                                 │
        Postgres + pgvector ◄────────────────────┤   S3 na JODĚ: public / private / uploads / masters
        ingest ◄── FineTune gallery (GET, token služby)
                                                 ▼
                                   fronta jobů (Postgres, SKIP LOCKED)
                                                 ▲ WORKER_TOKEN
                        worker (Go, SPARK) ──────┤ drží lease brokeru jen po dobu práce
                                                 ├─ ComfyUI: zvětšení, dopočet okrajů
                                                 └─ engine tvorby (instance backendu Restyleru)
```

- **Rozvržení** (podle ChatShopu): `apps/web`, `services/brain`, nově
  `services/shop`, `services/worker`, `apps/mobile`, `workflows/` (grafy pro
  tisk), `tools/printbench/`, `infra/`, `docs/`, `Prompts/`.
- **Databáze:** Postgres + pgvector na JODĚ; vývojová a testovací databáze
  tamtéž, protože na Macu Docker neběží (ChatShop počítá s lokálním compose).
  Dataset zakládá vlastník. Porty podle registru portů, do repa jen `.env.example`.
- **Úložiště:** S3 na JODĚ. `public/` náhledy s vodoznakem (nejvýš 1024 px),
  `private/` originály, `uploads/` fotky zákazníků, `masters/` tisková data.
  Soukromé jen přes krátce platné podepsané odkazy; tokeny se nelogují.
- **Veřejný vstup:** tunel a Caddy bez portů na hostu (ChatShop má Caddy na
  80/443 s vlastním TLS; nahradit). Admin a ingest za Cloudflare Access.
- **LLM a embeddingy:** jen přes gateway a broker. Embedding dotazu musí mít
  cestu bez SPARKu (fulltext; případně malý model na CPU, změřit na JODĚ).

### Datový model

ChatShop: `categories`, `filter_schemas`, `products` (atributy JSONB),
`product_embeddings` (vector 1024, bge-m3). Obrázek = `product`, téma = `category`.

| přibude | k čemu |
|---|---|
| sloupce `products`: stav `draft/listed/hidden`, zdroj (sha256, id v galerii, session), model, styl, rozměry, názvy a popisy cs/en, důvody brány | katalog obrázků; `price_czk` se u obrázku nepoužívá, cena je na provedení |
| `product_image_vectors` | embedding obrázku (SigLIP z galerie) pro „podobné“ |
| `print_profiles`, `profile_variants` | provedení ze seedu 03-USE-CASES.md, varianty a ceny výrobce |
| `product_fitness` | známka obrázek × profil (✅ ⬆ ⚠ ✖) a největší rozměr; zdroj filtru „hodí se na“ |
| `users`, `sessions` | přihlášení odkazem z e-mailu, stejné pro web i appku |
| `uploads`, `creations` | fotky zákazníků a výtvory z nich, vždy soukromé |
| `jobs` | fronta: `upscale`, `derive`, `render` |
| `orders`, `order_items`, `masters` | objednávka; položka = (obrázek nebo výtvor) × varianta × rozměr; tisková data |
| `payment_events`, `fulfilment_events`, `audit` | idempotentní webhooky, stopa |

### Stav objednávky

```
draft → submitted ─► quoted ─► accepted ─► paid ─► preparing ─► proof ─► approved ─► production ─► shipped ─► done
            └ (POD s pevnou cenou přeskočí quoted a proof)                                  kdykoli → cancelled
```

Fáze 1 umí jen `draft → submitted` (poptávka) a zprávu vlastníkovi.

## 6. Katalog

**Ingest obrázku** (adaptér v brainu, kroky ChatShopu):

1. *Dohledání:* řádek z galerie (model, styl, médium, rozměry, WD14 tagy,
   popisky, pásmo obsahu), zadání showcase (téma, námět, styl, formát; plán 04)
   a popis od VLM. Bere jen session označené pro výlohu, s `view=shared`.
2. *Extrakce:* LLM vrátí atributy podle schématu tématu. Co zadání showcase
   říká přesně (námět, styl), se nepřebíjí odhadem z obrázku.
3. *Sloučení schématu filtrů:* nové hodnoty rozšíří filtry tématu.
4. *Embedding:* text (název, popis, atributy) jako v ChatShopu; k tomu vektor
   obrázku z galerie.
5. Uložení jako `draft`. Opakovaný běh je idempotentní podle sha256.

Bez LLM (mimo jeho okno) projde ingest v omezené podobě z metadat a zadání
showcase; popis a volné atributy se doplní dávkou později.

**Brána zveřejnění.** Draft se vylistuje, jen když projde vším:

| kontrola | zdroj | když neprojde |
|---|---|---|
| session je označená pro výlohu | galerie, filtr `session` | nevstoupí vůbec |
| pásmo `safe`, ne `unsure` | taxonomie galerie | nevstoupí vůbec |
| celá linie je čistě z textu | `origin`, `parent_id`: žádný předek `upload` | jen ruční výjimka |
| model má povolenou licenci | `docs/LICENCES.md`, R7 | skryto |
| bez cizí postavy, značky, loga, textu a podpisu | WD14 tagy, seznam zakázaných | k ručnímu posouzení |
| schválení vlastníkem | admin, arch po 50, i po celých řadách | zůstává draft |

Co galerii chybí a přidá se tam samostatným PR ve `FineTuneGallery`: údaj
o kořeni linie, hromadný export embeddingů a tagů, případně větší náhled.
Stav zveřejnění žije tady, galerie o něm neví.

**Hledání:** fulltext + filtry vždy; vektory a chat, když jsou k dispozici
(hybrid z „Iterace 4+“ ChatShopu se dělá hned). Model se zákazníkovi neukazuje.

**Web:** hlavní stránka podle ChatShopu (chat nahoře, galerie s filtry),
detail (náhled, podobné, tabulka vhodnosti, „Chci tohle na…“), stránky use casů
(co to je, do jaké velikosti, co musí obrázek splnit, jak objednat), stránky
stylů a kolekcí pro publikum (děti, školy, interiér, koníčky, firmy), poptávka,
admin. Stránky katalogu se renderují na serveru kvůli vyhledávačům. Jazyky cs, en.

## 7. Tisková data

Model generuje ~1 Mpx; tisk chce 2 400 až 16 000 px (03-USE-CASES.md). Větší
obrázek se negeneruje přímo: model je na 1 Mpx naučený a ve větším rozlišení
opakuje motiv. Zvětšuje se hotový obrázek ve stupních.

**Bench (stopa T, `tools/printbench/`):**

1. Zjistit přes `/object_info`, které uzly a modely pro zvětšení ComfyUI na
   SPARKu má. Co chybí, sepsat se zdrojem, velikostí a licencí a **požádat
   vlastníka**; nic nestahovat samo.
2. Kandidáti: čistý zvětšovací model (RealESRGAN, UltraSharp, DAT/HAT);
   difuze po dlaždicích s ControlNet Tile (SDXL); SeedVR2; Z-Image-Turbo;
   kombinace difuze 2–4× a pak model 2–4×. U každého ověřit licenci.
3. Vzorek: 12–20 obrázků ze showcase přes třídy stylu (plochá kresba, tuš,
   akvarel, olej, fotorealismus, krajina, vzor), cíle 4×, 8×, 16×.
4. Výstup: arch s výřezy 1:1, čas a paměť, velikost souboru. Hlídat, jestli
   dlaždice nevymýšlejí texturu do plochých stylů.
5. Verdikt vlastníka → **třída zvětšení** podle stylu (strop 4× / 8× / 16×)
   a recept; zapsat do `docs/PRINT_BENCH.md` a do pravidla vhodnosti.

**Pipeline** (job `upscale`): profil → cílové pixely → recept → ComfyUI přes
worker a lease → kontrola (rozměr, DPI, profil sRGB, kontrolní součet) →
`masters/`. Do CMYK převádí tiskárna. Soubory mají stovky MB; do telefonu jde
jen odkaz.

**Odvozeniny** (job `derive`, většinou CPU v brainu): odstranění pozadí,
vektorizace, ořezová křivka, spadávka a zrcadlený ohyb, zrcadlení, dělení na
panely, bezešvý vzor, dopočet okrajů na jiný poměr stran (GPU), převody pro
hobby sady.

## 8. Tvorba z vlastní fotky

Engine se nepíše znovu: poběží **vlastní instance backendu Restyleru** a mluví
s ní jen `shop` (token služby jen na JODĚ, `X-User` = id účtu).

| potřeba | stav v enginu | co s tím |
|---|---|---|
| restyl se zachováním tváře, 300 stylů | je (PuLID na FLUX.1-dev, InstantID na SDXL) | licenčně nejisté (R7): obě cesty čtou tvář přes InsightFace a jedna jede na FLUX.1-dev |
| komerčně čistá cesta restylu | není | změřit editační modely s volnou licencí (kandidáti Qwen-Image-Edit, FLUX.2 klein 4B; licenci i to, jak drží podobu, ověřit) |
| inpaint s volnou maskou | neověřeno | přidat krok `inpaint`; předloha je v Ol1nLLM |
| restyl bez tváře (mazlíček, auto, dům, plyšák) | neověřeno | změřit cestu přes hloubku; licenčně jednodušší, vhodný první krok |
| výstup pro tisk | ~1–2 Mpx | navazuje job `upscale` |

Pravidla: jen předvolby, **žádný volný prompt ve v1**; nahrání přes API
(limit, překódování, odstranění EXIF a GPS, souhlas se zpracováním tváře,
kontrola obsahu a věku); každý výstup projde NudeNet, a když detektor neběží,
výstup se zahodí; kvóta na účet a IP; smazání kaskádou i v enginu a ve vstupní
složce ComfyUI; výtvor jde objednat, do katalogu nikdy.

## 9. Výroba

`FulfilmentProvider` ve službě `shop`, zapínaný po fázích:

1. **Poptávka** (fáze 1): položka, rozměr, kontakt → zpráva vlastníkovi.
2. **POD API** (fáze 4): varianty a ceny výrobce, objednávka s odkazem na
   master, webhooky. Odeslání musí jít pustit znovu.
3. **Partner** (fáze 5): nabídka, korektura (náhled 1:10 ke schválení),
   předání dat, ruční stavy.

Náhled produktu ve fázi 1: měřítko skládané v prohlížeči ze šablon (obrázek na
zdi s postavou, na tričku, na boku auta a návěsu). Fotorealistické mockupy až
z API výrobce.

## 10. Mobilní appka

Nová Flutter appka v `apps/mobile` (hned skill `setup-flutter-app`). Web zůstává
instalovatelná PWA jako v ChatShopu; appka přidává foťák, tvorbu a push.

- **Objednávka** (3a): chat a hledání z katalogu, detail, výběr use casu,
  náhled v měřítku, rozměr a varianta podle vhodnosti, košík, poptávka nebo
  platba v prohlížeči, stav, push.
- **Tvorba** (3b): fotka → styl → zachovat podobu → výsledek → oprava maskou →
  „Moje obrázky“ → objednat. Katalogy a masky z `tsumiki_shared`. Klávesnice
  se sama neotevírá.
- Platba za fyzické zboží jde mimo nákupy v aplikaci. Do obchodů až ve fázi 4.

## 11. Fáze

Každý krok je jeden PR. Fáze končí bránou. Stopy S a T běží od fáze 0, fáze
2 a 3 po fázi 1 souběžně.

### Fáze 0 — rešerše a rozhodnutí (bez produkčního kódu)

1. Zeptat se na R2–R13; zapsat `docs/DECISIONS.md`. Repo nemá `CLAUDE.md`:
   doplnit ho podle sdílené šablony (do 80 řádků: build, gate, invarianty).
2. Rozjet ChatShop v režimu bez LLM a projít kód. `docs/REUSE.md`: co zůstává,
   co se mění kvůli obrázkům, co chybí, co je zastaralé v infrastruktuře.
3. `docs/GALLERY_API.md`: API galerie proti kódu, potřebné PR (§6), aktuální
   počty podle pásem.
4. `docs/LICENCES.md`: model → licence → smí komerčně, se zdrojem. Generování,
   zachování tváře (InsightFace), zvětšování.
5. `docs/FULFILMENT.md`: POD výrobci a šablona pro partnery; opravit čísla
   v 03-USE-CASES.md.
6. `docs/CONTENT_POLICY.md`: pravidla obsahu a nahrávání (podklad pro právníka).

**Hotovo když:** dokumenty existují a R2–R13 mají odpověď nebo výslovné „počká“.

### Fáze 1 — katalog a výloha

1. Jádro: stav produktu (draft/listed), schvalování ingestu v adminu, hybridní
   hledání, srovnání infrastruktury (§5).
2. Adaptér ingestu pro obrázek; témata jako kategorie; růst filtrů ověřit na
   prvním tématu ze showcase.
3. Profily ze seedu, `product_fitness` s opatrným stropem, filtr „hodí se na“.
4. Web pro obrázky: mřížka, detail, podobné, náhled v měřítku, stránky use
   casů, stylů a kolekcí, náhledy s vodoznakem.
5. Chat nad obrázky: systémová instrukce, kontext atributů a profilů, režim
   bez LLM.
6. Služba `shop`: účty, poptávka (`orders` ve stavu `submitted`), zpráva
   vlastníkovi.
7. Nasazení na JODU za Cloudflare Access.

**Hotovo když:** vlastník na interní adrese najde obrázek chatem, filtrem
tématu i filtrem „hodí se na“, vidí vhodnost a odešle poptávku, která mu
přijde; a totéž projde s vypnutým LLM. **Brána:** veřejně jen na „nasaď“.

### Fáze 2 — tisková data

Fronta a worker s lease brokeru; job `upscale` podle benche; odvozeniny na
CPU; admin „připravit tisková data“; vhodnost podle tříd z benche; volitelně
prodej dat ke stažení (R3b).

**Hotovo když:** z poptávky na plátno 100×150 cm vznikne soubor, který tiskárna
přijme, a vlastník ho viděl vytištěný.

### Fáze 3 — mobilní appka

3a objednávka, 3b tvorba. Před 3b: vyjasněná R7, instance enginu, krok
`inpaint`, nahrávání a mazání, kvóty.

**Hotovo když:** z TestFlightu jde vyfotit, přestylovat, opravit maskou
a poslat poptávku; smazání účtu po sobě nenechá soubor na JODĚ ani na SPARKu.

### Fáze 4 — platby a výroba přes POD

Platební brána, vybraný výrobce, doprava a DPH, doklady, právní texty po
kontrole, mockupy z API, appka do obchodů.

**Hotovo když:** zkušební objednávka trička a plakátu projde od platby po
doručení bez ručního zásahu.

### Fáze 5 — velký formát

Nabídka a korektura s partnerem, panoramata, bezešvé vzory, šablony vozidel.

### Fáze 6 — rozšíření

Hobby sady, školní sady (pexeso, kartičky), 3D figurka, stickery, další jazyky.

## 12. Rizika

| riziko | dopad | opatření |
|---|---|---|
| licence modelů, hlavně zachování tváře | provoz bez licence | `docs/LICENCES.md`, R7; showcase jen z čistých modelů (schnell, Qwen) |
| čistý model je pomalý nebo slabý na styly | malá nebo jednotvárná výloha | srovnání schnell × dev × Qwen před výrobou (plán 04, S1) |
| chat bez LLM je slabší | hlavní rozdíl proti běžnému e-shopu nefunguje vždy | zásada 5, R12; měřit, jak často LLM běží |
| cizí postavy, značky, loga | porušení práv | brána §6, zadání showcase bez značek, ruční schválení |
| skutečné osoby, děti | osobnostní práva, GDPR | linie s `upload` nesmí ven; žádné děti ve v1; blok nezletilých |
| NSFW z galerie ve výloze | pověst, zákaz v obchodech s appkami | jen session pro výlohu + `safe` + schválení |
| tajemství v klientovi | únik přístupu ke GPU | zásada 2 a kontrola v CI |
| AI obsah a právo | výstup čistě z AI zřejmě není autorské dílo; povinnost označovat AI obsah | prodává se služba a tisková data, ne výhradní práva; ověřit právníkem |
| spotřebitelské právo | reklamace, odstoupení | zboží na míru má výjimku z odstoupení, reklamace ne; texty po kontrole |
| kvalita zvětšení, barvy mimo gamut | reklamace | bench, třídy zvětšení, korektura u velkých formátů |
| kapacita sdíleného GPU | čekání | fronta, slib v hodinách, dávky přes broker |
| tři běhová prostředí (TS, Python, Go) | složitost | jasné hranice (§5); R2 nabízí alternativu |

## 13. Pokyny pro implementaci

- Začni fází 0. Otázky R2–R13 polož najednou; neodhaduj odpovědi.
- Nejdřív ChatShop rozjeď a přečti. Jeho model (zásada 1) neměň; rozšiřuj ho.
- RobloxMarket nepoužívej jako předlohu.
- Fakta o API galerie a enginu ověřuj v kódu, ne z tohoto plánu (§14).
- GPU jen přes broker; nic na SPARKu neinstaluj. Chybějící uzel nebo model je
  otázka na vlastníka.
- Měření a třídění: připrav arch, verdikt nech na vlastníkovi.
- Nasazení, zveřejnění, `gh repo create`, placené služby jen na výslovný pokyn.
- Veřejné repo: žádné LAN adresy, cesty, e-maily, tokeny. Kód anglicky,
  dokumenty a PR česky.
- Po každé fázi aktualizuj tabulku v §0; odchylky zapiš do sekce
  „Aktualizace“ na konci souboru, ta má pak přednost.

## 14. Co není ověřeno

- **Uzly a modely pro zvětšení na SPARKu:** nezjištěno. První krok stopy T.
- **ChatShop:** popsán podle README, ARCHITECTURE.md a plánu iterací; kód
  nečten a aplikace nespuštěna.
- **API galerie a engine Restyleru:** podle průzkumu kódu jedním čtením.
- **Počty obrázků podle pásem:** z plánu kalibrace, mohou být staré.
- **Rozměry a DPI v 03-USE-CASES.md:** z praxe, ne od výrobců.
- **Licence:** FLUX.1-schnell je Apache 2.0, generování na Qwen-Image ověřil
  vlastník, FLUX.1-dev má nekomerční licenci na provoz. InsightFace,
  Qwen-Image-Edit (jiný model než Qwen-Image), FLUX.2 klein, Z-Image a SDXL
  checkpointy ověří `docs/LICENCES.md`.
- **Právní body v §12:** orientační, ne právní rada.

## Aktualizace

### 16. 11. 2026 — po fázi 0

- **R9:** veřejný název je **SlopMarket**; „ImageMarket“ zůstává jako název
  projektu v plánech.
- **R10: bez lidí ve v1.** Ve fázi 3b odpadá zachování tváře a souhlas se
  zpracováním tváře; nahrání má detektor lidské tváře jako bránu (fotka
  s tváří se odmítne). Lidi až po vyřešení licence InsightFace (R7).
- **R6:** kandidáti na partnera velkého formátu jsou v `docs/FULFILMENT.md`.
- **R5:** rešerše doporučuje Gelato na výrobu (tisk v ČR) a Prodigi jako první
  integraci (jediný se sandboxem); rozhodne zkušební objednávka.
- **ChatShop je dál od plánu, než §2 předpokládal** (`docs/REUSE.md`): chat
  dnes galerii nemění (karty jen v bublině), filtry bez kategorie nejsou,
  `price_czk` je povinné, admin a ingest jsou bez autentizace, `embed()` nemá
  cestu bez SPARKu. Fáze 1, krok 1 to musí dohnat dřív než adaptér ingestu.
- **Galerie** (`docs/GALLERY_API.md`): taxonomie v produkci neběží, takže
  `band`, `view=shared` a `/similar` dnes nefungují; linii nejde ověřit.
  Fáze 1, krok 2 závisí na PR 1, 4 a 6 ve FineTuneGallery a na zapnutí
  taxonomie.
- **Licence** (`docs/LICENCES.md`): kromě schnell a Qwen-Image jsou čisté
  i Qwen-Image-Edit, FLUX.2 klein 4B (ne 9B) a Z-Image-Turbo. Na zvětšení
  nepoužívat 4x-UltraSharp, na odstranění pozadí ne RMBG; BiRefNet a SeedVR2
  ano.

