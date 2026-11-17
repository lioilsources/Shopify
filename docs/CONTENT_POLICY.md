# Pravidla obsahu a nahrávání (SlopMarket)

Pracovní podklad pro právníka, ne hotové obchodní podmínky. Vychází z plánů
[02](../Prompts/02-PLAN-imagemarket.md) a [04](../Prompts/04-PLAN-showcase.md),
z [DECISIONS.md](DECISIONS.md) a [LICENCES.md](LICENCES.md). Stav k 16. 11. 2026.

## 1. Katalog (výloha)

Do katalogu smí obrázek, jen když projde vším níže (brána zveřejnění, plán 02 §6):

1. Pochází ze session galerie s předponou `showcase/`. Nic jiného z galerie do
   katalogu nevstoupí, ani ručně.
2. Je v pásmu obsahu `safe` a klasifikace je jistá (`unsure` nevstoupí).
3. Celá linie vznikla z textu: žádný předek není nahraná fotka (`upload`).
4. Vznikl na modelu, který [LICENCES.md](LICENCES.md) povoluje pro prodej
   (dnes FLUX.1-schnell, Qwen-Image; viz tam). FLUX.1-dev a odvozené ne.
5. Neobsahuje cizí postavu (film, hra, pohádka, maskot), značku, logo, nápis,
   podpis ani vodoznak. Automat hledá podle tagů a posílá k ručnímu posouzení.
6. Neobsahuje skutečnou osobu ani podobu skutečné osoby. Obličeje se do
   katalogu negenerují vůbec. Výjimka R14: demo portréty čistě vygenerovaných
   tváří, jen s příznakem `demo` a nikdy na prodej.
7. Neobsahuje děti (mimo demo portréty podle R14). Motivy pro děti mají za hrdinu zvíře, stroj, hračku nebo
   robota; lidské postavy jen dospělé a obecné.
8. Schválil ho vlastník (arch v adminu). Automat třídí, nikdy sám neschvaluje
   ani nevyřazuje.

Další pravidla katalogu:

- **Jména umělců** (R8): ve stylu jen u autorů 70 let po smrti; jinak popisný
  název („akvarel“, „japonský dřevořez“).
- **Naučné motivy** (druh dinosaura, plemeno, rostlina) se tak smí označit až
  po kontrole člověkem. Vlajky, mapy, čísla, písmena a popisky model nekreslí;
  sází je appka vektorem.
- **Označení AI:** každý obrázek je na webu označen jako vytvořený umělou
  inteligencí. Prodává se tisk, tisková data a služba, ne výhradní autorská
  práva k obrázku. (Ověřit právníkem: autorskoprávní status čistě AI výstupu
  a povinnost značení podle AI Act, čl. 50.)
- **Ikonická auta** a jiné motivy s designem výrobců: do katalogu ne bez
  právní kontroly.
- Na žádost držitele práv se obrázek stáhne z katalogu bez zbytečného odkladu
  (oznámení a odstranění) a zapíše do `audit`.

## 2. Nahrávání vlastní fotky (tvorba, fáze 3)

Ve v1 platí **bez lidí** (R10). Tvorba je jen pro mazlíčky, auta, domy,
plyšáky, hračky a jiné předměty.

| krok | pravidlo |
|---|---|
| přihlášení | jen s účtem; kvóta na účet i IP (R4: zdarma, denní limit) |
| souhlas | uživatel potvrdí, že má k fotce práva a že na ní nejsou lidé |
| velikost a formát | limit velikosti, překódování na serveru, odstranění EXIF a GPS |
| lidská tvář | detektor tváře na vstupu; nalezená tvář → fotka odmítnuta a smazána |
| obsah | kontrola obsahu (NudeNet a pásma galerie); cokoli mimo `safe` se odmítne |
| zadání | jen předvolby stylů, žádný volný prompt ve v1 |
| výstup | každý výstup projde NudeNet; když detektor neběží, výstup se zahodí |
| soukromí | nahrané fotky a výtvory jsou soukromé navždy (vlastní tabulka, vlastní bucket), do katalogu nikdy |
| sdílení | výtvor jde objednat k tisku; veřejný odkaz ve v1 není |

## 3. Uchování a smazání

- Nahraná fotka a výtvory bez objednávky se smažou **30 dní** po posledním
  použití (návrh z plánu, potvrdit).
- S objednávkou se drží po dobu nutnou pro výrobu a reklamaci, pak se
  smažou; doklad o objednávce zůstává podle účetních předpisů (bez obrázku).
- Smazání na žádost kdykoli: kaskádou v databázi, v úložišti (`uploads/`,
  `masters/`), v enginu tvorby a ve vstupní a výstupní složce ComfyUI.
  Fáze 3 je hotová, až to test prokáže.
- Odkazy na soukromé soubory jsou podepsané a krátce platné; tokeny se
  nelogují.

## 4. Zakázaný obsah (katalog i tvorba)

- sexuální obsah a nahota jakéhokoli druhu,
- cokoli s nezletilými (galerie má trvalý blok; tvorba ve v1 lidi nebere vůbec),
- skutečné osoby a jejich podoba,
- násilí, krutost na zvířatech, nenávistné symboly,
- cizí ochranné známky, loga, postavy a díla chráněná autorským právem,
- obsah zavádějící jako skutečná fotografie události (deepfake).

## 5. Otázky na právníka

1. Obchodní podmínky: prodej tisku a tiskových dat z AI obrázku; co zákazník
   získává (licence k tiskovým datům, rozsah).
2. Zboží na míru a výjimka z odstoupení od smlouvy; reklamace tisku.
3. Povinnost označovat AI obsah (AI Act, čl. 50) a forma označení.
4. GDPR u nahraných fotek: právní titul, lhůty, zpracovatelé (úložiště, výroba).
5. Podmínky z licence SDXL (Příloha A OpenRAIL++-M), pokud se SDXL použije:
   jak je převzít do podmínek.
6. Odpovědnost za obsah nahraný uživatelem a postup oznámení a odstranění
   (DSA).
7. Ceny pro ČR a SK, DPH, doklady (R11).
