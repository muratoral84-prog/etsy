#!/usr/bin/env node
/**
 * testler.mjs — QR üreteci ve vCard oluşturucu için bağımlılıksız testler.
 *
 *   node tools/testler.mjs
 *
 * Beklenen değerler ISO/IEC 18004 tablolarından ve referans uygulama
 * (segno 1.6.6) çıktısından alınmıştır; ayrıca üretilen kodlar zxing-cpp ile
 * çözülerek doğrulanmıştır (bkz. README).
 */
import { createRequire } from 'node:module';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const require = createRequire(import.meta.url);
const kok = join(dirname(fileURLToPath(import.meta.url)), '..');
const QR = require(join(kok, 'assets/js/qr.js'));
const VCard = require(join(kok, 'assets/js/vcard.js'));
const cfg = require(join(kok, 'assets/js/config.js'));
const T = require(join(kok, 'assets/js/tisort.js'));
const Tasarim = require(join(kok, 'assets/js/tasarimlar.js'));

let basarili = 0;
const hatalar = [];

function test(ad, fn) {
  try {
    fn();
    basarili++;
    console.log('  ✓ ' + ad);
  } catch (e) {
    hatalar.push(ad + ': ' + e.message);
    console.log('  ✗ ' + ad + ' — ' + e.message);
  }
}

function esit(bulunan, beklenen, mesaj) {
  const a = JSON.stringify(bulunan), b = JSON.stringify(beklenen);
  if (a !== b) throw new Error((mesaj ? mesaj + ' — ' : '') + 'beklenen ' + b + ', bulunan ' + a);
}

function dogru(kosul, mesaj) {
  if (!kosul) throw new Error(mesaj || 'koşul sağlanmadı');
}

function ozet(text, level) {
  const qr = QR.encode(text, { level });
  return {
    version: qr.version,
    mask: qr.mask,
    hash: createHash('sha256').update(qr.modules.map((r) => r.join('')).join('')).digest('hex').slice(0, 32)
  };
}

console.log('QR üreteci');

// ISO/IEC 18004 Tablo 25 — 32 biçim bilgisi dizisi (seviye<<3 | maske)
const BICIM_BILGISI = [
  21522, 20773, 24188, 23371, 17913, 16590, 20375, 19104,
  30660, 29427, 32170, 30877, 26159, 25368, 27713, 26998,
  5769, 5054, 7399, 6608, 1890, 597, 3340, 2107,
  13663, 12392, 16177, 14854, 9396, 8579, 11994, 11245
];

test('biçim bilgisi (BCH 15,5) 32 kombinasyonun tamamında doğru', () => {
  const seviyeBiti = { L: 1, M: 0, Q: 3, H: 2 };
  for (const seviye of ['L', 'M', 'Q', 'H']) {
    for (let maske = 0; maske < 8; maske++) {
      // Biçim bitleri matriste (8,0)-(8,5) konumlarından geri okunur
      const qr = QR.encode('A', { level: seviye, mask: maske });
      let okunan = 0;
      for (let i = 0; i <= 5; i++) okunan |= qr.modules[i][8] << i;
      okunan |= qr.modules[7][8] << 6;
      okunan |= qr.modules[8][8] << 7;
      okunan |= qr.modules[8][7] << 8;
      for (let j = 9; j < 15; j++) okunan |= qr.modules[8][14 - j] << j;
      esit(okunan, BICIM_BILGISI[(seviyeBiti[seviye] << 3) | maske], seviye + ' maske ' + maske);
    }
  }
});

test('sürüm seçimi veri uzunluğuna göre büyür', () => {
  esit(QR.encode('A'.repeat(17), { level: 'L' }).version, 1);
  esit(QR.encode('A'.repeat(18), { level: 'L' }).version, 2);
  esit(QR.encode('A'.repeat(32), { level: 'L' }).version, 2);
  esit(QR.encode('A'.repeat(33), { level: 'L' }).version, 3);
  esit(QR.encode('A'.repeat(7), { level: 'H' }).version, 1);
});

test('matris boyutu 4·sürüm + 17 kuralına uyar', () => {
  for (const uzunluk of [1, 20, 60, 120, 200]) {
    const qr = QR.encode('x'.repeat(uzunluk), { level: 'L' });
    esit(qr.size, qr.version * 4 + 17);
    esit(qr.modules.length, qr.size);
    esit(qr.modules[0].length, qr.size);
  }
});

