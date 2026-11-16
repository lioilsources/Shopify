# Licence modelů pro ImageMarket

Podklad pro R7 v `Prompts/02-PLAN-imagemarket.md` (a §14) a pro výběr modelů
v `Prompts/04-PLAN-showcase.md` (§3). ImageMarket prodává tisky obrázků
z AI a placenou službu restylu fotky. U každého modelu proto řešíme dvě
otázky:

- **Výstupy:** smí se prodávat obrázky, které model vytvoří?
- **Provoz:** smí model běžet v placené službě (výroba pro e-shop, restyl
  na objednávku)?

U licencí typu FLUX.1 [dev] to jsou dvě různé otázky. Licence sice dovoluje
komerčně použít výstupy, ale sám provoz modelu za úplatu zakazuje.

**Nejde o právní radu.** Tabulky shrnují veřejné texty licencí a model
cards k 16. 11. 2026. Před spuštěním placeného provozu je potřeba přečíst
plné znění, případně se poradit s právníkem.

Značky jistoty:

- **✔ text:** ověřeno přímo ze znění licence nebo model card.
- **~ odvozeno:** vychází z licence repozitáře nebo z obecného výkladu
  licence a model card to výslovně neuvádí.
- **? nejisté:** zdroje si odporují nebo mlčí.

## 1. Generování

