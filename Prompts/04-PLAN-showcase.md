# ImageMarket — plán showcase (co vygenerovat do výlohy)

Příloha k [02-PLAN-imagemarket.md](02-PLAN-imagemarket.md), stopa S. Výloha
potřebuje vlastní obsah: v galerii jsou hlavně pokusy a NSFW motivy, které se
ukazovat nedají, a zákazník musí mít z čeho vybírat. Tenhle plán říká, která
témata, v jakých stylech a formátech, na kterém modelu, v jakém pořadí a kolik.

## 0. Stav

| krok | stav | poznámka |
|---|---|---|
| S0 příprava | nezačato | čeká na R13 (pořadí témat) |
| S1 srovnání modelů schnell × dev × Qwen | — | ~310 obrázků na model; smí běžet na L40S |
| verdikt: který model na co | — | arch po trojicích |
| S2 pilot stylů | — | 6 témat × 8 námětů × ~40 stylů, na vybraném modelu |
| verdikt: téma × styl | — | |
| S3 výroba | — | jen schválené buňky |
| S4 doplňky | — | panoramata, vzory, sezóna, ukázky z fotky |

## 1. Odpověď na otázku: obličeje, plyšáci, auta, dinosauři?

Téma se hodí do výlohy, když je bezpečné pro děti, nestojí na cizích právech,
model ho umí nakreslit správně, funguje v mnoha stylech a jde na víc produktů.