test('bulucu desenleri (finder) üç köşede doğru', () => {
  const qr = QR.encode('https://muratoralmedya.com', { level: 'M' });
  const s = qr.size;
  for (const [r0, c0] of [[0, 0], [0, s - 7], [s - 7, 0]]) {
    esit(qr.modules[r0][c0], 1, 'köşe dolu değil');
    esit(qr.modules[r0 + 1][c0 + 1], 0, 'iç halka beyaz değil');
    esit(qr.modules[r0 + 3][c0 + 3], 1, 'çekirdek koyu değil');
  }
  esit(qr.modules[6][8], 1, 'zamanlama deseni hatalı');
  esit(qr.modules[6][9], 0, 'zamanlama deseni hatalı');
  esit(qr.modules[qr.size - 8][8], 1, 'koyu modül eksik');
});

test('UTF-8 karakterler bayt olarak sayılır', () => {
  // "ğ" 2 bayt: 9 karakterlik metin 1. sürüm-H sınırını (7 bayt) aşar
  dogru(QR.encode('ğüşiöç', { level: 'H' }).version >= 2, 'çok baytlı karakter sürümü artırmalı');
});

test('kapasite aşımında anlaşılır hata verir', () => {
  let hata = null;
  try { QR.encode('A'.repeat(300), { level: 'H' }); } catch (e) { hata = e; }
  dogru(hata !== null, 'hata bekleniyordu');
  dogru(/Veri cok uzun/.test(hata.message), 'hata mesajı beklenen metni içermiyor: ' + hata.message);
});

test('referans matrisleri değişmedi (segno 1.6.6 ile birebir)', () => {
  esit(ozet('https://muratoral84-prog.github.io/etsy/?kaynak=qr', 'M'),
    { version: 4, mask: 3, hash: 'e51eb4c20959432cacae1a338960106e' });
  esit(ozet('MURAT ORAL', 'H'),
    { version: 2, mask: 4, hash: 'dbd973edcb2b9e2de77dc958499b9f73' });
  esit(ozet('https://muratoralmedya.com', 'Q'),
    { version: 3, mask: 4, hash: '2c45f006f8105a27d06863ebf1e22fb3' });
});

test('SVG çıktısı sessiz bölge (quiet zone) içerir', () => {
  const qr = QR.encode('test', { level: 'M' });
  const svg = QR.toSvg('test', { level: 'M', quietZone: 4 });
  dogru(svg.startsWith('<svg '), 'svg etiketiyle başlamalı');
  dogru(svg.includes('viewBox="0 0 ' + (qr.size + 8) + ' ' + (qr.size + 8) + '"'), 'sessiz bölge 4 modül olmalı');
});

console.log('\nvCard');

test('vCard zorunlu alanları ve CRLF satır sonlarını içerir', () => {
  const vcf = VCard.build(cfg);
  dogru(vcf.startsWith('BEGIN:VCARD\r\nVERSION:3.0\r\n'), 'başlık hatalı');
  dogru(vcf.endsWith('END:VCARD\r\n'), 'kapanış hatalı');
  dogru(vcf.includes('FN:' + cfg.kisi.ad), 'FN eksik');
  dogru(vcf.includes('ORG:' + cfg.marka.ad), 'ORG eksik');
  dogru(/\r\nTEL;TYPE=CELL,VOICE:/.test(vcf), 'TEL eksik');
  dogru(/\r\nEMAIL;TYPE=INTERNET,WORK:/.test(vcf), 'EMAIL eksik');
});

test('vCard satırları 75 okteti aşmaz (RFC 6350 katlama)', () => {
  const vcf = VCard.build({
    ...cfg,
    marka: { ...cfg.marka, slogan: 'Çok uzun bir slogan '.repeat(12) }
  });
  for (const satir of vcf.split('\r\n')) {
    dogru(Buffer.byteLength(satir, 'utf8') <= 75, 'satır çok uzun: ' + Buffer.byteLength(satir, 'utf8') + ' bayt');
  }
});

test('vCard özel karakterleri kaçışlar', () => {
  const vcf = VCard.build({
    ...cfg,
    kisi: { ...cfg.kisi, ad: 'Murat, Oral; Test' }
  });
  dogru(vcf.includes('FN:Murat\\, Oral\; Test'), 'virgül/noktalı virgül kaçışlanmadı');
});