| model | licence | výstupy prodat | provoz za úplatu | zdroj | poznámka |
|---|---|---|---|---|---|
| FLUX.1-schnell | Apache 2.0 | ano ✔ | ano ✔ | [HF](https://huggingface.co/black-forest-labs/FLUX.1-schnell) | Card: „personal, scientific, and commercial purposes“. |
| FLUX.1-dev | FLUX.1 [dev] Non-Commercial License v1.1.1 | ano, s výhradou ✔ | **ne** ✔ | [LICENSE](https://huggingface.co/black-forest-labs/FLUX.1-dev/blob/main/LICENSE.md) | Viz rozbor pod tabulkou. |
| FLUX.1 Kontext dev | stejná licence jako FLUX.1-dev | ano, s výhradou ✔ | **ne** ✔ | [HF](https://huggingface.co/black-forest-labs/FLUX.1-Kontext-dev) | Card odkazuje na licenci FLUX.1 [dev]. |
| FLUX.1 Fill dev | stejná licence jako FLUX.1-dev | ano, s výhradou ✔ | **ne** ✔ | [HF](https://huggingface.co/black-forest-labs/FLUX.1-Fill-dev) | Totéž. Platí i pro odvozeniny (LoRA, manga apod.). |
| Qwen-Image | Apache 2.0 | ano ✔ | ano ✔ | [HF](https://huggingface.co/Qwen/Qwen-Image) | Odpovídá ověření vlastníka. |
| Qwen-Image-Edit (i 2509, 2511) | Apache 2.0 | ano ✔ | ano ✔ | [HF](https://huggingface.co/Qwen/Qwen-Image-Edit), [2511](https://huggingface.co/Qwen/Qwen-Image-Edit-2511) | Tag je `apache-2.0`. Sekce o licenci jmenuje jen „Qwen-Image“, ale to je jen šablona textu. |
| FLUX.2 klein 4B | Apache 2.0 | ano ✔ | ano ✔ | [HF](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B) | Card: „available for commercial use under the Apache 2.0 license“. **Pozor:** klein 9B má nekomerční licenci. |
| FLUX.2 dev | FLUX Non-Commercial License v2.1 | ano, s výhradou ✔ | **ne** ✔ | [LICENSE](https://huggingface.co/black-forest-labs/FLUX.2-dev/blob/main/LICENSE.md) | Stejná konstrukce jako u FLUX.1-dev, výslovně vylučuje „revenue-generating activity“. |
| Z-Image-Turbo | Apache 2.0 | ano ✔ | ano ✔ | [HF](https://huggingface.co/Tongyi-MAI/Z-Image-Turbo) | Card uvádí jen tag. Platí běžné podmínky Apache 2.0. |
| SDXL base 1.0 | CreativeML OpenRAIL++-M | ano ✔ | ano, s podmínkami ✔ | [LICENSE](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/blob/main/LICENSE.md) | Viz rozbor pod tabulkou. |
| Illustrious XL | Fair AI Public License 1.0-SD | ano ✔ | ano, s podmínkami ~ | [HF](https://huggingface.co/OnomaAIResearch/Illustrious-xl-early-release-v0), [FAIPL](https://freedevproject.org/faipl-1.0-sd/) | Výstupy licence nepokrývá. Kdo upravený model (finetune, merge, LoRA vpečená do vah) nabízí uživatelům přes síť, musí jim zpřístupnit i váhy. Card navíc „discourages“ monetizaci. Verze v0.1 je podle card „research-only“. |

**FLUX.1-dev a stejně licencované modely (Kontext, Fill, FLUX.2 dev):**

- Odstavec 2(d) o výstupech: „You may use Output for any purpose (including
  for commercial purposes)“. Zakazuje ale výstupy používat k tréninku,
  doladění nebo destilaci modelu, který by FLUX konkuroval.
- Odstavec 1(c) přitom dovoluje jen nekomerční účel a ten končí, jakmile
  plyne „any direct or indirect payment arising from the use“. Výroba
  obrázků na prodej je takovou platbou, takže samotný provoz licenci
  porušuje. Výstupy z nedovoleného provozu tak volné nejsou.
- Doložka o vyhodnocení, 1(c)(ii): firma smí model používat „for testing,
  evaluation, or non-commercial research and development in a non-production
  environment“. Srovnání v plánu 04 jako laťka je tedy v pořádku ✔.
  Obrázky ze srovnání ale nesmějí jít do výlohy ani do prodeje ~.
- Pro placený provoz nabízí BFL komerční licenci nebo vlastní API (FLUX
  [pro]). Cenu je třeba zjistit ?.

**SDXL base 1.0:**

- Licence nedělá žádný nárok na výstupy („Licensor claims no rights in the
  Output“).
- Výslovně dovoluje hostovanou službu („software-as-a-service“).
- Podmínka: omezení z Přílohy A se musí převzít jako vymahatelné ustanovení
  do podmínek služby. Patří mezi ně zákaz škodit nezletilým, šířit osobní
  údaje, pomlouvat a provádět automatizovaná rozhodnutí s právním dopadem.
  ImageMarket je proto musí mít v obchodních podmínkách.
- Komunitní checkpointy odvozené od SDXL mohou mít vlastní, přísnější
  licenci. Každý je třeba zkontrolovat zvlášť ?.

## 2. Zachování tváře

| model | licence | výstupy prodat | provoz za úplatu | zdroj | poznámka |
|---|---|---|---|---|---|
| InsightFace (antelopev2, buffalo_l) | kód MIT, **modely jen pro nekomerční výzkum** | ne ~ | **ne** ✔ | [GitHub](https://github.com/deepinsight/insightface) | Znění: „available for non-commercial research purposes only“. Pravidlo platí i pro modely, které stáhne pip balík. Komerční licenci nabízí InsightFace na vyžádání (kontakt je v README repozitáře). |
| InstantID | Apache 2.0 (vlastní váhy) | jen bez InsightFace ✔ | jen bez InsightFace ✔ | [HF](https://huggingface.co/InstantX/InstantID) | Za běhu potřebuje antelopev2, takže v praxi **ne**. |
| PuLID / PuLID-FLUX | Apache 2.0 (kód i váhy) | viz poznámka | **ne** ~ | [GitHub](https://github.com/ToTheBeginning/PuLID), [HF](https://huggingface.co/guozinan/PuLID) | Používá InsightFace (detekce a embedding tváře). Varianta PuLID-FLUX navíc běží na FLUX.1-dev, takže jsou tu dvě nekomerční závislosti. |
| IP-Adapter FaceID | bez SPDX tagu, výslovně **jen výzkum** | ne ✔ | **ne** ✔ | [HF](https://huggingface.co/h94/IP-Adapter-FaceID) | Znění: „released exclusively for research purposes and is not intended for commercial use“. Závisí také na InsightFace. |

Nejasná zůstává jedna věc: zda omezení modelu InsightFace „přechází“ i na
výsledný obrázek ?. Pro provoz to nerozhoduje, protože placená služba je
sama komerčním použitím modelu ✔.

## 3. Zvětšení

| model | licence | výstupy prodat | provoz za úplatu | zdroj | poznámka |
|---|---|---|---|---|---|
| Real-ESRGAN (x4plus, anime) | BSD-3-Clause | ano ~ | ano ~ | [GitHub](https://github.com/xinntao/Real-ESRGAN) | Licence repozitáře. Váhy z releases vlastní licenci neuvádějí. |
| 4x-UltraSharp (i V2) | CC BY-NC-SA 4.0 | **ne** ~ | **ne** ✔ | [OpenModelDB](https://openmodeldb.info/models/4x-UltraSharp), [diskuse](https://huggingface.co/Kim2091/UltraSharp/discussions/4) | Autor (Kim2091) píše, že výstupy podle něj „probably can't be used commercially“. Za výjimku je třeba autorovi napsat. |
| DAT | Apache 2.0 | ano ~ | ano ~ | [GitHub](https://github.com/zhengchen1999/DAT) | Licence repozitáře. Trénováno na DF2K, kde je DIV2K dataset pro akademické použití. Na váhy se to ale obvykle nevztahuje ?. |
| HAT | Apache 2.0 | ano ~ | ano ~ | [GitHub](https://github.com/XPixelGroup/HAT) | Totéž co DAT. |
| SeedVR2 (3B/7B) | Apache 2.0 | ano ✔ | ano ✔ | [HF](https://huggingface.co/ByteDance-Seed/SeedVR2-3B) | Card: „SeedVR and SeedVR2 are licensed under the Apache 2.0“. Port pro ComfyUI (numz) je pod MIT, resp. Apache. |
| ControlNet Tile SDXL (xinsir) | Apache 2.0 | ano ✔ | ano ✔ | [HF](https://huggingface.co/xinsir/controlnet-tile-sdxl-1.0) | Běží na SDXL, takže platí i podmínky OpenRAIL++. |

## 4. Detektory a pomocné modely

Tyto modely nic do obrázku nevkládají. Proto u nich rozhoduje jen provoz.

| model | licence | provoz za úplatu | zdroj | poznámka |
|---|---|---|---|---|
| NudeNet | AGPL-3.0 | ano, s podmínkami ~ | [GitHub](https://github.com/notAI-tech/NudeNet) | AGPL. Pokud se kód nemění a uživatel s ním přímo nekomunikuje (jen interní filtr), riziko je nízké. Úpravy, se kterými uživatelé komunikují přes síť, by se musely zveřejnit. Váhy jsou v balíku bez zvláštní licence ?. |
| WD14 tagger (SmilingWolf v3) | Apache 2.0 | ano ✔ | [HF](https://huggingface.co/SmilingWolf/wd-eva02-large-tagger-v3) | Starší verze (v2) zkontrolovat zvlášť ?. |
| SigLIP 2 | Apache 2.0 | ano ✔ | [HF](https://huggingface.co/google/siglip2-so400m-patch14-384) | |
| bge-m3 | MIT | ano ✔ | [HF](https://huggingface.co/BAAI/bge-m3) | |
| BiRefNet | MIT | ano ✔ | [HF](https://huggingface.co/ZhengPeng7/BiRefNet) | Doporučená náhrada za RMBG pro odstranění pozadí. |
| RMBG-1.4 (BRIA) | bria-rmbg-1.4, **nekomerční** | **ne** ✔ | [HF](https://huggingface.co/briaai/RMBG-1.4) | Card: „source-available model for non-commercial use“. Komerční použití jen po smlouvě s BRIA. |
| RMBG-2.0 (BRIA) | CC BY-NC 4.0 | **ne** ✔ | [HF](https://huggingface.co/briaai/RMBG-2.0) | Card: „open source for non commercial use only“. Komerčně jen přes placenou licenci nebo BRIA API. |

## 5. Co zůstává neověřené

- Cena a podmínky komerční licence BFL (FLUX.1-dev, Kontext, Fill) a
  InsightFace.
- Konkrétní komunitní checkpointy SDXL a Illustrious, které lab používá.
  Každý má vlastní licenci na Civitai nebo HF.
- Licence vah Real-ESRGAN, DAT a HAT. Známe jen licenci repozitářů.
- Zda nekomerční licence modelu (InsightFace, UltraSharp) omezuje i
  výstupy. Výklad se liší a autor UltraSharp se kloní k tomu, že ano.

## Závěr pro R7

- **Do výroby smí:** FLUX.1-schnell, Qwen-Image, Qwen-Image-Edit,
  FLUX.2 klein 4B, Z-Image-Turbo, SeedVR2, ControlNet Tile (xinsir),
  SigLIP 2, bge-m3, WD14 v3 a BiRefNet.
- **S podmínkami:**
  - SDXL base 1.0: omezení z Přílohy A musí být v obchodních podmínkách.
  - Illustrious: upravené váhy nabízené přes síť se musí zveřejnit.
    Raději se mu vyhnout.
  - NudeNet: AGPL, jen jako interní filtr bez úprav.
  - Real-ESRGAN, DAT a HAT: licence vah ověřená jen nepřímo.
- **Ven (bez koupené licence):**
  - FLUX.1-dev, Kontext dev, Fill dev, FLUX.2 dev, FLUX.2 klein 9B: provoz
    za úplatu zakázán. Ve srovnání smí zůstat jen jako laťka v neprodukčním
    prostředí.
  - 4x-UltraSharp, RMBG-1.4 a RMBG-2.0.
- **Zachování tváře:** všechny tři cesty (InstantID, PuLID, IP-Adapter
  FaceID) stojí na InsightFace, který má modely jen pro nekomerční výzkum.
  FaceID je navíc sám jen pro výzkum a PuLID-FLUX běží na FLUX.1-dev.
  **Placený restyl z fotky se zachováním tváře nespouštět**, dokud nebude
  jedno z tohoto:
  - koupená licence InsightFace,
  - face embedder s komerční licencí,
  - restyl bez identitního adaptéru (např. Qwen-Image-Edit nebo FLUX.2
    klein 4B s referenční fotkou, Apache 2.0). Kvalitu zachování tváře
    je třeba změřit.
