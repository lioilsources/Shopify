# Rozhodnutí vlastníka

Odpovědi na otázky R1–R13 z [plánu 02, §4](../Prompts/02-PLAN-imagemarket.md).
Zapsáno 16. 11. 2026 ve fázi 0. Novější rozhodnutí přepisují starší; změna se
zapisuje sem s datem, ne přepisem řádku.

| # | otázka | rozhodnutí | dopad |
|---|---|---|---|
| R1 | Kde se staví? | V tomto repu (16. 11. 2026). | Obecné věci do jádra, obrázkové do vlastních modulů. |
| R2 | Účty, objednávky, platby, fronta jobů | **Nová Go služba `services/shop`** vedle brainu. | Tři běhová prostředí (TS, Python, Go); brain zůstává na LLM, ingest a práci s obrázky. |
| R3 | Co se prodává jako první | **Poptávka bez platby**, vyřizuje vlastník. | Fáze 1 končí stavem objednávky `submitted` a zprávou vlastníkovi. |
| R4 | Platí se za tvorbu z fotky? | **Ne, zdarma s denní kvótou**; náklad nese marže tisku. | Žádné kredity, žádný nákup v aplikaci kvůli tvorbě. |
| R5 | POD výrobce pro malé formáty | **Po rešerši a zkušební objednávce.** | Podklad [FULFILMENT.md](FULFILMENT.md); výběr před fází 4. |
| R6 | Partneři pro velký formát | **Najít kandidáty** (rešerše). | Seznam v [FULFILMENT.md](FULFILMENT.md); do výběru jen poptávka. |
| R7 | Které modely smí do prodeje | **Podle [LICENCES.md](LICENCES.md).** FLUX.1-dev a odvozené ven; placená tvorba s tváří (InsightFace) se nespouští do vyjasnění. | Showcase jen z licenčně čistých modelů. |
| R8 | Jména umělců ve stylech | **Jen autoři mimo ochranu** (70 let po smrti); jinak popisný název stylu. | Registr stylů potřebuje rok úmrtí autora. |
| R9 | Veřejný název a doména | **SlopMarket** na **https://slop.ol1n.com** (17. 11. 2026), katalog veřejně hned; admin a ingest za Cloudflare Access. | Pracovní název „ImageMarket“ v plánech zůstává jako název projektu; veřejné texty používají SlopMarket. |
| R10 | Fotky lidí v tvorbě z fotky | **Bez lidí ve v1.** Jen mazlíčci, auta, domy, plyšáci a předměty. | Zachování tváře a souhlas se zpracováním tváře se ve v1 nestaví; nahraná fotka s detekovanou lidskou tváří se odmítne. Lidi až po vyřešení R7. |
| R11 | Fakturace, DPH, doručení | **Fakturuje vlastník, start ČR + SK.** | Ceny v CZK (SK v EUR až s platbami, fáze 4). |
| R12 | GPU pro veřejnost | **Podle návrhu plánu:** obchod plně použitelný bez LLM (hybridní hledání, filtry), chat jen když LLM běží; tisková data dávkově se slibem „do 24 h“. Po prvních číslech rozhodnout mezi malým LLM vedle ComfyUI a cloudovým API. | Režim bez LLM je provozní režim, ne jen vývojový. |
| R14 | Tváře v demo katalogu | **Výjimka jen pro demo (17. 11. 2026):** čistě vygenerované tváře bez předlohy, tedy děti, rodiče, prarodiče, miminka a tváře zvířat a ufonů, ve stylech Restyleru. | Jen přes `brain.demo_import` s příznakem `demo`, nikdy na prodej, nikdy z galerie ani z nahrané fotky. Žádná skutečná osoba, celebrita ani podoba. Děti jen v rodinném a portrétním kontextu, oblečené. Téma `portraits` import z galerie odmítá. R10 pro tvorbu z fotky platí dál. |
| R13 | Témata výlohy a pořadí | **Podle plánu 04, §1:** zvířata, dinosauři, stroje a vozidla, plyšáci, krajiny, psi a kočky. | Pořadí stopy S i ingestu výlohy. |

## Co z toho plyne pro plán

- R10 zužuje fázi 3b: krok „zachovat podobu“ odpadá, restyl běží jen cestou
  bez tváře (hloubka, editační model s volnou licencí). Nahrání potřebuje
  detektor lidské tváře jako bránu.
- R9: veřejné texty webu a appky se jmenují SlopMarket; identifikátory v kódu
  (`chatshop`, služby) se kvůli názvu nepřejmenovávají.
