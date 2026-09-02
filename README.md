# Murat Oral Medya Ajansı — NFC Dijital Kartvizit

NFC etiketine dokunulduğunda (veya QR kod okutulduğunda) açılan, tek dokunuşla
aranabilen / rehbere eklenebilen dijital kartvizit. Tamamen statik: derleme
adımı, paket kurulumu ve dış bağımlılık yok — QR üreteci de vCard oluşturucu da
bu depoda, sıfırdan yazılmış durumda.

```
NFC etiketi (NDEF URL kaydı)
        ↓ telefonu yaklaştır
https://…/etsy/?kaynak=nfc
        ↓
index.html → Ara · WhatsApp · E-posta · Rehbere ekle · QR · Paylaş
```

## Hızlı başlangıç

1. **Bilgileri girin** — `assets/js/config.js` tek düzenleme noktasıdır.
   Telefon, WhatsApp, e-posta, web, sosyal medya ve hizmetleri kendi
   bilgilerinizle değiştirin, sonra `dogrulanmisBilgiler: true` yapın
   (bu alan `false` iken sayfanın üstünde "örnek veri" uyarısı görünür).
2. **Dosyaları üretin** — `node tools/uret.mjs`
   (`kartvizit.vcf` ve `assets/qr-kartvizit.svg` yeniden oluşturulur).
3. **Yayınlayın** — depo ayarlarında **Settings → Pages → Source: GitHub Actions**
   seçin. `main` dalına her gönderimde `.github/workflows/pages.yml` önce
   testleri çalıştırır, sonra siteyi yayınlar.
   Varsayılan adres: `https://muratoral84-prog.github.io/etsy/`
   (farklı bir alan adı kullanacaksanız `config.js` içindeki `site.url` alanını
   güncelleyip 2. adımı tekrarlayın).
4. **Etikete yazın** — Android telefonda Chrome ile `…/nfc.html` sayfasını açın,
   boş NFC etiketini telefonun arkasına dokundurun ve **Etikete yaz**'a basın.

## NFC etiketine yazma

`nfc.html` sayfası [Web NFC](https://developer.mozilla.org/en-US/docs/Web/API/Web_NFC_API)
kullanır; **yalnızca Android + Chrome** ve **HTTPS** adreste çalışır
(`file://` veya `http://` üzerinden çalışmaz).

| Kayıt türü | Ne yazılır | Ne zaman |
| --- | --- | --- |
| **Adres (URL)** | ~50 bayt | Önerilen. En ucuz etikete sığar, içerik sonradan güncellenebilir. |
| **vCard** | ~650 bayt | Telefon internetsizken bile rehbere ekleme. NTAG216 gerekir. |
| **Adres + vCard** | ~700 bayt | İkisi birden; yalnızca büyük etiketlerde. |

Sayfa, seçilen kayıt için tahmini NDEF boyutunu hesaplar ve hangi etikete
sığdığını söyler (NTAG213 = 144 bayt, NTAG215 = 504 bayt, NTAG216 = 888 bayt).
**Etiketi oku / doğrula** düğmesi yazdıktan sonra içeriği geri okur.

Ayrıca **kalıcı kilit** seçeneği vardır: etiketi geri dönüşü olmayan biçimde
salt okunur yapar. İşlem öncesi onay ister; müşteriye/masaya bırakılacak
etiketler dışında kullanmayın.

**iPhone:** Web NFC desteklemez. Etiketi yazmak için Kestirmeler (Shortcuts)
uygulamasının NFC eylemini ya da NFC Tools benzeri bir uygulamayı kullanın;
etikete `nfc.html` sayfasındaki adresi yazmanız yeterlidir. Yazılmış etiketi
**okumak** iPhone XS ve sonrasında arka planda çalışır, ek uygulama gerekmez.

## QR kod

NFC'siz telefonlar için aynı adres QR koda gömülüdür:

- Sayfadaki **QR kod** düğmesi kodu ekranda gösterir ve PNG olarak indirir.
- `assets/qr-kartvizit.svg` baskı için hazır vektörel kod
  (`node tools/uret.mjs` ile yeniden üretilir).

## Dosya düzeni

| Dosya | Görevi |
| --- | --- |
| `index.html` | Kartvizit sayfası (NFC etiketinin işaret ettiği adres) |
| `nfc.html` | Etiket yazma / okuma / kilitleme aracı |
| `assets/js/config.js` | Tüm içerik ve iletişim bilgileri |
| `assets/js/app.js` | Kartvizit arayüzünü config'ten oluşturur |
| `assets/js/nfc.js` | Web NFC yazma, okuma, boyut hesabı |
| `assets/js/qr.js` | Bağımlılıksız QR üreteci (byte modu, sürüm 1–10) |
| `assets/js/vcard.js` | vCard 3.0 oluşturucu (RFC 6350 katlamalı) |
| `assets/css/style.css` | Tema ve mobil öncelikli düzen |
| `kartvizit.vcf` | "Rehbere ekle" düğmesinin indirdiği dosya (üretilir) |
| `assets/qr-kartvizit.svg` | Baskıya uygun QR kod (üretilir) |
| `tools/uret.mjs` | Üretilen dosyaları oluşturur |
| `tools/testler.mjs` | Bağımlılıksız testler |
| `tools/capraz-dogrulama.py` | İsteğe bağlı çapraz doğrulama (segno + zxing-cpp) |

## Testler

```bash
node tools/testler.mjs
```

Biçim bilgisi (BCH 15,5) tablosunun 32 kombinasyonunu, sürüm seçimini, matris
geometrisini, bulucu desenlerini, kapasite hatasını, referans matris özetlerini
ve vCard kurallarını doğrular. Bağımlılık gerektirmez.

İsteğe bağlı çapraz doğrulama (bağımsız kütüphanelerle):

```bash
pip install segno zxing-cpp opencv-python-headless numpy
python3 tools/capraz-dogrulama.py
```

Üretilen kodlar `zxing-cpp` ile taranıp geri okunur; veri kapasiteyi tam
doldurduğunda matrisler referans uygulama `segno` ile bit bit karşılaştırılır.
Dolgu baytı bulunan durumlarda segno, bayt sınırına oturmuş bit akışına
fazladan bir sıfır bayt eklediğinden matrisler kasıtlı olarak farklıdır; her
iki sembol de geçerli ve okunabilirdir.

## Teknik notlar

- **QR üreteci:** ISO/IEC 18004 byte modu, sürüm 1–10, L/M/Q/H hata düzeltme,
  8 maskenin tamamı ceza puanına göre değerlendirilir (N1–N4, 2015 sürümündeki
  1:1:3:1:1 kuralı dâhil). Reed–Solomon kodlaması GF(256), 0x11D ilkel polinomu.
  Maske değerlendirmesi, standarda uygun olarak biçim ve sürüm bilgisi
  yazılmadan önce yapılır.
- **vCard:** sürüm 3.0 (Android ve iOS rehberleriyle en uyumlu olan sürüm),
  CRLF satır sonları, 75 oktetlik satır katlama, virgül/noktalı virgül kaçışı.
- **Gizlilik:** sayfa hiçbir dış servise istek atmaz, çerez ve izleyici yoktur.
  Kanal ayrımı yalnızca adresteki `?kaynak=nfc|qr|paylasim` parametresiyle
  görsel olarak yapılır.
- **Erişilebilirlik:** 52 px'lik dokunma hedefleri, klavye odak halkaları,
  `prefers-reduced-motion` desteği, ekran okuyucu için `role="status"` günlüğü.
