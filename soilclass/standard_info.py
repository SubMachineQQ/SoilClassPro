from typing import Dict, List, TypedDict

from .i18n import get_language


class StandardInfo(TypedDict, total=False):
    label: str
    standard: str
    tests: List[str]
    inputs: List[str]
    notes: List[str]


STANDARD_INFO: Dict[str, StandardInfo] = {
    "ASTM": {
        "label": "ASTM \u2014 USCS",
        "standard": "ASTM D2487 (Standard Practice for Classification of "
                    "Soils for Engineering Purposes, Unified Soil "
                    "Classification System). Descends from Casagrande's "
                    "Airfield Classification System (1942); the companion "
                    "field/visual method is ASTM D2488.",
        "tests": [
            "Sieve analysis (ASTM D6913), washed over the 0.075 mm "
            "(No.200) sieve",
            "Hydrometer analysis (ASTM D7928), optional \u2014 extends "
            "the curve below 0.075 mm",
            "Atterberg limits (ASTM D4318) on the fraction passing "
            "0.425 mm (No.40) \u2014 Casagrande cup + rolling-thread PL",
            "Visual-manual identification (ASTM D2488) to flag organic "
            "(OL/OH) or highly organic (Pt) soils",
        ],
        "inputs": [
            "Percent passing the 4.75 mm (No.4) and 0.075 mm (No.200) "
            "sieves",
            "The full grain-size curve, for D10/D30/D60, Cu and Cc "
            "(needed only when fines < 12 %)",
            "Liquid Limit (LL) and Plastic Limit (PL) of the -No.40 "
            "fraction (needed when fines >= 5 %)",
            "Organic-soil flag \u2014 oven-dried LL less than 75 % of "
            "natural LL",
        ],
        "notes": [
            "Fines >= 50 % \u2192 fine-grained, classified on the "
            "Casagrande plasticity chart (A-line, LL = 50 split); "
            "fines < 50 % \u2192 coarse-grained, split further into "
            "gravel or sand by whichever dominates the +No.200 fraction.",
            "Dual symbols (e.g. SW-SM) apply only in the 5-12 % fines "
            "band \u2014 below 5 % grading alone decides W/P, above "
            "12 % the fines' plasticity decides M/C.",
        ],
    },
    "BS": {
        "label": "British Standard \u2014 BS 5930",
        "standard": "BS 5930:2015 (Code of Practice for Ground "
                    "Investigations), British Soil Classification System "
                    "(BSCS). Description follows BS EN ISO 14688; the "
                    "classification symbols themselves remain BS-specific.",
        "tests": [
            "Sieve analysis (BS EN ISO 17892-4 / BS 1377-2)",
            "Atterberg limits (BS EN ISO 17892-12) \u2014 fall-cone "
            "method, preferred over the Casagrande cup",
            "Visual description of colour, structure and organic "
            "content (BS EN ISO 14688-1)",
        ],
        "inputs": [
            "Percent passing the 2.0 mm and 0.063 mm sieves",
            "The full grain-size curve, for Cu and Cc (coarse soils, "
            "fines < 5 %)",
            "Liquid Limit (LL) and Plastic Limit (PL)",
        ],
        "notes": [
            "Size boundaries differ from ASTM: fines/sand split at "
            "0.063 mm (not 0.075 mm), sand/gravel at 2.0 mm (not "
            "4.75 mm) \u2014 the same sample can carry a different "
            "fines percentage under each standard.",
            "The coarse/fine threshold is 35 % fines (not USCS's "
            "50 %); grading needs Cu >= 4 for gravel or Cu >= 6 for "
            "sand \u2014 the same split USCS uses.",
            "Five plasticity bands (L/I/H/V/E) instead of USCS's two "
            "(L/H) give a finer split of high-plasticity clays and "
            "silts.",
        ],
    },
    "ISO14688": {
        "label": "TS EN ISO 14688 \u2014 ESCS",
        "standard": "TS EN ISO 14688-1 / -2 (Geotechnical investigation and "
                    "testing \u2014 Identification and classification of "
                    "soil), the Turkish adoption of EN ISO 14688. "
                    "ISO 14688-2 fixes the principles "
                    "(size fractions, grading, plasticity); the group "
                    "symbols used here follow the application scheme of "
                    "Kova\u010devi\u0107, Juri\u0107-Ka\u0107uni\u0107, "
                    "Libri\u0107 & Ivo\u0161 (2018), Gra\u0111evinar 70(10), "
                    "873\u2013879 (European Soil Classification System, "
                    "ESCS).",
        "tests": [
            "Sieve analysis (TS EN ISO 17892-4), washed over the "
            "0.063 mm sieve",
            "Atterberg limits (TS EN ISO 17892-12) \u2014 fall-cone method",
            "Organic content, by visual description (TS EN ISO 14688-1)",
        ],
        "inputs": [
            "Percent passing the 2.0 mm and 0.063 mm sieves",
            "The full grain-size curve, for Cu and Cc (coarse soils)",
            "Liquid Limit (LL) and Plasticity Index (PI) (needed when "
            "fines >= 5 %)",
        ],
        "notes": [
            "Size boundaries: gravel 2.0\u201363 mm, sand "
            "0.063\u20132.0 mm, fines < 0.063 mm. Soil is coarse when "
            "more than 50 % is retained on 0.063 mm.",
            "Symbols are Gr / Sa / Si / Cl for the main fraction, with "
            "lower-case prefixes for the secondary fractions (clSa = "
            "clayey SAND, saClM = sandy medium-plasticity CLAY) and a "
            "grading letter W / M / P / U / G for clean and slightly "
            "fine coarse soils.",
            "Fine soils use four plasticity classes \u2014 L, M, H, V at "
            "LL = 35, 50 and 70 % \u2014 and the A-line separates clay "
            "from silt. Below PI = 4 the soil is silt; between PI = 4 and "
            "7 above the A-line it is silty clay (ClL-SiL).",
            "ISO 14688-2 itself gives no complete symbol set, so limits "
            "the paper leaves open (inclusive ends of ranges, sand and "
            "gravel shares taken on the whole sample) are documented in "
            "the decision trail.",
        ],
    },
    "RSCS": {
        "label": "RSCS \u2014 Park & Santamarina",
        "standard": "Revised Soil Classification System. Park & Santamarina "
                    "(2017), JGGE 143(8); implementation after Castro, Park & "
                    "Santamarina (2023), JGGE 149(11). Fines classification "
                    "after Jang & Santamarina (2016), JGGE 142(4). Void "
                    "ratios from roundness R and Cu follow Cho, Dodds & "
                    "Santamarina (2006), JGGE 132(5), 591\u2013602.",
        "tests": [
            "Sieve analysis \u2014 sieves #4 (4.75 mm) and #200 (0.075 mm)",
            "Maximum and minimum void ratio of the gravel (ASTM D4253 / "
            "D4254) \u2014 or particle roundness R and Cu instead",
            "Maximum and minimum void ratio of the sand \u2014 or R and Cu",
            "Liquid Limit of the fines, fall cone, on material passing #200",
            "Optional: Liquid Limit with 2-M NaCl brine and with kerosene, "
            "for the fines classification",
        ],
        "inputs": [
            "Gravel, sand and fines percentages",
            "Gravel e_max / e_min  (or roundness R and Cu)",
            "Sand e_max / e_min  (or roundness R and Cu)",
            "Liquid Limit with deionized water, LL_dw",
            "Optional: LL_brine and LL_kerosene \u2192 electrical "
            "sensitivity S_E and the 12 fines groups (NL \u2026 HH)",
        ],
        "notes": [
            "Boundaries are soil-specific: they move with particle shape, "
            "gradation and the plasticity of the fines.",
            "Atterberg limits are run on material passing #200, not #40 as "
            "in the USCS \u2014 archival data cannot be used directly.",
            "Measuring LL with 2-M NaCl brine and with kerosene as well "
            "adds the fines' electrical sensitivity S_E, giving a "
            "two-letter fines group (e.g. F(F)-IL) and unlocking the two "
            "fines-classification charts. Without them the soil still "
            "classifies \u2014 just without that suffix.",
        ],
    },
    "AASHTO": {
        "label": "AASHTO \u2014 M 145",
        "standard": "AASHTO M 145 / ASTM D3282 (Classification of Soils "
                    "and Soil-Aggregate Mixtures for Highway Construction "
                    "Purposes). Developed in 1929 for subgrade rating; "
                    "still the basis of most pavement design guides.",
        "tests": [
            "Sieve analysis to the No.10 (2.00 mm), No.40 (0.425 mm) "
            "and No.200 (0.075 mm) sieves",
            "Atterberg limits (ASTM D4318) on the -No.40 fraction",
        ],
        "inputs": [
            "Percent passing the 2.00 mm, 0.425 mm and 0.075 mm sieves",
            "Liquid Limit (LL) and Plasticity Index (PI)",
        ],
        "notes": [
            "Groups run A-1 (best subgrade) to A-7 (poorest); the "
            "Group Index (0-20, shown in parentheses after the symbol) "
            "further ranks soils within a group.",
            "Granular soils (<= 35 % passing No.200) sort into "
            "A-1/A-2/A-3; silt-clay soils (> 35 %) into A-4 through "
            "A-7, split by LL and by whether PI is above or below "
            "LL - 30 (A-7-5 vs A-7-6).",
            "Rates subgrade suitability for roads, not general "
            "engineering behaviour \u2014 a soil's USCS symbol and its "
            "AASHTO group commonly disagree in emphasis, not just "
            "notation.",
        ],
    },
}


