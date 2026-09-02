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

console.log('\n%d test geçti, %d test başarısız.', basarili, hatalar.length);
process.exit(hatalar.length ? 1 : 0);