console.log('\nYapılandırma');

test('config.js gerekli alanları içerir', () => {
  for (const yol of ['site.url', 'marka.ad', 'kisi.ad', 'iletisim.telefon', 'nfc.varsayilanKayit']) {
    const deger = yol.split('.').reduce((o, k) => (o || {})[k], cfg);
    dogru(deger, yol + ' tanımlı değil');
  }
  dogru(/^https?:\/\//.test(cfg.site.url), 'site.url http(s) ile başlamalı');
});

console.log('\nTişört tasarımları');

test('alfabe tasarımlarda geçen tüm karakterleri kapsar', () => {
  const kullanilan = new Set();
  for (const t of Tasarim.TASARIMLAR) {
    for (const metin of t.metinler || []) {
      for (const ch of T.normalize(metin)) if (ch !== ' ') kullanilan.add(ch);
    }
  }
  for (const ch of 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') {
    dogru(T.HARFLER[ch], ch + ' alfabede yok');
  }
  for (const ch of kullanilan) dogru(T.HARFLER[ch], ch + ' alfabede yok');
});

test('Türkçe harfler alfabedeki karşılıklarına indirgenir', () => {
  esit(T.normalize('şığüöç'), 'SIGUOC');
  esit(T.normalize('İstanbul'), 'ISTANBUL');
});

test('metin eni harf + aralık toplamına eşit', () => {
  // iki harf = 2 kutu + 1 aralık, boşluk kendi eninde
  esit(T.birimEni('AB'), 2 * T.EN + T.ARA);
  esit(T.birimEni('A B'), 2 * T.EN + T.BOSLUK + 2 * T.ARA);
  esit(T.birimEni(''), 0);
});

// SVG yol verisinin sınırlayıcı kutusu (M/L/H/V/Q/Z komutları yeterli).
function kutu(d) {
  const parcalar = d.match(/[MLHVQZ]|-?\d+(?:\.\d+)?/g) || [];
  const s = { xMin: Infinity, yMin: Infinity, xMax: -Infinity, yMax: -Infinity };
  let komut = null, x = 0, y = 0, yigin = [];
  const isle = (px, py) => {
    x = px; y = py;
    s.xMin = Math.min(s.xMin, x); s.xMax = Math.max(s.xMax, x);
    s.yMin = Math.min(s.yMin, y); s.yMax = Math.max(s.yMax, y);
  };
  for (const parca of parcalar) {
    if (/[A-Z]/.test(parca)) { komut = parca; yigin = []; continue; }
    yigin.push(Number(parca));
    if ((komut === 'M' || komut === 'L') && yigin.length === 2) { isle(yigin[0], yigin[1]); yigin = []; }
    else if (komut === 'H') { isle(yigin[0], y); yigin = []; }
    else if (komut === 'V') { isle(x, yigin[0]); yigin = []; }
    else if (komut === 'Q' && yigin.length === 4) { isle(yigin[0], yigin[1]); isle(yigin[2], yigin[3]); yigin = []; }
  }
  return s;
}

test('istenen ene göre ölçeklenir ve ortalanır', () => {
  const y = T.yaziYolu('HANG', { en: 1000, x: 500, hiza: 'orta', y: 0 });
  esit(Math.round(y.en), 1000);
  const k = kutu(y.d);
  esit(Math.round(k.xMin), 0, 'sol kenar');
  esit(Math.round(k.xMax), 1000, 'sağ kenar');
  esit(Math.round(k.yMin), 0, 'üst kenar');
  esit(Math.round(k.yMax), Math.round(y.boy), 'alt kenar');
});

test('tüm gövdeler aynı sarım yönünde (delik açmaz)', () => {
  // Ters yönlü bir çokgen nonzero kuralında üstteki dikdörtgeni deler.
  const alan = (n) => n.reduce((t, a, i) => {
    const b = n[(i + 1) % n.length];
    return t + a[0] * b[1] - b[0] * a[1];
  }, 0);
  dogru(alan(T.bant(0, 0, 100, 100, 20).v) > 0, 'soldan sağa bant ters');
  dogru(alan(T.bant(100, 100, 0, 0, 20).v) > 0, 'sağdan sola bant ters');
  for (const [ad, sekiller] of Object.entries(T.HARFLER)) {
    for (const sekil of sekiller) {
      if (sekil.t === 'p') dogru(alan(sekil.v) > 0, ad + ' harfinde ters çokgen');
    }
  }
});

test('her glif kendi kutusunun içinde kalır', () => {
  for (const [ad, sekiller] of Object.entries(T.HARFLER)) {
    for (const sekil of sekiller) {
      const noktalar = sekil.t === 'r'
        ? [[sekil.v[0], sekil.v[1]], [sekil.v[0] + sekil.v[2], sekil.v[1] + sekil.v[3]]]
        : sekil.v;
      for (const [x, y] of noktalar) {
        dogru(x >= 0 && x <= T.EN, ad + ' x kutu dışında: ' + x);
        dogru(y >= 0 && y <= T.BOY, ad + ' y kutu dışında: ' + y);
      }
    }
  }
});

test('bilinmeyen karakter sessizce yutulmaz', () => {
  let hata = null;
  try { T.yaziYolu('A@B', { olcek: 1 }); } catch (e) { hata = e; }
  dogru(hata && /@/.test(hata.message), 'hata fırlatılmadı');
});

test('her tasarım her palette geçerli SVG üretir', () => {
  for (const t of Tasarim.TASARIMLAR) {
    for (const palet of Object.keys(Tasarim.PALETLER)) {
      const svg = Tasarim.toSvg(t.kod, { palet });
      dogru(!/NaN|undefined|null/.test(svg), t.kod + '/' + palet + ' geçersiz sayı içeriyor');
      dogru(svg.startsWith('<svg ') && svg.endsWith('</svg>'), t.kod + ' SVG kökü bozuk');
      dogru(svg.includes('viewBox="0 0 3600 4800"'), t.kod + ' tuval ölçüsü yanlış');
      dogru(svg.includes(Tasarim.PALETLER[palet].murekkep), t.kod + ' ana mürekkep kullanılmamış');
      dogru(svg.includes(Tasarim.PALETLER[palet].vurgu), t.kod + ' vurgu rengi kullanılmamış');
      const acik = (svg.match(/</g) || []).length, kapali = (svg.match(/>/g) || []).length;
      esit(acik, kapali, t.kod + ' etiketleri dengesiz');
    }
  }
});

test('çizimler baskı alanının dışına taşmaz', () => {
  for (const t of Tasarim.TASARIMLAR) {
    const svg = Tasarim.toSvg(t.kod, { palet: 'acik-zemin' });
    for (const [, d] of svg.matchAll(/ d="([^"]+)"/g)) {
      const k = kutu(d);
      dogru(k.xMin >= 0 && k.xMax <= Tasarim.TUVAL.en, t.kod + ' x taşması: ' + k.xMin + '..' + k.xMax);
      dogru(k.yMin >= 0 && k.yMax <= Tasarim.TUVAL.boy, t.kod + ' y taşması: ' + k.yMin + '..' + k.yMax);
    }
    // daire/elips/dikdörtgen öğeleri de tuval içinde kalmalı
    for (const [, cx, cy, r] of svg.matchAll(/<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"/g)) {
      dogru(+cx - +r >= 0 && +cx + +r <= Tasarim.TUVAL.en, t.kod + ' daire x taşması');
      dogru(+cy - +r >= 0 && +cy + +r <= Tasarim.TUVAL.boy, t.kod + ' daire y taşması');
    }
  }
});

test('baskı ölçüsü 12x16 inç / 300 dpi', () => {
  esit(Tasarim.TUVAL.en / Tasarim.TUVAL.dpi, 12);
  esit(Tasarim.TUVAL.boy / Tasarim.TUVAL.dpi, 16);
  const svg = Tasarim.toSvg(Tasarim.TASARIMLAR[0].kod, {});
  dogru(svg.includes('width="12in"') && svg.includes('height="16in"'), 'inç ölçüsü yazılmamış');
});

test('bilinmeyen tasarım veya palet hata verir', () => {
  let a = null, b = null;
  try { Tasarim.toSvg('yok', {}); } catch (e) { a = e; }
  try { Tasarim.toSvg(Tasarim.TASARIMLAR[0].kod, { palet: 'yok' }); } catch (e) { b = e; }
  dogru(a && b, 'hata fırlatılmadı');
});

console.log('\n%d test geçti, %d test başarısız.', basarili, hatalar.length);
process.exit(hatalar.length ? 1 : 0);
