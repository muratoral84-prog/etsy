# Basketbol tişört baskıları — Etsy listeleme dosyası

Bu klasördeki tasarımlar `node tools/tisort-uret.mjs` ile üretilir; kaynak
`assets/js/tasarimlar.js` içindedir. Önizleme: `tisort.html`.

## Yasal not (önce bunu okuyun)

Etsy'de en sık kapatılan basketbol listelemeleri telif/marka ihlalinden
kapanır. Bu depodaki tasarımlar bilerek **jenerik** tutulmuştur:

- Gerçek bir sporcunun **adı, portresi, silueti, imzası, lakabı** yok.
- Takım adı, lig adı (NBA vb.), kulüp logosu, forma tasarımı yok.
- Marka sloganı veya tescilli logo (Jumpman, Air, Swoosh vb.) yok.
- Yalnızca **23 sayısı** kullanılır; tek başına bir sayı tescil edilemez.
  Ancak sayıyı gerçek bir oyuncunun adı, takımı veya lakabıyla birlikte
  kullanmak ihlal olur — ürün başlığına ve etiketlerine oyuncu adı yazmayın.

Listelemeyi "Michael Jordan tişörtü" diye adlandırmak tasarım özgün olsa bile
isim/görüntü hakkı ihlalidir ve dükkânın kapanma sebebidir.

## Baskı dosyaları

| Dosya | Kullanım |
| --- | --- |
| `tasarim/hang-time-acik-zemin.svg` | Beyaz / bej / gri melanj tişört |
| `tasarim/hang-time-koyu-zemin.svg` | Siyah / lacivert / haki tişört |
| `tasarim/yirmi-uc-acik-zemin.svg` | Beyaz / bej / gri melanj tişört |
| `tasarim/yirmi-uc-koyu-zemin.svg` | Siyah / lacivert / haki tişört |
| `tasarim/pota-acik-zemin.svg` | Beyaz / bej / gri melanj tişört |
| `tasarim/pota-koyu-zemin.svg` | Siyah / lacivert / haki tişört |

**Teknik:** 3600×4800 px = 12×16 inç @ 300 dpi, şeffaf zemin, iki mürekkep
(ana renk + turuncu vurgu). Tüm yazılar vektör yola çevrilmiştir; baskıcıda
yazı tipi eksikliği sorunu çıkmaz. SVG'yi Printful/Printify PNG istiyorsa
Inkscape ile dışa aktarın:

```bash
inkscape urun/tisort/tasarim/yirmi-uc-koyu-zemin.svg \
  --export-type=png --export-dpi=300 \
  --export-filename=yirmi-uc-koyu-zemin.png
```

**Yerleşim (POD):** ön ortadan baskı, yaka dikişinin 7,5–8 cm altından
başlayacak şekilde; genişlik 30 cm (12 inç), S–XL bedenlerde aynı kalıp,
2XL+ için %10 büyütün.

---

## 1) Yirmi Üç — halka içinde 23

**Başlık (EN, ≤140 karakter):**
Basketball 23 Shirt, Retro Hoops Tee, Vintage Hardwood Basketball T-Shirt, Gift for Basketball Player, Number 23 Graphic Tee

**Başlık (TR):**
Basketbol 23 Tişört, Retro Basketbol Baskılı Tişört, Basketbolcuya Hediye

**Etiketler (13 adet, her biri ≤20 karakter):**
`basketball shirt`, `number 23 tee`, `hoops t shirt`, `retro basketball`,
`hardwood tee`, `basketball gift`, `vintage hoops`, `streetball shirt`,
`basketball lover`, `sports graphic tee`, `gift for baller`,
`varsity number tee`, `basketball mom`

**Açıklama (EN):**
> Old-school hardwood energy on a soft everyday tee. A heavy block "23" locked
> inside a bold ring, with GREATEST OF ALL TIME set in vintage varsity type.
> Original artwork — no team, league or player branding.
>
> • Printed on demand, ships in 2–5 business days
> • Unisex fit, 100% ring-spun cotton (heather colours 52/48)
> • Machine wash cold, inside out, tumble dry low
> • Sizes S–3XL — see the size chart photo before ordering
>
> Made for pickup-game regulars, coaches, basketball parents and anyone who
> still talks about the hardwood era. Gift-ready for birthdays and the start
> of the season.