| téma | pro koho | práva | umí to model | hotové náměty | pořadí |
|---|---|---|---|---|---|
| **zvířata** (les, safari, farma, moře, ptáci, hmyz, plazi, mazlíčci) | všichni | čisté | ano | Lexify: 7 balíčků, 350 námětů | 1 |
| **dinosauři** | děti, rodiče, školy | čisté | ano; počet nohou a správnost druhu kontrolovat | Lexify: 30 námětů (PR #15) | 2 |
| **stroje a vozidla** (bagr, traktor, hasiči, vlak, loď, letadlo, raketa) | děti, rodiče, řidiči | čisté, když jsou obecné: bez značek, log a nápisů | ano | sepsat (lodě a bagry viz §10) | 3 |
| **plyšáci a hračky** | děti, rodiče | čisté, když nepřipomínají cizí postavy | ano | sepsat ~30 | 4 |
| **krajiny a příroda** (hory, les, moře, louky, houby, květiny) | dospělí, interiér, velký formát | čisté | ano | sepsat ~40 | 5 |
| **psi a kočky podle plemen** | dospělí, dárky | čisté | ano; plemeno kontrolovat | generátor Lexify má seznamy plemen | 6 |
| jídlo a kuchyně (ovoce, zelenina, káva, víno, koření) | interiér, gastro | čisté | ano | Lexify: 100 námětů | 7 |
| vesmír, podmořský svět | děti, interiér | čisté | ano | sepsat | 8 |
| fantasy a hry (draci, hrady, roboti, sci-fi města) | hráči, podložky | jen vlastní návrhy | ano | sepsat | 9 |
| koníčky (rybáři, myslivci, houbaři, včelaři, hasiči, motorkáři) | dárky | čisté | ano | sepsat | 10 |
| vzory (květinové, geometrické, dětské) | látky, tapety, obaly | čisté | chce bezešvé generování | — | S4 |
| panoramata pro vozy (vlci, orli, koně, hory, bouře, plameny) | polepy, plachty | čisté | chce široký formát | — | S4 |
| sezóna (Vánoce, Velikonoce, Valentýn, začátek školy) | dárky | čisté | ano | — | S4, s předstihem 8 týdnů |
| **ikonická auta** (konkrétní modely a roky) | fanoušci aut | **značky a design výrobců**; pro kartičky popisné, pro zboží riziko | na FLUX.1-dev ano | Lexify: 30 námětů (lokální větev) | až po právní kontrole |
| **obličeje** | — | podoba skutečných lidí, děti blokuje galerie | — | — | **do katalogu ne** |
| vlajky, mapy, číslice, písmena, anatomie těla | školy | čisté | **ne**: model je kreslí špatně | Lexify: 4 balíčky | negenerovat; sázet vektorem |
| emoce | školy | čisté | jen na zvířatech a postavičkách, ne na dětech | Lexify: 50 námětů | později |

**Obličeje:** cizí portrét si nikdo nekoupí a nese riziko podoby. Obličeje
patří jen do **ukázek služby** (před a po restylu), na syntetických dospělých
tvářích nebo na vlastních fotkách vlastníka, a až bude jasná licence
zachování tváře (plán 02, R7).

**Plyšáci** jsou téma i styl: „zvíře jako plyšák“ funguje na každém námětu
z Lexify a je to rovnou dětská kolekce.

## 2. Zásady

1. **Do výlohy jen z licenčně čistých modelů** (§3). Výroba na nečistém modelu
   by se vyhodila. Lexify má stejný dluh (fotky z FLUX.1-dev) a showcase ho
   může splatit, viz §9.
2. **Bez cizích práv:** žádné postavy z filmů, her a pohádek, žádné značky,
   loga, nápisy. Zadání to říká v `avoid` a brána to kontroluje.
3. **Motivy pro děti nejsou obrázky dětí.** Hrdinou je zvíře, stroj, hračka,
   robot. Lidské postavy jen dospělé a obecné.
4. **Co má být fakticky správně, model nesází.** Vlajky, mapy, čísla, písmena
   a popisky se přidávají vektorem. „Naučný“ se obrázek smí jmenovat až po
   kontrole člověkem (druh dinosaura, plemeno, tvar listu).
5. **Každý obrázek nese své zadání** až do katalogu: téma, klíč námětu, styl,
   formát, model, seed. Z klíče námětu Lexify plynou názvy v 17 jazycích.
6. **Showcase je v galerii oddělený:** session s předponou `showcase/`. Ingest
   výlohy bere jen je.
7. **Verdikt dělá vlastník** nad archy; automat jen třídí. Nic se nezahazuje.
8. SPARK jen přes broker, dávky přes `sparkctl exec`. L40S jen pro SFW měření.

## 3. Modely

| model | v labu | licence | role |
|---|---|---|---|
| **FLUX.1-schnell** | `flux-schnell`, přes gen-queue, 4 kroky, jen 1024×1024 | Apache 2.0 | kandidát výroby |
| **Qwen-Image** | `qwen-image`, jen v labu, graf v ComfyUI, 1328², 20 kroků, cfg 2.5, čte i negativ | generování je v pořádku (ověřil vlastník 16. 11. 2026) | kandidát výroby |
| **FLUX.1-dev** | `flux-manga` (v registru je to čistý FLUX.1-dev bez LoRA), graf v ComfyUI | nekomerční; vyhodnocení mimo produkci licence firmám dovoluje (znění ověřit) | **jen laťka ve srovnání** |

FLUX.1-dev je ve srovnání proto, aby bylo vidět, o kolik čisté modely
zaostávají, a jestli by stálo za to licenci koupit. Jeho obrázky do výlohy
nejdou, dokud licence není (plán 02, R7). SDXL base a Z-Image-Turbo zůstávají
možností na později, až je projde `docs/LICENCES.md`.

Co o těch třech víme z dřívějších měření (jiné náměty, tedy jen vodítko):

- Na techniky (tužka, akvarel, tuš) reagoval FLUX.1-schnell i FLUX.1-dev ze
  všech modelů nejvíc (vlna 7, barevná metrika).
- Qwen-Image se zatím měřil jen jako zdroj fotky pro restyl, ne se styly.
  README labu o něm říká, že styly umí hůř než Illustrious.
- **Rychlost:** Qwen-Image na SPARKu 131–167 s na obrázek, na L40S 20–35 s
  (měřeno 10. 11. 2026). FLUX.1-schnell jsou vteřiny. FLUX.1-dev změřit.
- FLUX.1-dev u dvou renesančních stylů nakreslil nahou postavu přes výslovné
  zadání oblečení (vlna 6). U zvířat a strojů to nehrozí, u lidských postav ano.

## 4. Kolekce: pro koho a na co

| kolekce | témata | styly | produkty |
|---|---|---|---|
| dětský pokoj (rodiče) | lesní zvířátka, safari, dinosauři, stroje, vesmír, moře, plyšáci | knižní ilustrace, akvarel, pastel, plochá grafika, vystřihovaný papír, plastelína, plyš a filc, pastelky | plakát, obraz, samolepky na zeď, růstový metr, polštář, deka, povlečení, puzzle, tričko |
| školy a školky | zvířata, ovoce a zelenina, počasí, roční období, povolání, doprava, dinosauři | plochá grafika, knižní ilustrace, fotografie, čárová kresba | plakáty do třídy, sady kartiček, pexeso, omalovánky, odměnové samolepky, diplomy, záložky |
| interiér (dospělí) | krajiny, botanika, houby, majestátní zvířata, kuchyně, abstrakce | olej, akvarel, tuš, secese, art deco, cestovní plakát, bauhaus, japonský dřevořez, botanická tabule | plátno, plakát, kov a akryl, tapeta, sklo za linku, roleta |
| dárky a koníčky | psi a kočky podle plemen, ryby, zvěř, houby, traktory, motorky | rytina, linoryt, patentový výkres, retro plakát, olej | tričko, hrnek, plakát, plechová cedule, polštář |
| hráči | draci, hrady, sci-fi města, roboti | digitální malba, olej, tuš | herní podložka, playmat, plakát, plátno |
| vozy a firmy | panoramata, vzory, livreje, obecné motivy řemesel | airbrush, fotografie, grafika | polep, plachta, roll-up, výloha |
| vzory | květiny, geometrie, dětské motivy | plochá grafika, akvarel | látka, tapeta, balicí papír, obal na mobil |

## 5. Styly

Registr Ol1nLLM má 310 stylů, ale měřených jen na dvou námětech (baletka, muž
u stolu). Pilot je změří znovu na tématech výlohy.

- **Z registru** (~30): techniky (tužka, akvarel, tuš, uhel, kvaš, olej,
  linoryt, pastelka) a epochy s jasnou plochou (ukiyo-e, secese, art deco,
  egyptská stěna, čínská tuš). Výběr podle `docs/style-matrix.md`.
- **Noví kandidáti** (~10, soubor kandidátů pro lab, do registru až po verdiktu):
  knižní ilustrace, plyš a filc, plastelína, vystřihovaný papír, cestovní
  plakát, patentový výkres, botanická tabule, plechová cedule, samolepka
  s bílým okrajem, omalovánka (čárová kresba).
- Styly vyřazené ve vlně 7 (pastelky, papírová koláž, risograph, pixel art…)
  se smí změřit znovu: verdikt tehdy platil pro jiné náměty.

## 6. Formáty

| formát | k čemu | kdy |
|---|---|---|
| 2:3 na výšku | plakát, plátno, tričko | S2, S3 |
| 3:2 na šířku | krajiny, plátno, puzzle | S2, S3 |
| 1:1 | polštář, hrnek, samolepka | S1 až S3 |
| 16:9 a 2,25:1 | herní podložka, tapeta na plochu | S3 |
| 3:1 až 5:1 | sklo za linku, plachta kamionu, polep | S4: široké generování nebo dopočet okrajů |

FLUX.1-schnell jde v labu jen 1024×1024; Qwen-Image a FLUX.1-dev jedou grafem
a rozměr se dá nastavit. Jestli gen-queue umí pro schnell i jiné rozměry, zjistí
S0. Když ne, je to argument proti schnellu, nebo důvod pustit ho grafem v ComfyUI.

## 7. Postup

### S0 — příprava (PR v `Ol1nLLM`, případně v `DuolingoCards`)

1. Ověřit, že `qwen-image` a `flux-manga` jdou v labu pustit jako běžné modely
   v txt2img se styly (Qwen byl dosud jen model pozice v restylu). Co chybí,
   doplnit jen pro lab; do appky nic.
2. Rozměry pro FLUX.1-schnell (§6).
3. Převodník zadání: z `brief` v balíčku Lexify (`subject`, `attrs`,
   `setting`, `avoid`) udělat soubor promptů pro lab. Všechny tři modely čtou
   větu, tedy sloupec `flux`. Popisek promptu = `téma/klíč`
   (např. `dinosaurs/dino.triceratops`).
4. Soubor kandidátů stylů (§5) a seznamy námětů pro témata, která Lexify
   nemá (stroje, plyšáci, krajiny, plemena).
5. Cesta metadat: ověřit, že popisek promptu a styl dojdou přes
   `lab export --send` do galerie a odtud do ingestu výlohy; když ne, doplnit.
   Session pojmenovat `showcase/<téma>/<vlna>`. Qwen-Image musí být v registru
   modelů galerie, jinak podle něj nepůjde filtrovat.
6. Třídění: nechat VLM soudce v galerii ohodnotit každý obrázek (námět je
   vidět celý, anatomie sedí, styl dorazil, žádný text) a podle toho řadit
   archy. Jen řadí, nevyřazuje.

### S1 — srovnání modelů: schnell × dev × Qwen

Otázka: který čistý model má vyrábět výlohu, jestli jeden na všechno, nebo
každý na něco, a o kolik oba zaostávají za FLUX.1-dev.

**Matice** (stejná pro všechny tři modely):

- 6 témat × 4 náměty × 12 stylů + obrázek bez stylu ke každému námětu
  = 312 obrázků na model, seed 777.
- Náměty: první čtyři z tabulky pilotu níž.
- 12 stylů: šest technik (tužka, akvarel, tuš perem, olej, linoryt, kvaš), tři
  epochy (ukiyo-e, secese, art deco), tři dětské (knižní ilustrace, plyš
  a filc, plochá grafika).
- Kontrola šumu: 4 buňky × 3 seedy na model, aby šel rozdíl mezi modely
  odlišit od rozdílu mezi seedy.
- Text v obraze: 6 buněk s krátkým nápisem (název plakátu česky s diakritikou).
  Qwen-Image má pověst modelu, který text umí; kdyby ho zvládl, zásada 4
  o sázení vektorem by se pro nadpisy dala zmírnit.

**Co držet stejné a co ne:**

- Stejný text promptu a stylu (věta, přirozený dialekt), stejný seed.
- Každý model ve svém referenčním nastavení (kroky, cfg, rozměr): měří se to,
  co by šlo do výroby. Arch ukazuje rozměr výstupu a výřez 1:1.
- Negativ čte jen Qwen-Image. Srovnání běží **bez negativu**; druhý průchod
  Qwenu s negativem jen na buňkách, kde selhal.

**Co se měří:**

| co | jak |
|---|---|
| styl dorazil | pohled vlastníka na arch; barevná reakce proti obrázku bez stylu jen jako řazení |
| námět je správně (nohy, kola, druh, celý v záběru) | VLM soudce řadí, vlastník rozhoduje |
| text a podpisy navíc, kde nemají být | WD14 tagy, pohled |
| nápis tam, kde být má | pohled, jen u šesti textových buněk |
| vhodnost pro tisk | rozměr výstupu, ostrost na výřezu 1:1 |
| čas na obrázek, paměť | log běhu; vedle sebe pro všechny tři |
| pásmo obsahu | taxonomie galerie; cokoli mimo `safe` vypsat |

**Čas a kde to běží.** Qwen-Image je úzké hrdlo: 312 obrázků je na SPARKu
11–15 hodin, na L40S 2–3 hodiny. **Srovnání smí běžet na L40S** (rozhodl
vlastník 16. 11. 2026): Qwen-Image a FLUX.1-dev tam, přes ComfyUI v tunelu,
stejným postupem jako vlna 7e; FLUX.1-schnell na SPARKu přes gen-queue (lease
s doplňkem `flux-schnell`), jsou to minuty. Před během na L40S přečíst jeho
poznámky k modelům, ověřit, že tam váhy obou modelů jsou, a nic nestahovat
bez souhlasu. Na L40S jen SFW a žádná firemní data. Časy v archu uvádět se
jménem stroje; FLUX.1-dev změřit na prvních buňkách.

**Výstup:** arch po trojicích (řádek = námět × styl, sloupce = tři modely,
pod tím výřezy 1:1), souhrnná tabulka (čas, podíl buněk se správným námětem,
nálezy mimo `safe`) a `docs/SHOWCASE.md`.

**Verdikt vlastníka:** pro každou skupinu (téma × druh stylu) jeden z výsledků:
schnell, Qwen, žádný čistý model nestačí. Poslední možnost je podklad pro
rozhodnutí o licenci FLUX.1-dev. Výsledek smí být i dělba (například techniky
na jednom, dětské styly na druhém).

### S2 — pilot stylů

- Na modelu (modelech) podle verdiktu S1.
- 6 témat × 8 námětů × ~40 stylů × 1 seed, k tomu obrázek bez stylu. Řádově
  2 000 obrázků na model. **Na Qwenu je to na SPARKu 3–4 dny čistého času**,
  na L40S 11–20 hodin; pokud Qwen vyhraje jen pro část stylů, pilotovat na něm jen tu část.
- Arch na téma: řádky náměty, sloupce styly.
- **Verdikt vlastníka** po buňkách téma × styl: jde do výroby, nebo ne.

Náměty (první čtyři z každého řádku jdou už do S1):

| téma | 8 námětů |
|---|---|
| zvířata | liška, jelen, sova, medvěd, vlk, zajíc, ježek, veverka |
| dinosauři | Tyrannosaurus, Triceratops, Stegosaurus, Brachiosaurus, Velociraptor, Ankylosaurus, Spinosaurus, Parasaurolophus |
| stroje a vozidla | bagr, traktor, hasičské auto, plachetnice, parní lokomotiva, nákladní auto, letadlo, raketa |
| plyšáci a hračky | medvídek, zajíc, robot, dřevěný vláček, slon, lev, dinosaurus, houpací kůň |
| krajiny | horské jezero, bukový les v mlze, mořské útesy, chalupa v zimě, levandulové pole, řeka v údolí, duny, polární záře |
| psi a kočky | labrador, jezevčík, mainská mývalí, siamská, německý ovčák, border kolie, francouzský buldoček, britská krátkosrstá |

### S3 — výroba

- Jen schválené buňky. Na téma všechny náměty (30–50) × schválené styly
  (10–15) × 3 seedy, ve formátu podle námětu.
- Odhad: 1 500–2 000 obrázků na téma, 6 témat kolem 10 000; po schválení
  zůstane odhadem třetina, tedy kolem 3 000 kusů ve výloze. Čísla jsou odhad.
- **Rychlost modelu rozhoduje o objemu.** 10 000 obrázků je na schnellu
  otázka hodin, na Qwenu na SPARKu přes dva týdny čistého času. Vyhraje-li
  Qwen, výroba se zúží (méně seedů, méně stylů na téma), rozloží do nočních
  dávek, nebo se rozhodne o jiném stroji.
- Dávky přes broker po tématech; export do galerie; taxonomie obsahu; ingest
  výlohy; schvalování po řadách (plán 02, §6).

### S4 — doplňky

- Panoramata pro velký formát a vzory (bezešvé generování).
- Další témata z §1 podle zájmu, sezónní kolekce s předstihem.
- Ukázky služby z fotky: syntetické dospělé tváře a vlastní fotky vlastníka
  (mazlíček, auto, plyšák) před a po, ve 12 stylech. Až po R7.
- Vzorky pro tiskový bench: 12–20 obrázků přes třídy stylu.

## 8. Kontrola kvality

| co | jak |
|---|---|
| námět celý a správný (nohy, kola, druh) | soudce řadí, vlastník schvaluje; u „naučných“ kontrola člověkem |
| styl dorazil | proti obrázku bez stylu v archu |
| žádný text, podpis, logo | WD14 tagy, soudce |
| pásmo obsahu | taxonomie galerie: jen `safe` a jisté |
| podobnost s cizí postavou | zadání bez jmen, ruční pohled u plyšáků a fantasy |
| duplicity | podobnost embeddingů v rámci buňky; nechat nejlepší z blízkých |

## 9. Lexify: co si projekty dají navzájem

- **Lexify → výloha:** hotová zadání obrázků (`brief`) a názvy námětů
  v 17 až 30 jazycích. To je pro katalog název, popis i hledání zadarmo.
- **Výloha → Lexify:** fotografický styl na čistém modelu je přesně to
  přegenerování, které Lexify potřebuje kvůli licenci. Obrázky ze showcase
  jdou vrátit do balíčků (rozhodne vlastník).
- **Školy:** balíček Lexify + sada z výlohy (plakát do třídy, kartičky,
  pexeso, omalovánky ke stejným námětům) je jedna nabídka pro učitele.

## 10. Co není ověřeno

- **Balíčky Lexify.** Na tomto stroji a na GitHubu je v `main` 15 balíčků po
  50 kartách; navíc dinosauři (otevřený PR #15, 30 karet) a ikonická auta
  (lokální větev `content/cars-iconic`, 30 karet, nepushnutá). **Lodě a bagry,
  o kterých vlastník mluví, tu nejsou**; nejspíš jsou na jiném stroji nebo
  nepushnuté. Než začne S0, sehnat aktuální seznam balíčků.
- **Qwen-Image a FLUX.1-dev jako běžné modely v labu se styly:** z dokumentace
  to neplyne, ověří S0.
- **Rychlost FLUX.1-dev na SPARKu** a rozměry FLUX.1-schnell přes gen-queue.
  Časy Qwenu jsou z jednoho měření vedle jiného běžícího modelu.
- **Jak modely zvládnou styly na těchto tématech:** to je účel S1 a S2.
  Dosavadní měření je na jiných námětech.
- **Znění licence FLUX.1-dev** k vyhodnocení mimo produkci; licence
  Qwen-Image podle ověření vlastníka, bez odkazu na zdroj v tomto plánu.
- **Objemy a podíl schválených:** odhad.
- **Pilot a výroba na L40S:** souhlas vlastníka platí pro srovnání (S1);
  pro S2 a S3 se zeptat znovu.