STANDARD_INFO_TR: Dict[str, StandardInfo] = {
    "ASTM": {
        "label": "ASTM \u2014 USCS",
        "standard": "ASTM D2487 (M\u00fchendislik Ama\u00e7l\u0131 Zemin "
                    "S\u0131n\u0131fland\u0131rmas\u0131 \u0130\u00e7in "
                    "Standart Uygulama, Birle\u015ftirilmi\u015f Zemin "
                    "S\u0131n\u0131fland\u0131rma Sistemi). "
                    "Casagrande'nin Havaalan\u0131 S\u0131n\u0131fland\u0131rma "
                    "Sistemi'nden (1942) t\u00fcremi\u015ftir; e\u015flik "
                    "eden g\u00f6rsel/manuel y\u00f6ntem ASTM D2488'dir.",
        "tests": [
            "Elek analizi (ASTM D6913), 0,075 mm (No.200) elekten y\u0131kanarak",
            "Hidrometre analizi (ASTM D7928), opsiyonel \u2014 e\u011friyi "
            "0,075 mm alt\u0131na uzat\u0131r",
            "Atterberg limitleri (ASTM D4318), 0,425 mm (No.40) elekten "
            "ge\u00e7en k\u0131s\u0131mda \u2014 Casagrande kab\u0131 + "
            "yuvarlama ipli\u011fi ile PL",
            "G\u00f6rsel-manuel tan\u0131mlama (ASTM D2488), organik "
            "(OL/OH) veya y\u00fcksek organik (Pt) zeminleri belirlemek "
            "i\u00e7in",
        ],
        "inputs": [
            "4,75 mm (No.4) ve 0,075 mm (No.200) elekten ge\u00e7en y\u00fczdeler",
            "Tam dane da\u011f\u0131l\u0131m e\u011frisi, D10/D30/D60, Cu "
            "ve Cc i\u00e7in (sadece ince dane < %12 oldu\u011funda "
            "gerekli)",
            "-No.40 fraksiyonunun Likit Limiti (LL) ve Plastik Limiti "
            "(PL) (ince dane >= %5 oldu\u011funda gerekli)",
            "Organik zemin bayra\u011f\u0131 \u2014 f\u0131r\u0131nda "
            "kurutulmu\u015f LL, do\u011fal LL'nin %75'inden az",
        ],
        "notes": [
            "\u0130nce dane >= %50 \u2192 ince daneli, Casagrande "
            "plastisite grafi\u011finde s\u0131n\u0131fland\u0131r\u0131l\u0131r "
            "(A-hatt\u0131, LL = 50 ayr\u0131m\u0131); ince dane < %50 "
            "\u2192 iri daneli, +No.200 fraksiyonuna hakim olan \u00e7ak\u0131l "
            "veya kuma g\u00f6re ayr\u0131l\u0131r.",
            "\u0130kili semboller (\u00f6rn. SW-SM) sadece %5-12 ince "
            "dane band\u0131nda ge\u00e7erlidir \u2014 %5 alt\u0131nda "
            "sadece derecelenme W/P'yi, %12 \u00fcst\u00fcnde ince "
            "danenin plastisitesi M/C'yi belirler.",
        ],
    },
    "BS": {
        "label": "\u0130ngiliz Standard\u0131 \u2014 BS 5930",
        "standard": "BS 5930:2015 (Zemin Ara\u015ft\u0131rmalar\u0131 "
                    "Uygulama Kodu), \u0130ngiliz Zemin S\u0131n\u0131fland\u0131rma "
                    "Sistemi (BSCS). Tan\u0131mlama BS EN ISO 14688'i "
                    "takip eder; s\u0131n\u0131fland\u0131rma "
                    "sembollerinin kendisi BS'ye \u00f6zg\u00fc kal\u0131r.",
        "tests": [
            "Elek analizi (BS EN ISO 17892-4 / BS 1377-2)",
            "Atterberg limitleri (BS EN ISO 17892-12) \u2014 d\u00fc\u015fen "
            "koni y\u00f6ntemi, Casagrande kab\u0131na tercih edilir",
            "Renk, yap\u0131 ve organik i\u00e7eri\u011fin g\u00f6rsel "
            "tan\u0131m\u0131 (BS EN ISO 14688-1)",
        ],
        "inputs": [
            "2,0 mm ve 0,063 mm elekten ge\u00e7en y\u00fczdeler",
            "Tam dane da\u011f\u0131l\u0131m e\u011frisi, Cu ve Cc i\u00e7in "
            "(iri daneli zeminler, ince dane < %5)",
            "Likit Limit (LL) ve Plastik Limit (PL)",
        ],
        "notes": [
            "Boyut s\u0131n\u0131rlar\u0131 ASTM'den farkl\u0131d\u0131r: "
            "ince dane/kum ayr\u0131m\u0131 0,063 mm'de (0,075 mm de\u011fil), "
            "kum/\u00e7ak\u0131l ayr\u0131m\u0131 2,0 mm'de (4,75 mm de\u011fil) "
            "\u2014 ayn\u0131 numune her standarda g\u00f6re farkl\u0131 "
            "bir ince dane y\u00fczdesi ta\u015f\u0131yabilir.",
            "\u0130ri/ince dane s\u0131n\u0131r\u0131 %35 ince danedir "
            "(USCS'nin %50'si de\u011fil); derecelenme i\u00e7in \u00e7ak\u0131lda "
            "Cu >= 4, kumda Cu >= 6 gerekir \u2014 USCS ile ayn\u0131 ayr\u0131m.",
            "USCS'nin iki band\u0131 (L/H) yerine be\u015f plastisite "
            "band\u0131 (L/I/H/V/E), y\u00fcksek plastisiteli kil ve "
            "siltlerde daha ince bir ayr\u0131m sa\u011flar.",
        ],
    },
    "ISO14688": {
        "label": "TS EN ISO 14688 \u2014 ESCS",
        "standard": "TS EN ISO 14688-1 / -2 (Geoteknik ara\u015ft\u0131rma "
                    "ve deneyler \u2014 Zeminlerin tan\u0131mlanmas\u0131 "
                    "ve s\u0131n\u0131fland\u0131r\u0131lmas\u0131), "
                    "EN ISO 14688'in T\u00fcrk standard\u0131d\u0131r. "
                    "ISO 14688-2 ilkeleri "
                    "belirler (dane boyutu fraksiyonlar\u0131, "
                    "derecelenme, plastisite); burada kullan\u0131lan grup "
                    "sembolleri Kova\u010devi\u0107, Juri\u0107-"
                    "Ka\u0107uni\u0107, Libri\u0107 & Ivo\u0161 (2018), "
                    "Gra\u0111evinar 70(10), 873\u2013879 uygulama "
                    "\u015femas\u0131n\u0131 (Avrupa Zemin "
                    "S\u0131n\u0131fland\u0131rma Sistemi, ESCS) "
                    "izler.",
        "tests": [
            "Elek analizi (TS EN ISO 17892-4), 0,063 mm elekten "
            "y\u0131kanarak",
            "Atterberg limitleri (TS EN ISO 17892-12) \u2014 "
            "d\u00fc\u015fen koni y\u00f6ntemi",
            "Organik madde, g\u00f6zle tan\u0131mlama ile "
            "(TS EN ISO 14688-1)",
        ],
        "inputs": [
            "2,0 mm ve 0,063 mm elekten ge\u00e7en y\u00fczdeler",
            "Tam dane da\u011f\u0131l\u0131m e\u011frisi, Cu ve Cc "
            "i\u00e7in (iri daneli zeminler)",
            "Likit Limit (LL) ve Plastisite \u0130ndisi (PI) (ince dane "
            ">= %5 oldu\u011funda gerekli)",
        ],
        "notes": [
            "Boyut s\u0131n\u0131rlar\u0131: \u00e7ak\u0131l "
            "2,0\u201363 mm, kum 0,063\u20132,0 mm, ince dane < "
            "0,063 mm. 0,063 mm elekte tutulan %50'den fazlaysa zemin "
            "iri daneli say\u0131l\u0131r.",
            "Ana fraksiyon i\u00e7in semboller Gr / Sa / Si / Cl'dir; "
            "ikincil fraksiyonlar k\u00fc\u00e7\u00fck harfli "
            "\u00f6n eklerle yaz\u0131l\u0131r (clSa = killi KUM, "
            "saClM = kumlu orta plastisiteli K\u0130L) ve temiz veya "
            "az ince daneli iri zeminlerde W / M / P / U / G "
            "derecelenme harfi eklenir.",
            "\u0130nce daneli zeminlerde d\u00f6rt plastisite s\u0131n\u0131f\u0131 "
            "vard\u0131r \u2014 LL = %35, 50 ve 70'te L, M, H, V \u2014 "
            "ve A-hatt\u0131 kili siltten ay\u0131r\u0131r. PI < 4 "
            "ise zemin siltir; A-hatt\u0131 \u00fczerinde 4 ile 7 "
            "aras\u0131nda siltli kildir (ClL-SiL).",
            "ISO 14688-2'nin kendisi tam bir sembol seti vermez; "
            "makalenin a\u00e7\u0131k b\u0131rakt\u0131\u011f\u0131 "
            "hususlar (aral\u0131k s\u0131n\u0131rlar\u0131n\u0131n "
            "dahil olmas\u0131, kum ve \u00e7ak\u0131l oranlar\u0131n\u0131n "
            "t\u00fcm numuneye g\u00f6re al\u0131nmas\u0131) karar "
            "izlemesinde belirtilir.",
        ],
    },
    "RSCS": {
        "label": "RSCS \u2014 Park & Santamarina",
        "standard": "Revize Edilmi\u015f Zemin S\u0131n\u0131fland\u0131rma "
                    "Sistemi. Park & Santamarina (2017), JGGE 143(8); "
                    "uygulama Castro, Park & Santamarina'ya (2023) g\u00f6re, "
                    "JGGE 149(11). \u0130nce dane s\u0131n\u0131fland\u0131rmas\u0131 "
                    "Jang & Santamarina'ya (2016) g\u00f6re, JGGE 142(4). "
                    "R ve Cu'dan bo\u015fluk oran\u0131 tahmini Cho, Dodds "
                    "& Santamarina (2006), JGGE 132(5), 591\u2013602 "
                    "\u00e7al\u0131\u015fmas\u0131na dayan\u0131r.",
        "tests": [
            "Elek analizi \u2014 #4 (4,75 mm) ve #200 (0,075 mm) elekleri",
            "\u00c7ak\u0131l\u0131n maksimum ve minimum bo\u015fluk oran\u0131 "
            "(ASTM D4253 / D4254) \u2014 veya bunun yerine dane "
            "yuvarlakl\u0131\u011f\u0131 R ve Cu",
            "Kumun maksimum ve minimum bo\u015fluk oran\u0131 \u2014 veya "
            "R ve Cu",
            "\u0130nce danenin Likit Limiti, d\u00fc\u015fen koni, #200'den "
            "ge\u00e7en malzemede",
            "Opsiyonel: ince dane s\u0131n\u0131fland\u0131rmas\u0131 "
            "i\u00e7in 2-M NaCl tuzlu su ve gazya\u011f\u0131 ile Likit "
            "Limit",
        ],
        "inputs": [
            "\u00c7ak\u0131l, kum ve ince dane y\u00fczdeleri",
            "\u00c7ak\u0131l e_max / e_min (veya yuvarlakl\u0131k R ve Cu)",
            "Kum e_max / e_min (veya yuvarlakl\u0131k R ve Cu)",
            "Deiyonize su ile Likit Limit, LL_dw",
            "Opsiyonel: LL_brine ve LL_kerosene \u2192 elektriksel "
            "duyarl\u0131l\u0131k S_E ve 12 ince dane grubu (NL \u2026 HH)",
        ],
        "notes": [
            "S\u0131n\u0131rlar zemine \u00f6zg\u00fcd\u00fcr: dane "
            "\u015fekli, derecelenme ve ince danenin plastisitesiyle "
            "de\u011fi\u015firler.",
            "Atterberg limitleri, USCS'deki gibi #40'tan de\u011fil "
            "#200'den ge\u00e7en malzemede yap\u0131l\u0131r \u2014 "
            "ar\u015fiv verisi do\u011frudan kullan\u0131lamaz.",
            "LL'yi 2-M NaCl tuzlu su ve gazya\u011f\u0131 ile de \u00f6l\u00e7mek, "
            "ince danenin elektriksel duyarl\u0131l\u0131\u011f\u0131 S_E'yi "
            "ekler; iki harfli bir ince dane grubu (\u00f6rn. F(F)-IL) "
            "verir ve iki ince dane s\u0131n\u0131fland\u0131rma "
            "grafi\u011finin kilidini a\u00e7ar. Bunlar olmadan zemin "
            "yine s\u0131n\u0131fland\u0131r\u0131l\u0131r \u2014 sadece "
            "o ek olmadan.",
        ],
    },
    "AASHTO": {
        "label": "AASHTO \u2014 M 145",
        "standard": "AASHTO M 145 / ASTM D3282 (Karayolu \u0130n\u015faat\u0131 "
                    "Ama\u00e7l\u0131 Zeminlerin ve Zemin-Agrega "
                    "Kar\u0131\u015f\u0131mlar\u0131n\u0131n "
                    "S\u0131n\u0131fland\u0131r\u0131lmas\u0131). 1929'da "
                    "taban zemini derecelendirmesi i\u00e7in geli\u015ftirildi; "
                    "h\u00e2l\u00e2 \u00e7o\u011fu \u00fcstyap\u0131 tasar\u0131m "
                    "k\u0131lavuzunun temelidir.",
        "tests": [
            "No.10 (2,00 mm), No.40 (0,425 mm) ve No.200 (0,075 mm) "
            "eleklerine kadar elek analizi",
            "-No.40 fraksiyonunda Atterberg limitleri (ASTM D4318)",
        ],
        "inputs": [
            "2,00 mm, 0,425 mm ve 0,075 mm elekten ge\u00e7en y\u00fczdeler",
            "Likit Limit (LL) ve Plastisite \u0130ndisi (PI)",
        ],
        "notes": [
            "Gruplar A-1'den (en iyi taban zemini) A-7'ye (en zay\u0131f) "
            "kadar s\u0131ralan\u0131r; Grup \u0130ndisi (0-20, sembolden "
            "sonra parantez i\u00e7inde) grup i\u00e7inde zeminleri daha "
            "da s\u0131ralar.",
            "Gran\u00fcler zeminler (No.200'den ge\u00e7en <= %35) "
            "A-1/A-2/A-3'e; silt-kil zeminler (> %35) LL'ye ve PI'nin "
            "LL - 30'un \u00fcst\u00fcnde mi alt\u0131nda m\u0131 "
            "oldu\u011funa g\u00f6re (A-7-5'e kar\u015f\u0131 A-7-6) A-4 "
            "ile A-7 aras\u0131na ayr\u0131l\u0131r.",
            "Yollar i\u00e7in taban zemini uygunlu\u011funu "
            "derecelendirir, genel m\u00fchendislik davran\u0131\u015f\u0131n\u0131 "
            "de\u011fil \u2014 bir zeminin USCS sembol\u00fc ile AASHTO "
            "grubu, sadece g\u00f6sterimde de\u011fil vurguda da "
            "genellikle farkl\u0131l\u0131k g\u00f6sterir.",
        ],
    },
}


def get_standard_info(key: str) -> StandardInfo:
    table = STANDARD_INFO_TR if get_language() == "tr" else STANDARD_INFO
    return table[key]
