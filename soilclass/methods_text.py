from __future__ import annotations

from typing import Dict, List, Tuple

from .i18n import get_language

Block = Tuple[str, object]

_TR: List[Tuple[str, List[Block]]] = [
    ("Genel", [
        ("h1", "Genel hesaplar"),
        ("p", "Bu bölüm, beş sınıflandırma sisteminin ortak olarak kullandığı "
              "girdi kontrollerini ve dane dağılımı hesaplarını açıklar. Her "
              "sistemin kendi kuralları ayrı sekmelerde verilmiştir."),
        ("h2", "Girdi kontrolleri"),
        ("b", "En az iki elek noktası gerekir. Elek açıklığı sıfırdan büyük, "
              "geçen yüzde 0–100 arasında olmalıdır."),
        ("b", "Elek açıklığı küçüldükçe geçen yüzde artamaz; artış varsa "
              "sınıflandırma yapılmaz ve ilgili satırlar gösterilir."),
        ("b", "Likit limit (LL) ve plastik limit (PL) 0–600 arasında olmalı ve "
              "PL, LL'den büyük olmamalıdır."),
        ("b", "\"Plastik değil (NP)\" işaretlendiğinde LL ve PL kullanılmaz; "
              "zemin plastik olmayan kabul edilir."),
        ("h2", "Plastisite indisi"),
        ("f", "PI = LL − PL      (negatif çıkarsa PI = 0 alınır)"),
        ("h2", "Dane dağılımı eğrisi"),
        ("p", "Elek verisi, dane boyutunun 10 tabanında logaritmasına karşı "
              "geçen yüzde olarak ele alınır. Noktalar arasındaki değerler "
              "monoton parçalı kübik Hermite interpolasyonu (PCHIP) ile "
              "hesaplanır. Bu yöntem eğriyi ölçülen noktalardan geçirir ve "
              "noktalar arasında yapay tepe veya çukur oluşturmaz."),
        ("b", "Aynı açıklık iki kez girilmişse iki geçen yüzdenin ortalaması "
              "kullanılır."),
        ("b", "İstenen boyut ölçülen aralığın dışındaysa en yakın uçtaki geçen "
              "yüzde kullanılır (örneğin en küçük elek 0,075 mm'den büyükse "
              "ince dane oranı, en küçük elekteki geçen yüzdeye eşit alınır)."),
        ("b", "Grafiklerde eğri, ölçülen aralığın dışına uç eğimiyle "
              "logaritmik eksende doğrusal olarak uzatılır. Bu uzatma yalnızca "
              "çizim içindir; sınıflandırmada kullanılmaz."),
        ("h2", "Karakteristik dane çapları ve derecelenme"),
        ("p", "D10, D30 ve D60, eğri üzerinde sırasıyla %10, %30 ve %60 geçen "
              "değerine karşılık gelen dane çaplarıdır ve eğrinin tersine "
              "çözülmesiyle (ikiye bölme yöntemi) bulunur. İstenen yüzde "
              "ölçülen aralıkta değilse ilgili çap hesaplanmaz."),
        ("f", "Cu = D60 / D10\nCc = D30² / (D10 · D60)"),
        ("p", "D10 bulunamazsa Cu ve Cc hesaplanamaz; her sistemin bu durumda "
              "ne yaptığı kendi sekmesinde belirtilmiştir."),
        ("h2", "Fraksiyonlar"),
        ("p", "Çakıl, kum ve ince dane yüzdeleri eğri üzerinden iki sınır "
              "boyuttaki geçen yüzdelerden hesaplanır:"),
        ("f", "İnce dane = P(sınır kum/ince)\n"
              "Kum      = P(sınır çakıl/kum) − P(sınır kum/ince)\n"
              "Çakıl    = 100 − P(sınır çakıl/kum)"),
        ("t", [("Sistem", "Çakıl / kum sınırı", "Kum / ince sınırı"),
               ("USCS (ASTM D2487)", "4,75 mm (No. 4)", "0,075 mm (No. 200)"),
               ("BS 5930", "2,0 mm", "0,063 mm"),
               ("TS EN ISO 14688", "2,0 mm", "0,063 mm"),
               ("AASHTO M 145", "2,0 mm (No. 10)", "0,075 mm (No. 200)"),
               ("RSCS", "4,75 mm (No. 4)", "0,075 mm (No. 200)")]),
        ("h2", "A-hattı ve U-hattı"),
        ("f", "A-hattı: PI = 0,73 · (LL − 20)\nU-hattı: PI = 0,9 · (LL − 8)"),
        ("p", "A-hattı USCS, BS 5930 ve TS EN ISO 14688'de kil/silt ayrımında "
              "kullanılır. U-hattı yalnızca plastisite grafiğinde üst sınır "
              "olarak çizilir; sınıflandırma kararlarında kullanılmaz."),
    ]),
    ("USCS", [
        ("h1", "USCS — ASTM D2487"),
        ("p", "Birleştirilmiş Zemin Sınıflandırma Sistemi. Fraksiyonlar 4,75 mm "
              "(No. 4) ve 0,075 mm (No. 200) sınırlarıyla hesaplanır."),
        ("h2", "1. İri / ince daneli ayrımı"),
        ("b", "İnce dane ≥ %50 → ince daneli zemin."),
        ("b", "İnce dane < %50 → iri daneli zemin."),
        ("h2", "2. İnce dane sembolü"),
        ("b", "Organik işaretliyse: LL < 50 → OL, LL ≥ 50 → OH."),
        ("b", "LL < 50: PI > 7 ve PI ≥ A-hattı → CL; PI < 4 veya PI < A-hattı "
              "→ ML; diğer durumlar (4 ≤ PI ≤ 7, A-hattı üzerinde/üstünde) → "
              "CL-ML."),
        ("b", "LL ≥ 50: PI ≥ A-hattı → CH; aksi halde MH."),
        ("b", "LL veya PI yoksa ince daneler siltli (ML) kabul edilir ve karar "
              "izlemesinde belirtilir."),
        ("h2", "3. İnce daneli zeminin adı"),
        ("p", "Grup adları: CL yağsız kil, ML silt, CH yağlı kil, MH elastik "
              "silt, CL-ML siltli kil, OL/OH organik silt/kil. İri dane oranı "
              "(kum + çakıl):"),
        ("b", "%15–30 → \"kumlu\" veya \"çakıllı\" eki (hangisi büyükse; eşitse "
              "kum)."),
        ("b", "≥ %30 → ad \"Kumlu …\" ya da \"Çakıllı …\" olarak başlar."),
        ("h2", "4. İri daneli zemin"),
        ("b", "Çakıl > kum → G (çakıl), aksi halde S (kum)."),
        ("b", "İyi derecelenmiş (W): çakılda Cu ≥ 4, kumda Cu ≥ 6 ve "
              "1 ≤ Cc ≤ 3. Bu koşul sağlanmazsa veya Cu/Cc hesaplanamazsa kötü "
              "derecelenmiş (P)."),
        ("t", [("İnce dane", "Sembol", "Örnek"),
               ("< %5", "GW, GP, SW, SP", "İyi derecelenmiş kum"),
               ("%5–12", "Çift sembol", "SP-SM, GW-GC"),
               ("> %12", "GM, GC, SM, SC", "Killi kum")]),
        ("b", "İnce danenin türü 2. adımdaki kuralla belirlenir: CL/CH → C; "
              "ML/MH/OL/OH → M. CL-ML ince daneler %12'nin üstünde GC-GM veya "
              "SC-SM, %5–12 arasında M olarak işlenir."),
        ("b", "Diğer iri fraksiyon ≥ %15 ise ada \"çakıllı\" ya da \"kumlu\" "
              "niteleyicisi eklenir."),
        ("h2", "Notlar"),
        ("b", "Organik iri daneli zeminlerde ince dane türü M olarak işlenir."),
        ("b", "Çakıl ve kum oranları eşitse zemin kum grubunda değerlendirilir."),
    ]),
    ("BS 5930", [
        ("h1", "İngiliz Standardı — BS 5930:2015+A1:2020"),
        ("p", "Fraksiyonlar 2,0 mm ve 0,063 mm sınırlarıyla hesaplanır."),
        ("h2", "1. İri / ince ayrımı"),
        ("b", "İnce dane ≥ %35 → ince zemin (kil veya silt)."),
        ("b", "İnce dane < %35 → iri zemin (çakıl veya kum)."),
        ("h2", "2. Plastisite aralığı (LL'ye göre)"),
        ("t", [("LL (%)", "Harf", "Plastisite"),
               ("< 35", "L", "düşük"),
               ("35–50", "I", "orta"),
               ("50–70", "H", "yüksek"),
               ("70–90", "V", "çok yüksek"),
               ("≥ 90", "E", "aşırı yüksek")]),
        ("h2", "3. İnce zemin"),
        ("b", "LL ve PI zorunludur; yoksa sınıflandırma yapılmaz."),
        ("b", "PI ≥ A-hattı ve PI > 0 → kil (C); aksi halde silt (M). Sembol "
              "harf + plastisite harfidir (örneğin CI, MH)."),
        ("b", "Organik işaretliyse sembolün sonuna O eklenir (örneğin CIO)."),
        ("b", "İri dane (kum + çakıl) ≥ %35 ise sembolün başına S veya G, adın "
              "başına \"Kumlu\" ya da \"Çakıllı\" eklenir (hangisi büyükse; "
              "eşitse kum)."),
        ("h2", "4. İri zemin"),
        ("b", "Çakıl > kum → G (ÇAKIL), aksi halde S (KUM)."),
        ("b", "İyi derecelenmiş (W): çakılda Cu ≥ 4, kumda Cu ≥ 6 ve "
              "1 ≤ Cc ≤ 3. Değilse Cu ≤ 3 ise üniform derecelenmiş (Pu), "
              "diğer durumlarda kötü derecelenmiş (P)."),
        ("b", "İnce danenin türü: PI ≥ A-hattı → killi (C), aksi halde siltli "
              "(M). LL veya PI yoksa ya da PI = 0 ise siltli kabul edilir."),
        ("t", [("İnce dane", "Sembol", "Ad"),
               ("< %5", "GW, GPu, GP, SW…", "İyi / üniform / kötü derecelenmiş"),
               ("%5–15", "G-M, S-C…", "Az siltli / az killi"),
               ("%15–35", "GM, SC…", "Çok siltli / çok killi")]),
        ("b", "İnce dane ≥ %5 olan iri zeminlerde LL biliniyor ve PI > 0 ise "
              "sembolün sonuna plastisite harfi eklenir (örneğin SCI)."),
    ]),
    ("TS EN ISO 14688", [
        ("h1", "TS EN ISO 14688-1 / -2:2018"),
        ("p", "Fraksiyonlar 2,0 mm ve 0,063 mm sınırlarıyla hesaplanır. "
              "Semboller standarttaki kısaltmalarla oluşturulur: Gr çakıl, Sa "
              "kum, Si silt, Cl kil; küçük harfli ön ekler niteleyicidir "
              "(gr çakıllı, sa kumlu, si siltli, cl killi, or organik)."),
        ("h2", "1. İri / ince ayrımı"),
        ("b", "İnce dane ≥ %50 → ince zemin; aksi halde iri zemin."),
        ("h2", "2. Plastisite sınıfı (LL'ye göre)"),
        ("t", [("LL (%)", "Harf", "Plastisite"),
               ("< 35", "L", "düşük"),
               ("35–50", "M", "orta"),
               ("50–70", "H", "yüksek"),
               ("≥ 70", "V", "çok yüksek")]),
        ("h2", "3. İnce danenin türü"),
        ("b", "PI < 4 veya PI < A-hattı → silt (Si)."),
        ("b", "A-hattı üzerinde/üstünde ve PI ≤ 7 → siltli kil (Cl-Si)."),
        ("b", "Diğer durumlar → kil (Cl)."),
        ("h2", "4. İnce zemin"),
        ("b", "LL ve PI zorunludur; yoksa sınıflandırma yapılmaz."),
        ("b", "Sembol: tür + plastisite harfi (örneğin ClM, SiL, ClL-SiL)."),
        ("b", "Kum veya çakıldan büyük olanı > %15 ise sa ya da gr ön eki "
              "eklenir (örneğin saClM)."),
        ("h2", "5. İri zemin"),
        ("b", "Çakıl > kum → ana fraksiyon Gr, aksi halde Sa."),
        ("p", "Derecelenme harfi Cu ve Cc'ye göre:"),
        ("t", [("Koşul", "Harf", "Anlamı"),
               ("Cu ≥ 15 ve Cc < 0,5", "G", "aralıklı derecelenmiş"),
               ("Cu ≥ 15 ve 1 ≤ Cc ≤ 3", "W", "iyi derecelenmiş"),
               ("6 ≤ Cu < 15 ve Cc < 1", "M", "orta derecelenmiş"),
               ("3 ≤ Cu < 6 ve Cc < 1", "P", "kötü derecelenmiş"),
               ("Cu < 3 ve Cc < 1", "U", "üniform derecelenmiş"),
               ("Diğer durumlar", "P", "kötü derecelenmiş")]),
        ("t", [("İnce dane", "Sembol", "Örnek"),
               ("< %5", "Ana fraksiyon + derecelenme", "SaW, GrP"),
               ("%5–15", "İnce ön eki + ana fraksiyon + derecelenme", "siSaP"),
               ("> %15", "İnce ön eki + ana fraksiyon", "clSa")]),
        ("b", "İnce ön eki: silt → si, kil → cl. Siltli kil ince daneler "
              "%5–15 aralığında sicl (derecelenme harfi yazılmaz), %15'in "
              "üstünde cl olarak işlenir."),
        ("b", "%5'in altında Cu/Cc hesaplanamazsa P kabul edilir; %5–15 "
              "aralığında hesaplanamazsa derecelenme harfi yazılmaz."),
        ("b", "İnce dane ≥ %5 olan iri zeminde LL veya PI yoksa ince daneler "
              "siltli kabul edilir ve sonuç \"geçici\" olarak işaretlenir."),
        ("b", "Organik işaretliyse sembolün başına or, adın başına \"organik\" "
              "eklenir."),
        ("h2", "Not"),
        ("p", "İkinci iri fraksiyon %15'i aşsa bile üçüncül ön ek (sa-/gr-) "
              "iri zeminlerde sembole eklenmez; sembolde yalnızca ana fraksiyon "
              "ve ince dane ön eki gösterilir. Bu durum karar izlemesinde "
              "belirtilir."),
    ]),
    ("AASHTO", [
        ("h1", "AASHTO M 145 / ASTM D3282"),
        ("p", "Karayolu dolgu ve taban zeminleri için sınıflandırma. Kullanılan "
              "geçen yüzdeler eğri üzerinden okunur:"),
        ("f", "P10  = 2,0 mm (No. 10) elekten geçen %\n"
              "P40  = 0,425 mm (No. 40) elekten geçen %\n"
              "P200 = 0,075 mm (No. 200) elekten geçen %"),
        ("p", "PI yoksa veya PI = 0 ise zemin plastik olmayan (NP) kabul "
              "edilir."),
        ("h2", "1. Granüler malzeme (P200 ≤ %35)"),
        ("p", "Kurallar tablodaki sırayla, yukarıdan aşağıya denenir; ilk sağlanan grup seçilir:"),
        ("t", [("Grup", "Koşul", ""),
               ("A-1-a", "P10 ≤ 50, P40 ≤ 30, P200 ≤ 15, PI ≤ 6", ""),
               ("A-1-b", "P40 ≤ 50, P200 ≤ 25, PI ≤ 6", ""),
               ("A-3", "P40 > 50, P200 ≤ 10, NP", ""),
               ("A-2-4", "PI ≤ 10, LL ≤ 40", ""),
               ("A-2-5", "PI ≤ 10, LL > 40", ""),
               ("A-2-6", "PI > 10, LL ≤ 40", ""),
               ("A-2-7", "PI > 10, LL > 40", "")]),
        ("p", "A-2 alt grubunda LL yoksa 0 alınır."),
        ("h2", "2. Silt-kil malzeme (P200 > %35)"),
        ("t", [("Grup", "Koşul", ""),
               ("A-4", "PI ≤ 10, LL ≤ 40", ""),
               ("A-5", "PI ≤ 10, LL > 40", ""),
               ("A-6", "PI > 10, LL ≤ 40", ""),
               ("A-7-5", "PI > 10, LL > 40, PI ≤ LL − 30", ""),
               ("A-7-6", "PI > 10, LL > 40, PI > LL − 30", "")]),
        ("p", "LL veya PI yoksa A-4 kabul edilir ve karar izlemesinde "
              "belirtilir."),
        ("h2", "3. Grup indisi (GI)"),
        ("f", "GI = (F − 35) · [0,2 + 0,005 · (LL − 40)] + 0,01 · (F − 15) · (PI − 10)"),
        ("b", "F = P200. Parantez içi terimler sınırlandırılır: (F − 35) ve "
              "(F − 15) 0–40, (LL − 40) ve (PI − 10) 0–20 aralığında alınır."),
        ("b", "A-2-6 ve A-2-7 için yalnızca ikinci terim kullanılır: "
              "GI = 0,01 · (F − 15) · (PI − 10)."),
        ("b", "A-1, A-3, A-2-4 ve A-2-5 için GI = 0."),
        ("b", "GI en yakın tam sayıya yuvarlanır; negatif değerler 0 alınır. "
              "Sonuç \"A-2-6 (1)\" biçiminde gösterilir."),
        ("h2", "4. Taban zemini değerlendirmesi"),
        ("t", [("Grup", "Değerlendirme", ""),
               ("A-1, A-2, A-3", "Mükemmel ile iyi", ""),
               ("A-4, A-5, A-6, A-7", "Orta ile zayıf", "")]),
    ]),
    ("RSCS", [
        ("h1", "Revize Zemin Sınıflandırma Sistemi (RSCS)"),
        ("p", "Park ve Santamarina (2017) tarafından önerilen, uygulaması Castro, "
              "Park ve Santamarina (2023) ile açıklanan sistem. Zemin, çakıl, kum "
              "ve ince danenin yük taşıma (mekanik kontrol) ve akışkan akışı "
              "üzerindeki etkisine göre sınıflandırılır. Fraksiyonlar 4,75 mm "
              "(No. 4) ve 0,075 mm (No. 200) sınırlarıyla hesaplanır."),
        ("p", "RSCS yalnızca \"RSCS sınıflandırmasını dahil et\" işaretliyse "
              "hesaplanır. Parametre girilmezse aşağıdaki varsayılanlar "
              "kullanılır ve karar izlemesinde belirtilir."),
        ("h2", "1. İri danelerin boşluk oranları"),
        ("p", "Çakıl ve kum için ölçülmüş e_maks ve e_min girilmişse doğrudan "
              "kullanılır. Girilmemişse dane yuvarlaklığı R ve üniformluk "
              "katsayısı Cu'dan hesaplanır (Youd 1973; Cho vd. 2006):"),
        ("f", "e_maks = 0,032 + 0,154 / R + 0,522 / Cu\n"
              "e_min  = −0,012 + 0,082 / R + 0,371 / Cu"),
        ("p", "İkisi de yoksa R = 0,35 ve Cu = 2,0 alınır; bu değerlerle "
              "e_maks = 0,733 ve e_min = 0,408 olur."),
        ("h2", "2. İnce danenin boşluk oranları"),
        ("p", "Ana penceredeki LL, deiyonize su ile ölçülen likit limittir. LL "
              "yoksa LL = 25 alınır (plastik olmayan ince dane). Gs = 2,65."),
        ("f", "e_F|LL    = Gs · LL / 100\n"
              "e_F|10kPa = 0,026 · LL + 0,07\n"
              "e_F|1MPa  = 0,011 · LL + 0,21\n"
              "λ         = 2 · log10(LL − 25)   (λ ≥ 1; LL ≤ 25 için λ = 1)\n"
              "e_F|akış  = max(λ · e_F|LL ; e_F|10kPa)"),
        ("p", "λ = 1 olduğunda akış sınırı mekanik sınırla çakışır ve G(F), "
              "GS(F), S(F) grupları oluşmaz."),
        ("h2", "3. Belirgin karışımlar ve sınırlar"),
        ("p", "Grup sınırları, karışımlardaki boşlukların doldurulması koşuluyla "
              "hesaplanan 13 belirgin karışım noktasıyla çizilir. İki fazlı "
              "karışımda \"misafir\" malzemenin oranı:"),
        ("f", "misafir (%) = 100 · e_ev / (1 + e_ev + e_misafir)"),
        ("p", "Üç fazlı karışımlarda çakıl iskeletinin boşluğu kum + ince dane "
              "karışımıyla doldurulur:"),
        ("f", "d = 1 + e_G / (1 + e_S) + [e_G / (1 + e_F)] · [1 − 1 / (1 + e_S)]\n"
              "çakıl = 100 / d ;  kum = 100 · [e_G / (1 + e_S)] / d ;  ince = 100 − çakıl − kum"),
        ("p", "Gevşek iri iskelet için katsayılar: α(çakıl–kum) = 2,5 ve "
              "α(iri–ince) = 1,3. Karışım noktaları:"),
        ("t", [("No", "Karışım", "Kullanılan boşluk oranları"),
               ("1", "Çakıl + ince", "e_min,G ; e_F|10kPa"),
               ("2", "Çakıl + kum", "e_min,G ; e_maks,S"),
               ("3", "Çakıl + kum + ince", "e_min,G ; e_maks,S ; e_F|10kPa"),
               ("4", "Kum + ince", "e_min,S ; e_F|10kPa"),
               ("5", "Çakıl + kum", "2,5·e_maks,G ; e_min,S"),
               ("6", "Çakıl + kum + ince", "2,5·e_maks,G ; e_min,S ; e_F|10kPa"),
               ("7", "Çakıl + ince", "1,3·e_maks,G ; e_F|1MPa"),
               ("8", "Kum + ince", "1,3·e_maks,S ; e_F|1MPa"),
               ("9", "Çakıl + kum + ince", "2,5·e_maks,G ; 1,3·e_maks,S ; e_F|1MPa"),
               ("10", "Çakıl + ince", "e_min,G ; e_F|akış"),
               ("11", "Çakıl + kum + ince", "e_min,G ; e_maks,S ; e_F|akış"),
               ("12", "Çakıl + kum + ince", "2,5·e_maks,G ; e_min,S ; e_F|akış"),
               ("13", "Kum + ince", "e_min,S ; e_F|akış")]),
        ("h2", "4. Grubun belirlenmesi"),
        ("p", "Numunenin çakıl–kum–ince dane oranları üçgen diyagramda bir noktaya "
              "dönüştürülür ve 10 grup çokgeninden hangisinin içinde kaldığı "
              "bulunur. Nokta iki grubun sınırındaysa listede önce gelen grup "
              "raporlanır ve karar izlemesinde belirtilir. Sembolde parantez "
              "dışı harfler yükü taşıyan fraksiyonu, parantez içi harf akışı "
              "kontrol eden fraksiyonu gösterir."),
        ("t", [("Grup", "Açıklama", ""),
               ("G(G)", "Çakıl kontrollü; akışı çakıl kontrol eder", ""),
               ("GS(S)", "Çakıl ve kum yükü taşır; akışı kum kontrol eder", ""),
               ("S(S)", "Kum kontrollü; akışı kum kontrol eder", ""),
               ("G(F)", "Çakıl yükü taşır; akışı ince dane kontrol eder", ""),
               ("GS(F)", "Çakıl ve kum yükü taşır; akışı ince dane kontrol eder", ""),
               ("S(F)", "Kum yükü taşır; akışı ince dane kontrol eder", ""),
               ("GF(F)", "Geçiş: çakıl ve ince dane yükü taşır", ""),
               ("GSF(F)", "Geçiş: üç fraksiyon birlikte yükü taşır", ""),
               ("SF(F)", "Geçiş: kum ve ince dane yükü taşır", ""),
               ("F(F)", "İnce dane kontrollü; yükü ve akışı ince dane kontrol eder", "")]),
        ("h2", "5. İnce danenin sınıflandırılması (Jang ve Santamarina 2016)"),
        ("p", "Akışı ince danenin kontrol ettiği gruplarda (F) ve 2 M NaCl "
              "tuzlu su ile gazyağıyla ölçülen likit limitler de girilmişse "
              "ince dane, plastisite ve elektriksel duyarlılığa göre "
              "sınıflandırılır:"),
        ("f", "tuz = 1 − 0,11688 · LL_tuzlu / 100\n"
              "r_gaz = (LL_gaz / LL_tuzlu) · (tuz / 0,78)\n"
              "r_su  = (LL_su / LL_tuzlu) · tuz\n"
              "b = max(r_gaz ; 1 / r_gaz) ,  c = max(r_su ; 1 / r_su)\n"
              "S_E = √[(b − 1)² + (c − 1)²]\n"
              "LL_tuzlu (düzeltilmiş) = LL_tuzlu / tuz"),
        ("t", [("Plastisite (düzeltilmiş LL_tuzlu)", "Harf", ""),
               ("≤ 30", "N (plastik olmayan)", ""),
               ("30–50", "L (düşük)", ""),
               ("50–75", "I (orta)", ""),
               ("> 75", "H (yüksek)", "")]),
        ("t", [("Elektriksel duyarlılık S_E", "Harf", ""),
               ("≤ 0,4", "L (düşük)", ""),
               ("0,4–1,0", "I (orta)", ""),
               ("> 1,0", "H (yüksek)", "")]),
        ("p", "İki harf grup sembolüne eklenir (örneğin SF(F)-LI). Bu sınıflandırma "
              "için ek likit limitler girilmemişse karar izlemesinde bir "
              "hatırlatma gösterilir."),
    ]),
    ("Kaynaklar", [
        ("h1", "Kaynaklar"),
        ("b", "ASTM D2487-17, Standard Practice for Classification of Soils for "
              "Engineering Purposes (Unified Soil Classification System)."),
        ("b", "ASTM D3282, Standard Practice for Classification of Soils and "
              "Soil-Aggregate Mixtures for Highway Construction Purposes."),
        ("b", "AASHTO M 145, Standard Specification for Classification of Soils "
              "and Soil-Aggregate Mixtures for Highway Construction Purposes."),
        ("b", "BS 5930:2015+A1:2020, Code of Practice for Ground Investigations."),
        ("b", "EN ISO 14688-1 / -2:2018; TS EN ISO 14688-1 / -2, Jeoteknik "
              "araştırma ve deneyler - Zeminlerin tanımlanması ve "
              "sınıflandırılması."),
        ("b", "Park, J. ve Santamarina, J.C. (2017), \"Revised Soil "
              "Classification System for Coarse-Fine Mixtures\", J. Geotech. "
              "Geoenviron. Eng., 143(8), 04017039."),
        ("b", "Castro, G.M., Park, J. ve Santamarina, J.C. (2023), \"Revised "
              "Soil Classification System: Implementation and Engineering "
              "Implications\", J. Geotech. Geoenviron. Eng., 149(11), 04023109."),
        ("b", "Jang, J. ve Santamarina, J.C. (2016), \"Fines Classification "
              "Based on Sensitivity to Pore-Fluid Chemistry\", J. Geotech. "
              "Geoenviron. Eng., 142(4), 06015018."),
        ("b", "Fritsch, F.N. ve Carlson, R.E. (1980), \"Monotone Piecewise "
              "Cubic Interpolation\", SIAM J. Numer. Anal., 17(2), 238–246."),
    ]),
]

