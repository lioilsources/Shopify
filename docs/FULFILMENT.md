# Výroba: POD výrobci a partneři (SlopMarket)

Rešerše k [plánu 02](../Prompts/02-PLAN-imagemarket.md) (R5, R6, §9, fáze 0 krok 5), doručení ČR + SK,
stav webu 16. 11. 2026. Před zapnutím profilu se vše ověří v API výrobce. **(3.)** = cizí zdroj, ne výrobce.

## 1. Výrobci (POD API)

### Gelato
- **API:** REST, klíč v hlavičce. Objednávka (`orderType: order | draft`) nese
  položky s `files[{type, url}]`. URL musí jít stáhnout bez přihlášení.
  Má quote, katalog a webhooky (JSON POST na URL z API portálu, testovací
  notifikace). Samostatný sandbox nenabízí. Testuje se konceptem (`draft`) nebo
  skutečnou objednávkou s unikátní referencí.
  [webhooks](https://developers.gelato.com/docs/webhooks),
  [testovací objednávka](https://connect-support.gelato.com/en/articles/12398334-order-intake-gcw-how-to-place-a-test-order-using-postman)
- **EU výroba:** síť partnerů ve 32 zemích, **včetně Česka, Polska a Německa**.
  Vyrábí se u zákazníka. Gelato uvádí, že lokálně jde ~90 % objednávek
  ([země](https://gelato.com/custom-products), [CZ](https://gelato.com/print-on-demand/czech)).
- **Specifikace:** hrnek 11 oz má tiskovou plochu **200×96 mm**, 15 oz 213×103 mm
  ([mugs](https://support.gelato.com/en/articles/8996273-what-is-the-printable-area-for-mugs)).
  Hrnek 11 oz potřebuje spadávku 2 mm nahoře a dole, ostatní nádobí žádnou
  ([drinkware](https://connect-support.gelato.com/en/articles/9858062-what-print-size-is-required-for-drinkware-production)).
  Plátno: na každou stranu se přidá **ohyb + 15 mm**. Ohyb je 34 mm u slim (2 cm)
  a 40 mm u thick (4 cm), takže plátno 20×30 cm slim potřebuje soubor 298×398 mm
  ([canvas](https://support.gelato.com/en/articles/8996347-how-do-i-upload-my-design-for-a-canvas)).
  Pro tisk na zeď Gelato doporučuje 300 DPI
  ([blog](https://www.gelato.com/au/blog/how-to-print-on-canvas)).
- **Cena:** produkt + doprava. Gelato+ je volitelné předplatné se slevami.
  Podpora uvádí dvě různé ceny, €24 a €119/měs. (Gold), a proto se ověří
  ([plány](https://support.gelato.com/en/articles/8996313-how-much-does-gelato-subscription-cost)).
- **DPH:** Gelato je plátcem DPH v 16 evropských zemích. Daň uvádí na faktuře
  samostatně a s místním DIČ. Sazba záleží na zemi výroby a doručení
  ([daně](https://support.gelato.com/en/articles/8996146-getting-started-with-taxes)).

### Printful
- **API:** REST, v1 a v2 (v2 je místy ještě beta). Objednávka obsahuje položky
  se soubory podle URL a `external_id`. Koncept (draft) se neplatí a nevyrábí,
  dokud nepřijde `POST /orders/{id}/confirm`. Nepovedenou objednávku jde opravit
  a potvrdit znovu. Webhooky v1 posílají `url` a `types`, ale bez vlastních hlaviček,
  takže tajemství musí jít do cesty URL. Sandbox nemá, roli testu hraje koncept.
  [v2 docs](https://developers.printful.com/docs/v2-beta/), [v1](https://developers.printful.com/docs/)
- **EU výroba:** vlastní centra v Rize (LV, textil) a Barceloně (ES). Polské
  Łódź bylo odloženo. Partnerská výroba je mimo EU
  ([centra](https://help.printful.com/hc/en-us/articles/360014067239-Where-are-the-European-fulfillment-centers-located),
  [kde se tiskne](https://support.printful.com/hc/en-us/articles/41396775395729-Where-are-Printful-products-printed)).
  Do ČR a SK se tedy posílá z LV a ES, ne z místa.
- **Specifikace:** DPI 150–300, nad 600 ne
  ([průvodce](https://www.printful.com/graphics-and-embroidery-guide)).
  DTG plocha je 12×16″ a u vybraných produktů se zvětšuje na **15×18″**
  ([blog](https://www.printful.com:443/blog/everything-you-need-to-know-to-prepare-the-perfect-printfile)).
  Herní podložka a desk mat mají **36×18″**, 150+ DPI, **u desk matu 300 DPI**,
  PNG nebo JPEG ([produkt](https://www.printful.com/custom/tech-accessories/personalized/gaming-mouse-pad)).
  Deky chtějí sRGB, PNG nebo JPEG, bez vodítek
  ([deky](https://www.printful.com/custom-blankets)). Hrnek 11 oz má 9×3,5″
  = 2700×1050 px **(3.)** ([teeinblue](https://support.teeinblue.com/en/article/1t5nz1m/)).
  Termohrnek 20 oz má 2776×2374 px **(3.)** ([MyDesigns](https://mydesigns.io/product-catalog/tumblers/product/20oz-stainless-steel-tumbler)).
  Přesné rozměry vrací endpoint printfiles v API pro každou variantu.
- **Cena:** bez měsíčního poplatku, platí se produkt + doprava.
- **DPH:** Printful účtuje DPH u každé objednávky doručené do EU, bez ohledu
  na místo výroby. S platným EU DIČ může být 0 % u přeshraniční dodávky z LV
  nebo ES ([VAT](https://help.printful.com/hc/en-us/articles/360014008620-what-do-i-need-to-do-to-charge-the-correct-vat-rate-)).

### Prodigi
- **API:** REST v4, a podle dokumentace už i v5. Objednávka nese
  `items[].assets[{printArea, url}]` a volitelné `callbackUrl` pro stavové
  callbacky. Má quote a detail produktu.
  **Má skutečný sandbox** (`api.sandbox.prodigi.com/v4.0`, vlastní klíče),
  kde se objednávky nezpracují ani nezaplatí
  ([reference](https://www.prodigi.com/print-api/docs/reference/),
  [první objednávka](https://prodigi.com/blog/your-first-print-api-order)).
- **EU výroba:** vlastní výroba v UK a **Nizozemsku** (kvůli rychlosti do
  kontinentální EU), k tomu 50–70 partnerů v 10+ zemích. Česko mezi nimi
  doložené není ([going dutch](https://prodigi.com/blog/going-dutch)).
- **Specifikace:** ideálně 300 DPI
  ([rozlišení](https://help.prodigi.com/support/solutions/articles/35000138845-what-resolution-do-images-need-to-be-)).
  Plátno na rámu 38 mm potřebuje **+40 mm (1,575″) na každou stranu**. Okraj
  je zrcadlený, černý nebo bílý ([plátna](http://www.prodigi.com/faq/canvases/)).
- **Cena:** bez paušálu, produkt + doprava. Prodigi Pro je volitelný.
- **DPH:** bez platného DIČ účtuje DPH jako spotřebiteli. DIČ se zadává
  v účtu. Zboží z NL je bez dovozních poplatků
  ([EU VAT](https://help.prodigi.com/support/solutions/articles/35000138814-how-does-vat-work-in-the-eu-)).

### Printify
- **API:** REST s tokenem a scope `orders.write`. Obrázky se nahrají přes
  `uploads` (URL nebo base64), produkt nese `print_areas` podle tiskárny.
  Objednávka čeká „On hold“, dokud nepřijde `send_to_production`. Webhooky
  posílají například `order:created`. Sandbox nemá. Tiskovou plochu a pixely
  určuje **každá tiskárna zvlášť**
  ([API](https://developers.printify.com/),
  [objednávky přes API](https://help.printify.com/hc/en-us/articles/4483629894289-How-do-orders-and-products-submitted-through-API-look-like-inside-my-account)).
- **EU výroba:** marketplace tiskáren, mezi nimi **CZ (OPT OnDemand)**, DE
  (Textildruck Europa, Posterflow), PL (HFT71), LV (Ideju Druka, Print Pigeons)
  a NL ([shipping](https://printify.com/shipping-rates/)).
- **Cena:** Free, nebo Premium (~$29/měs., až −20 % na produkty). Cena
  záleží na tiskárně.
- **DPH:** od 10/2021 účtuje DPH na objednávky do EU (OSS). S DIČ z jiné
  země EU platí 0 % a reverse charge řeší obchodník
  ([blog](https://printify.com/blog/winning-european-union-vat-laws-with-printify),
  [VAT](https://help.printify.com/hc/en-us/articles/4483628906513)).

## 2. Pokrytí profilů z 03-USE-CASES

✓ = v katalogu, ? = neověřeno nebo jen u části tiskáren, — = ne (ověřit katalogovým API).

| profil | Gelato | Printful | Prodigi | Printify |
|---|---|---|---|---|
| tričko, mikina (DTG/DTF) | ✓ | ✓ | ✓ | ✓ |
| plakát | ✓ | ✓ | ✓ | ✓ |
| plátno na rámu | ✓ | ✓ | ✓ | ✓ |
| kov, akryl | ✓ | ? | ✓ | ? |
| hrnek | ✓ | ✓ | ✓ | ✓ |
| termohrnek | ? | ✓ | ? | ✓ |
| deka | ? | ✓ | ? | ✓ |
| puzzle | ? | ✓ | ✓ | ✓ |
| desk mat | — | ✓ | ✓ | ✓ |
| samolepky | ? | ✓ | ✓ | ✓ |
| kalendář, přání | ✓ | ? | ✓ | ? |

## 3. Srovnání

| | Gelato | Printful | Prodigi | Printify |
|---|---|---|---|---|
| sandbox | ne (draft) | ne (draft) | **ano** | ne (on hold) |
| soubor podle URL | ano | ano | ano | upload, pak id |
| webhooky | ano | ano | callbackUrl | ano |
| výroba nejblíž CZ/SK | **CZ, PL, DE** | LV, ES | NL, UK | **CZ, PL, DE** (podle tiskárny) |
| jednotné specifikace | ano | ano | ano | ne, liší se tiskárna od tiskárny |
| paušál | volitelný | ne | volitelný | volitelný |
| DPH do EU | lokální registrace | účtuje do EU | podle DIČ | OSS, 0 % s DIČ |

## 4. Doporučení pro zkušební objednávku (R5)

1. **Prodigi sandbox** jako první integrace: celý tok (quote, objednávka,
   callback, opakované odeslání) se dá projet bez peněz.
2. **Gelato** jako hlavní kandidát na výrobu: tiskne v ČR, takže je
   nejkratší doprava a DPH je lokální. Zkušební objednávka: plakát A3, plátno
   40×60, hrnek 11 oz. Doručit na adresu v ČR i v SK.
3. **Printful** pro produkty, které Gelato nemá (desk mat, deka, puzzle):
   jeden desk mat a jedna deka. Změřit dobu doručení z LV/ES.
4. Printify až jako záloha, protože kvalita a specifikace kolísají podle tiskárny.

Měří se: barvy proti sRGB masteru, ostrost po upscalu, doba doručení, cena s DPH a dopravou → R5 v `docs/DECISIONS.md`.

## 5. Kandidáti na partnera velkého formátu (CZ/SK) (R6)

Jen veřejné údaje z webů firem. Data e-mailem nebo formulářem, API nemá nikdo.

| firma | web | co dělá | data | zveřejněné specifikace |
|---|---|---|---|---|
| Tiskni rychle (CZ) | [tisknirychle.cz](https://www.tisknirychle.cz/tisk/jak-pripravit-tiskova-data) | velkoplošný tisk A3–A0, bannery, roll-upy, polepy aut, fotoobrazy, citylight | e-mail | PDF, TIFF/JPG/PNG, CMYK, 1:1 nebo 1:10; 300 dpi zblízka, 70–100 dpi zdálky; spad 3 mm, roll-up 5 mm + 30–50 mm dole, PVC s oky ≥ 10 mm a motiv ≥ 50 mm od kraje, polep ≥ 5 mm |
| SAMOLEPKY.CZ (CZ) | [samolepky.cz](https://samolepky.cz) | digitální tisk, sítotisk, billboardy, bigboardy, plachty, CLV, polepy vozidel | poptávka | na webu nenalezeno |
| US Print (CZ) | [usprint.cz](https://usprint.cz) | velkoformátový tisk, partnerská spolupráce ([e15](https://www.e15.cz/radce/usprint-cz-kdyz-velkoformatovy-tisk-neni-jen-zakazka-ale-partnerstvi-1427706)) | poptávka | ověřit |
| Stonožka (CZ) | [stonozka.cz](http://www.stonozka.cz/jak-dodat-podklady-tisk-plachty/) | reklamní plachty | e-mail | plachta 1:10 při 600 dpi nebo 1:1 při 60 dpi; +3 mm na stranu |
| ColorPoint (CZ) | [colorpoint.cz](https://colorpoint.cz/faq/jak-pripravit-data/) | expresní digitální a velkoformátový tisk | e-mail/web | návod k datům na webu |
| PointPrint (SK) | [pointprint.sk](https://pointprint.sk/tlac-billboardov-a-plagatov) | billboardy (euro, bigboard, megaboard), citylight, bannery, tapety, plátno, roll-upy | e-mail | PDF/AI/PSD, CMYK, billboard 30–50 dpi při finální velikosti, plakát 150–300; spad ≥ 5 mm, ořez jako magenta vrstva, billboard ≥ 10 cm bezpečná zóna |
| Thrillidea (SK) | [thrillidea.sk](https://www.thrillidea.sk/velkoformatova-tlac.html) | billboardy, bannery, plachty, mesh | e-mail | PDF 1:10 při 300 dpi, CMYK, texty v křivkách |
| BK Studio (SK) | [bkstudio.sk](https://www.bkstudio.sk/velkoformatova-tlac) | bannery, roll-upy, fólie, polepy (cast fólie) | e-mail | 100–150 dpi 1:1, detail 200–300; spad 3 mm |

Sklo za linkou a fototapetu ze seznamu nikdo výslovně nedělá. Pro ně je potřeba
samostatný kandidát (sklenářství s UV tiskem, výrobce tapet). Vlastník vybere 1–3
a pošle jim šablonu níže.

## 6. Šablona pro partnera velkého formátu

> Dobrý den, připravujeme obchod s tiskem vlastních motivů (SlopMarket) a hledáme
> partnera pro velký formát v ČR a SK. Prosíme o odpovědi:
>
> 1. **Produkty a formáty:** které produkty (billboard, plachta, mesh, roll-up,
>    citylight, polep vozu, fototapeta, sklo…) a jejich max. šíře role a délka panelu.
> 2. **Rozlišení:** minimální a doporučené DPI při finální velikosti, nebo
>    měřítko (1:1, 1:10). Maximální rozměr souboru v px a v MB.
> 3. **Soubor:** formát (PDF/X-4, TIFF, JPG), barevný prostor (sRGB nebo CMYK),
>    ICC profil, komprese, vrstvy, ořezová křivka.
> 4. **Spadávka a bezpečné zóny:** spad v mm, oka a svary, panely a přesahy,
>    kazeta u roll-upu, okna a lišty u polepu.
> 5. **Korektura:** posíláte digitální náhled nebo barevný nátisk, kolik
>    kol je v ceně, kdo schvaluje.
> 6. **Ceny:** ceník za m² nebo za kus podle materiálu, montáž, doprava, DPH,
>    minimální zakázka, množstevní slevy.
> 7. **Lhůty:** výroba od schválení dat, doprava do ČR a SK, expres.
> 8. **Předání dat:** upload, odkaz ke stažení, FTP, nebo API. Stav zakázky
>    (e-mail, webhook). Fakturace a reklamace.

## 7. Opravy čísel v 03-USE-CASES.md

Do [03-USE-CASES.md](../Prompts/03-USE-CASES.md) se propsaly jen rozdíly doložené výrobcem nebo partnerem.

| řádek | bylo | je | zdroj |
|---|---|---|---|
| tričko | 30×40 cm, 2 400–4 700 px | 30×40 až 38×46 cm, 2 400–5 400 px | Printful 12×16″, nově 15×18″ |
| plátno | ohyb 3–5 cm, 2 400–8 900 px | ohyb 4–5,5 cm na stranu, 2 800–9 500 px | Gelato (34/40 + 15 mm), Prodigi 40 mm |
| hrnek | 20×9 cm, poměr 2,2:1 | 20×9,6 cm + spad 2 mm nahoře a dole (Gelato), poměr 2–2,6:1 podle výrobce, 2 400–2 700 px | Gelato; Printful (3.) |
| desk mat | 90×40 cm, 150–200 DPI, poměr 2,25:1 | 91×46 cm, 150–300 DPI, poměr 2:1, 5 400–10 800 px | Printful 36×18″, 300 DPI |
| banner, plachta | „oka, svary: bezpečná zóna“ | spad ≥ 10 mm, motiv ≥ 50 mm od kraje | Tiskni rychle |
| roll-up | spodních 15 cm v kazetě | spad 5 mm + 30–50 mm dole do kazety | Tiskni rychle |
| samolepky | alfa + ořezová křivka | + spad 2–3 mm | Tiskni rychle |

Beze změny, protože zdroje se shodují nebo chybí: plakát se spadem 3 mm,
billboard 1:10 při 15–40 DPI (PointPrint uvádí 30–50 při finální velikosti),
puzzle (rozměry se liší podle výrobce: 50×70 až 76×51 cm), termohrnek, deka, kov a akryl.