**Açıklama (TR):**
> Eski usul parke havası, günlük giyilebilecek yumuşak bir tişörtte. Kalın
> blok "23" rakamı bir halkanın içinde, altında retro varsity tipografi.
> Tasarım tamamen özgündür; takım, lig veya oyuncu markası içermez.
>
> • Sipariş üzerine baskı, 2–5 iş gününde kargoda
> • Unisex kalıp, %100 penye pamuk
> • Tersyüz ederek 30°C'de yıkayın, düşük ısıda kurutun
> • S–3XL bedenler — sipariş öncesi beden tablosuna bakın

---

## 2) Hang Time — havalanan top

**Başlık (EN):**
Hang Time Basketball Shirt, Retro Hoops Graphic Tee, Streetball T-Shirt, Basketball Coach Gift, Vintage Sports Tee

**Başlık (TR):**
Hang Time Basketbol Tişörtü, Retro Sokak Basketbolu Baskılı Tişört

**Etiketler:**
`hang time shirt`, `basketball shirt`, `hoops graphic tee`, `streetball tee`,
`retro sports tee`, `basketball gift`, `dunk t shirt`, `bball tee`,
`coach gift shirt`, `basketball team`, `vintage hoops`, `player gift`,
`sports lover tee`

**Açıklama (EN):**
> The arc of a ball at the top of its flight, two lines of chunky block type
> underneath: HANG TIME · HARDWOOD CLASSICS. Screen-print-friendly two-colour
> artwork with clean edges at any size. Original design, no licensed marks.
>
> • Printed on demand, ships in 2–5 business days
> • Unisex fit, 100% ring-spun cotton
> • Wash cold inside out — the print stays sharp
> • Sizes S–3XL

---

## 3) Pota — file ve düşen top

**Başlık (EN):**
Nothing But Net Shirt, Basketball Hoop Graphic Tee, Retro Streetball T-Shirt, Basketball Player Gift, Sports Graphic Tee

**Başlık (TR):**
Nothing But Net Tişört, Pota Baskılı Basketbol Tişörtü

**Etiketler:**
`nothing but net`, `basketball hoop tee`, `basketball shirt`, `swish tee`,
`streetball shirt`, `hoops graphic tee`, `retro basketball`, `bball gift`,
`sports graphic tee`, `basketball coach`, `player gift shirt`,
`basketball fan tee`, `net t shirt`

**Açıklama (EN):**
> Backboard, rim, net and the ball on its way through — drawn from scratch in
> clean vector lines, finished with NOTHING BUT NET in heavy block letters.
> Original artwork, no team or league marks.
>
> • Printed on demand, ships in 2–5 business days
> • Unisex fit, 100% ring-spun cotton
> • Machine wash cold, inside out
> • Sizes S–3XL

---

## Listeleme ayarları (üçü için ortak)

| Alan | Değer |
| --- | --- |
| Kategori | Clothing → Unisex Adult Clothing → Tops & Tees → T-shirts |
| Who made it | I did (tasarım) / Another company (baskı, POD ise) |
| What is it | A finished product |
| When made | Made to order |
| Materials | Cotton, Ring-spun cotton, Water-based ink |
| Production partner | POD sağlayıcınızı Etsy panelinde tanımlayın (zorunlu) |
| Renk varyasyonları | Siyah, Lacivert, Haki, Beyaz, Kum, Gri melanj |
| Beden varyasyonları | S, M, L, XL, 2XL, 3XL |
| Personalization | Kapalı |
| Renewal | Automatic |

**Fotoğraf sırası:** 1) koyu tişört üzerinde tasarım 2) açık tişört
3) yakın plan baskı dokusu 4) beden tablosu 5) renk seçenekleri
6) kumaş/yıkama bilgisi 7) paketleme. `tisort.html` sayfasındaki manken
görselini taslak olarak kullanabilirsiniz; vitrin fotoğrafında gerçek ürün
görseli kullanmak dönüşümü artırır.