_EN: List[Tuple[str, List[Block]]] = [
    ("General", [
        ("h1", "General calculations"),
        ("p", "This section describes the input checks and grain-size "
              "calculations shared by all five classification systems. The "
              "rules of each system are given in its own tab."),
        ("h2", "Input checks"),
        ("b", "At least two sieve points are required. Sieve openings must be "
              "greater than zero and percent passing between 0 and 100."),
        ("b", "Percent passing may not increase as the opening gets smaller; if "
              "it does, the soil is not classified and the rows are reported."),
        ("b", "The liquid limit (LL) and plastic limit (PL) must be between 0 "
              "and 600, and PL may not exceed LL."),
        ("b", "When \"Non-plastic (NP)\" is ticked, LL and PL are ignored and "
              "the soil is treated as non-plastic."),
        ("h2", "Plasticity index"),
        ("f", "PI = LL − PL      (a negative result is taken as PI = 0)"),
        ("h2", "Grain-size curve"),
        ("p", "Sieve data are treated as percent passing against the base-10 "
              "logarithm of particle size. Values between the points are "
              "obtained by monotone piecewise cubic Hermite interpolation "
              "(PCHIP), which passes through every measured point and does not "
              "create artificial peaks or dips between them."),
        ("b", "If the same opening is entered twice, the two values are "
              "averaged."),
        ("b", "If a requested size lies outside the measured range, the value "
              "at the nearest end is used (for example, if the finest sieve is "
              "coarser than 0.075 mm, the fines content equals the percent "
              "passing the finest sieve)."),
        ("b", "On the charts the curve is extended beyond the measured range "
              "with its end slope on the logarithmic axis. This extension is "
              "for drawing only and is not used in classification."),
        ("h2", "Characteristic sizes and grading"),
        ("p", "D10, D30 and D60 are the particle sizes at 10 %, 30 % and 60 % "
              "passing, found by inverting the curve (bisection). If the "
              "required percentage is outside the measured range, that size is "
              "not computed."),
        ("f", "Cu = D60 / D10\nCc = D30² / (D10 · D60)"),
        ("p", "If D10 cannot be found, Cu and Cc are not available; each tab "
              "states what the system does in that case."),
        ("h2", "Fractions"),
        ("p", "Gravel, sand and fines contents are taken from the curve at two "
              "boundary sizes:"),
        ("f", "Fines  = P(sand/fines boundary)\n"
              "Sand   = P(gravel/sand boundary) − P(sand/fines boundary)\n"
              "Gravel = 100 − P(gravel/sand boundary)"),
        ("t", [("System", "Gravel / sand boundary", "Sand / fines boundary"),
               ("USCS (ASTM D2487)", "4.75 mm (No. 4)", "0.075 mm (No. 200)"),
               ("BS 5930", "2.0 mm", "0.063 mm"),
               ("TS EN ISO 14688", "2.0 mm", "0.063 mm"),
               ("AASHTO M 145", "2.0 mm (No. 10)", "0.075 mm (No. 200)"),
               ("RSCS", "4.75 mm (No. 4)", "0.075 mm (No. 200)")]),
        ("h2", "A-line and U-line"),
        ("f", "A-line: PI = 0.73 · (LL − 20)\nU-line: PI = 0.9 · (LL − 8)"),
        ("p", "The A-line separates clay from silt in USCS, BS 5930 and TS EN "
              "ISO 14688. The U-line is only drawn on the plasticity chart as an "
              "upper bound and is not used in any decision."),
    ]),
    ("USCS", [
        ("h1", "USCS — ASTM D2487"),
        ("p", "Unified Soil Classification System. Fractions use the 4.75 mm "
              "(No. 4) and 0.075 mm (No. 200) boundaries."),
        ("h2", "1. Coarse / fine split"),
        ("b", "Fines ≥ 50 % → fine-grained soil."),
        ("b", "Fines < 50 % → coarse-grained soil."),
        ("h2", "2. Fines symbol"),
        ("b", "If organic is ticked: LL < 50 → OL, LL ≥ 50 → OH."),
        ("b", "LL < 50: PI > 7 and PI ≥ A-line → CL; PI < 4 or PI < A-line → "
              "ML; otherwise (4 ≤ PI ≤ 7 on/above the A-line) → CL-ML."),
        ("b", "LL ≥ 50: PI ≥ A-line → CH; otherwise MH."),
        ("b", "If LL or PI is missing, the fines are assumed silty (ML) and "
              "this is stated in the decision trail."),
        ("h2", "3. Name of a fine-grained soil"),
        ("p", "Group names: CL lean clay, ML silt, CH fat clay, MH elastic silt, "
              "CL-ML silty clay, OL/OH organic silt/clay. Coarse content "
              "(sand + gravel):"),
        ("b", "15–30 % → \"with sand\" or \"with gravel\" (whichever is larger; "
              "sand on a tie)."),
        ("b", "≥ 30 % → the name starts with \"Sandy …\" or \"Gravelly …\"."),
        ("h2", "4. Coarse-grained soil"),
        ("b", "Gravel > sand → G (gravel), otherwise S (sand)."),
        ("b", "Well graded (W): Cu ≥ 4 for gravel, Cu ≥ 6 for sand, and "
              "1 ≤ Cc ≤ 3. Otherwise, or if Cu/Cc cannot be computed, poorly "
              "graded (P)."),
        ("t", [("Fines", "Symbol", "Example"),
               ("< 5 %", "GW, GP, SW, SP", "Well-graded sand"),
               ("5–12 %", "Dual symbol", "SP-SM, GW-GC"),
               ("> 12 %", "GM, GC, SM, SC", "Clayey sand")]),
        ("b", "The fines type follows step 2: CL/CH → C; ML/MH/OL/OH → M. "
              "CL-ML fines give GC-GM or SC-SM above 12 % and are treated as M "
              "between 5 and 12 %."),
        ("b", "If the other coarse fraction is ≥ 15 %, \"with sand\" or "
              "\"with gravel\" is added to the name."),
        ("h2", "Notes"),
        ("b", "In organic coarse-grained soils the fines are treated as M."),
        ("b", "If gravel and sand are equal, the soil is placed in the sand "
              "group."),
    ]),
    ("BS 5930", [
        ("h1", "British Standard — BS 5930:2015+A1:2020"),
        ("p", "Fractions use the 2.0 mm and 0.063 mm boundaries."),
        ("h2", "1. Coarse / fine split"),
        ("b", "Fines ≥ 35 % → fine soil (clay or silt)."),
        ("b", "Fines < 35 % → coarse soil (gravel or sand)."),
        ("h2", "2. Plasticity range (by LL)"),
        ("t", [("LL (%)", "Letter", "Plasticity"),
               ("< 35", "L", "low"),
               ("35–50", "I", "intermediate"),
               ("50–70", "H", "high"),
               ("70–90", "V", "very high"),
               ("≥ 90", "E", "extremely high")]),
        ("h2", "3. Fine soil"),
        ("b", "LL and PI are required; otherwise the soil is not classified."),
        ("b", "PI ≥ A-line and PI > 0 → clay (C); otherwise silt (M). The "
              "symbol is the letter plus the plasticity letter (e.g. CI, MH)."),
        ("b", "If organic is ticked, O is appended (e.g. CIO)."),
        ("b", "If coarse content (sand + gravel) is ≥ 35 %, S or G is put in "
              "front of the symbol and \"Sandy\" or \"Gravelly\" in front of the "
              "name (whichever is larger; sand on a tie)."),
        ("h2", "4. Coarse soil"),
        ("b", "Gravel > sand → G (GRAVEL), otherwise S (SAND)."),
        ("b", "Well graded (W): Cu ≥ 4 for gravel, Cu ≥ 6 for sand, and "
              "1 ≤ Cc ≤ 3. Otherwise uniformly graded (Pu) if Cu ≤ 3, else "
              "poorly graded (P)."),
        ("b", "Fines type: PI ≥ A-line → clayey (C), otherwise silty (M). If "
              "LL or PI is missing or PI = 0, the fines are taken as silty."),
        ("t", [("Fines", "Symbol", "Name"),
               ("< 5 %", "GW, GPu, GP, SW…", "Well / uniformly / poorly graded"),
               ("5–15 %", "G-M, S-C…", "Slightly silty / slightly clayey"),
               ("15–35 %", "GM, SC…", "Very silty / very clayey")]),
        ("b", "For coarse soils with fines ≥ 5 %, the plasticity letter is "
              "appended when LL is known and PI > 0 (e.g. SCI)."),
    ]),
    ("TS EN ISO 14688", [
        ("h1", "TS EN ISO 14688-1 / -2:2018"),
        ("p", "Fractions use the 2.0 mm and 0.063 mm boundaries. Symbols use the "
              "abbreviations of the standard: Gr gravel, Sa sand, Si silt, Cl "
              "clay; lower-case prefixes are qualifiers (gr gravelly, sa sandy, "
              "si silty, cl clayey, or organic)."),
        ("h2", "1. Coarse / fine split"),
        ("b", "Fines ≥ 50 % → fine soil; otherwise coarse soil."),
        ("h2", "2. Plasticity class (by LL)"),
        ("t", [("LL (%)", "Letter", "Plasticity"),
               ("< 35", "L", "low"),
               ("35–50", "M", "medium"),
               ("50–70", "H", "high"),
               ("≥ 70", "V", "very high")]),
        ("h2", "3. Fines type"),
        ("b", "PI < 4 or PI < A-line → silt (Si)."),
        ("b", "On/above the A-line with PI ≤ 7 → silty clay (Cl-Si)."),
        ("b", "Otherwise → clay (Cl)."),
        ("h2", "4. Fine soil"),
        ("b", "LL and PI are required; otherwise the soil is not classified."),
        ("b", "Symbol: type + plasticity letter (e.g. ClM, SiL, ClL-SiL)."),
        ("b", "If the larger of sand and gravel exceeds 15 %, the prefix sa or "
              "gr is added (e.g. saClM)."),
        ("h2", "5. Coarse soil"),
        ("b", "Gravel > sand → main fraction Gr, otherwise Sa."),
        ("p", "Grading letter from Cu and Cc:"),
        ("t", [("Condition", "Letter", "Meaning"),
               ("Cu ≥ 15 and Cc < 0.5", "G", "gap graded"),
               ("Cu ≥ 15 and 1 ≤ Cc ≤ 3", "W", "well graded"),
               ("6 ≤ Cu < 15 and Cc < 1", "M", "medium graded"),
               ("3 ≤ Cu < 6 and Cc < 1", "P", "poorly graded"),
               ("Cu < 3 and Cc < 1", "U", "uniformly graded"),
               ("Any other case", "P", "poorly graded")]),
        ("t", [("Fines", "Symbol", "Example"),
               ("< 5 %", "Main fraction + grading", "SaW, GrP"),
               ("5–15 %", "Fines prefix + main fraction + grading", "siSaP"),
               ("> 15 %", "Fines prefix + main fraction", "clSa")]),
        ("b", "Fines prefix: silt → si, clay → cl. Silty-clay fines give sicl "
              "between 5 and 15 % (no grading letter) and cl above 15 %."),
        ("b", "Below 5 % fines, P is assumed if Cu/Cc cannot be computed; "
              "between 5 and 15 % the grading letter is then omitted."),
        ("b", "If LL or PI is missing in a coarse soil with fines ≥ 5 %, the "
              "fines are assumed silty and the result is marked "
              "\"provisional\"."),
        ("b", "If organic is ticked, or is put in front of the symbol and "
              "\"organic\" in front of the name."),
        ("h2", "Note"),
        ("p", "Even if the second coarse fraction exceeds 15 %, the tertiary "
              "prefix (sa-/gr-) is not added to coarse soils; the symbol shows "
              "only the main fraction and the fines prefix. The decision trail "
              "states this."),
    ]),
    ("AASHTO", [
        ("h1", "AASHTO M 145 / ASTM D3282"),
        ("p", "Classification for highway embankment and subgrade soils. The "
              "percent passing values are read from the curve:"),
        ("f", "P10  = % passing 2.0 mm (No. 10)\n"
              "P40  = % passing 0.425 mm (No. 40)\n"
              "P200 = % passing 0.075 mm (No. 200)"),
        ("p", "If PI is missing or PI = 0, the soil is treated as non-plastic "
              "(NP)."),
        ("h2", "1. Granular material (P200 ≤ 35 %)"),
        ("p", "The rules are tried from top to bottom; the first one met gives the group:"),
        ("t", [("Group", "Condition", ""),
               ("A-1-a", "P10 ≤ 50, P40 ≤ 30, P200 ≤ 15, PI ≤ 6", ""),
               ("A-1-b", "P40 ≤ 50, P200 ≤ 25, PI ≤ 6", ""),
               ("A-3", "P40 > 50, P200 ≤ 10, NP", ""),
               ("A-2-4", "PI ≤ 10, LL ≤ 40", ""),
               ("A-2-5", "PI ≤ 10, LL > 40", ""),
               ("A-2-6", "PI > 10, LL ≤ 40", ""),
               ("A-2-7", "PI > 10, LL > 40", "")]),
        ("p", "In the A-2 subgroups a missing LL is taken as 0."),
        ("h2", "2. Silt-clay material (P200 > 35 %)"),
        ("t", [("Group", "Condition", ""),
               ("A-4", "PI ≤ 10, LL ≤ 40", ""),
               ("A-5", "PI ≤ 10, LL > 40", ""),
               ("A-6", "PI > 10, LL ≤ 40", ""),
               ("A-7-5", "PI > 10, LL > 40, PI ≤ LL − 30", ""),
               ("A-7-6", "PI > 10, LL > 40, PI > LL − 30", "")]),
        ("p", "If LL or PI is missing, A-4 is assumed and stated in the "
              "decision trail."),
        ("h2", "3. Group index (GI)"),
        ("f", "GI = (F − 35) · [0.2 + 0.005 · (LL − 40)] + 0.01 · (F − 15) · (PI − 10)"),
        ("b", "F = P200. The terms are limited: (F − 35) and (F − 15) to 0–40, "
              "(LL − 40) and (PI − 10) to 0–20."),
        ("b", "For A-2-6 and A-2-7 only the second term is used: "
              "GI = 0.01 · (F − 15) · (PI − 10)."),
        ("b", "GI = 0 for A-1, A-3, A-2-4 and A-2-5."),
        ("b", "GI is rounded to the nearest whole number; negative values are "
              "taken as 0. The result is shown as \"A-2-6 (1)\"."),
        ("h2", "4. Subgrade rating"),
        ("t", [("Group", "Rating", ""),
               ("A-1, A-2, A-3", "Excellent to good", ""),
               ("A-4, A-5, A-6, A-7", "Fair to poor", "")]),
    ]),
    ("RSCS", [
        ("h1", "Revised Soil Classification System (RSCS)"),
        ("p", "Proposed by Park and Santamarina (2017), with its implementation "
              "described by Castro, Park and Santamarina (2023). The soil is "
              "classified by how gravel, sand and fines control load-carrying "
              "(mechanical control) and fluid flow. Fractions use the 4.75 mm "
              "(No. 4) and 0.075 mm (No. 200) boundaries."),
        ("p", "RSCS is only calculated when \"Include RSCS classification\" is "
              "ticked. If no parameters are entered, the defaults below are "
              "used and stated in the decision trail."),
        ("h2", "1. Void ratios of the coarse fractions"),
        ("p", "Measured e_max and e_min of gravel and sand are used directly. "
              "Otherwise they are computed from particle roundness R and the "
              "coefficient of uniformity Cu (Youd 1973; Cho et al. 2006):"),
        ("f", "e_max = 0.032 + 0.154 / R + 0.522 / Cu\n"
              "e_min = −0.012 + 0.082 / R + 0.371 / Cu"),
        ("p", "If neither is given, R = 0.35 and Cu = 2.0 are used, giving "
              "e_max = 0.733 and e_min = 0.408."),
        ("h2", "2. Void ratios of the fines"),
        ("p", "The LL in the main window is the liquid limit with deionized "
              "water. If LL is missing, LL = 25 is used (non-plastic fines). "
              "Gs = 2.65."),
        ("f", "e_F|LL    = Gs · LL / 100\n"
              "e_F|10kPa = 0.026 · LL + 0.07\n"
              "e_F|1MPa  = 0.011 · LL + 0.21\n"
              "λ         = 2 · log10(LL − 25)   (λ ≥ 1; λ = 1 for LL ≤ 25)\n"
              "e_F|flow  = max(λ · e_F|LL ; e_F|10kPa)"),
        ("p", "When λ = 1 the flow boundary coincides with the mechanical "
              "boundary and the G(F), GS(F) and S(F) groups do not exist."),
        ("h2", "3. Notable mixtures and boundaries"),
        ("p", "The group boundaries are drawn through 13 notable mixtures, "
              "computed from the condition that the voids of one material are "
              "filled by another. For a two-phase mixture the \"guest\" "
              "content is:"),
        ("f", "guest (%) = 100 · e_host / (1 + e_host + e_guest)"),
        ("p", "In three-phase mixtures the voids of the gravel skeleton are "
              "filled by the sand + fines mixture:"),
        ("f", "d = 1 + e_G / (1 + e_S) + [e_G / (1 + e_F)] · [1 − 1 / (1 + e_S)]\n"
              "gravel = 100 / d ;  sand = 100 · [e_G / (1 + e_S)] / d ;  fines = 100 − gravel − sand"),
        ("p", "Factors for a loose coarse skeleton: α(gravel–sand) = 2.5 and "
              "α(coarse–fines) = 1.3. The mixtures are:"),
        ("t", [("No", "Mixture", "Void ratios used"),
               ("1", "Gravel + fines", "e_min,G ; e_F|10kPa"),
               ("2", "Gravel + sand", "e_min,G ; e_max,S"),
               ("3", "Gravel + sand + fines", "e_min,G ; e_max,S ; e_F|10kPa"),
               ("4", "Sand + fines", "e_min,S ; e_F|10kPa"),
               ("5", "Gravel + sand", "2.5·e_max,G ; e_min,S"),
               ("6", "Gravel + sand + fines", "2.5·e_max,G ; e_min,S ; e_F|10kPa"),
               ("7", "Gravel + fines", "1.3·e_max,G ; e_F|1MPa"),
               ("8", "Sand + fines", "1.3·e_max,S ; e_F|1MPa"),
               ("9", "Gravel + sand + fines", "2.5·e_max,G ; 1.3·e_max,S ; e_F|1MPa"),
               ("10", "Gravel + fines", "e_min,G ; e_F|flow"),
               ("11", "Gravel + sand + fines", "e_min,G ; e_max,S ; e_F|flow"),
               ("12", "Gravel + sand + fines", "2.5·e_max,G ; e_min,S ; e_F|flow"),
               ("13", "Sand + fines", "e_min,S ; e_F|flow")]),
        ("h2", "4. Group"),
        ("p", "The gravel–sand–fines contents of the sample are converted to a "
              "point on the ternary diagram and the group polygon containing it "
              "is found. If the point lies on a boundary, the group listed first "
              "is reported and the decision trail says so. Letters outside the "
              "brackets show the load-carrying fraction; the letter in brackets "
              "shows the fraction that controls fluid flow."),
        ("t", [("Group", "Description", ""),
               ("G(G)", "Gravel-controlled; gravel controls flow", ""),
               ("GS(S)", "Gravel and sand carry the load; sand controls flow", ""),
               ("S(S)", "Sand-controlled; sand controls flow", ""),
               ("G(F)", "Gravel carries the load; fines control flow", ""),
               ("GS(F)", "Gravel and sand carry the load; fines control flow", ""),
               ("S(F)", "Sand carries the load; fines control flow", ""),
               ("GF(F)", "Transitional: gravel and fines carry the load", ""),
               ("GSF(F)", "Transitional: all three fractions carry the load", ""),
               ("SF(F)", "Transitional: sand and fines carry the load", ""),
               ("F(F)", "Fines-controlled; fines control load and flow", "")]),
        ("h2", "5. Fines classification (Jang and Santamarina 2016)"),
        ("p", "In the groups where fines control flow (F), and when the liquid "
              "limits with 2 M NaCl brine and with kerosene are also entered, "
              "the fines are classified by plasticity and electrical "
              "sensitivity:"),
        ("f", "salt = 1 − 0.11688 · LL_brine / 100\n"
              "r_ker = (LL_ker / LL_brine) · (salt / 0.78)\n"
              "r_dw  = (LL_dw / LL_brine) · salt\n"
              "b = max(r_ker ; 1 / r_ker) ,  c = max(r_dw ; 1 / r_dw)\n"
              "S_E = √[(b − 1)² + (c − 1)²]\n"
              "LL_brine (corrected) = LL_brine / salt"),
        ("t", [("Plasticity (corrected LL_brine)", "Letter", ""),
               ("≤ 30", "N (non-plastic)", ""),
               ("30–50", "L (low)", ""),
               ("50–75", "I (intermediate)", ""),
               ("> 75", "H (high)", "")]),
        ("t", [("Electrical sensitivity S_E", "Letter", ""),
               ("≤ 0.4", "L (low)", ""),
               ("0.4–1.0", "I (intermediate)", ""),
               ("> 1.0", "H (high)", "")]),
        ("p", "The two letters are appended to the group symbol (e.g. "
              "SF(F)-LI). If the extra liquid limits are not entered, the "
              "decision trail shows a reminder."),
    ]),
    ("References", [
        ("h1", "References"),
        ("b", "ASTM D2487-17, Standard Practice for Classification of Soils for "
              "Engineering Purposes (Unified Soil Classification System)."),
        ("b", "ASTM D3282, Standard Practice for Classification of Soils and "
              "Soil-Aggregate Mixtures for Highway Construction Purposes."),
        ("b", "AASHTO M 145, Standard Specification for Classification of Soils "
              "and Soil-Aggregate Mixtures for Highway Construction Purposes."),
        ("b", "BS 5930:2015+A1:2020, Code of Practice for Ground Investigations."),
        ("b", "EN ISO 14688-1 / -2:2018, Geotechnical investigation and testing - "
              "Identification and classification of soil."),
        ("b", "Park, J. and Santamarina, J.C. (2017), \"Revised Soil "
              "Classification System for Coarse-Fine Mixtures\", J. Geotech. "
              "Geoenviron. Eng., 143(8), 04017039."),
        ("b", "Castro, G.M., Park, J. and Santamarina, J.C. (2023), \"Revised "
              "Soil Classification System: Implementation and Engineering "
              "Implications\", J. Geotech. Geoenviron. Eng., 149(11), 04023109."),
        ("b", "Jang, J. and Santamarina, J.C. (2016), \"Fines Classification "
              "Based on Sensitivity to Pore-Fluid Chemistry\", J. Geotech. "
              "Geoenviron. Eng., 142(4), 06015018."),
        ("b", "Fritsch, F.N. and Carlson, R.E. (1980), \"Monotone Piecewise "
              "Cubic Interpolation\", SIAM J. Numer. Anal., 17(2), 238–246."),
    ]),
]

_SECTIONS: Dict[str, List[Tuple[str, List[Block]]]] = {"tr": _TR, "en": _EN}


def method_sections(lang: str = None) -> List[Tuple[str, List[Block]]]:
    return _SECTIONS.get(lang or get_language(), _EN)
