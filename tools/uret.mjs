#!/usr/bin/env node
/**
 * uret.mjs — config.js'ten kartvizit dosyalarını üretir.
 *
 *   node tools/uret.mjs
 *
 * Üretilenler:
 *   kartvizit.vcf            → "Rehbere ekle" düğmesinin indirdiği dosya
 *   assets/qr-kartvizit.svg  → baskıya uygun QR kod (kartvizit adresi)
 */
import { createRequire } from 'node:module';
import { writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const require = createRequire(import.meta.url);
const kok = join(dirname(fileURLToPath(import.meta.url)), '..');

const cfg = require(join(kok, 'assets/js/config.js'));
const VCard = require(join(kok, 'assets/js/vcard.js'));
const QR = require(join(kok, 'assets/js/qr.js'));

function adres(kanal) {
  const temel = String(cfg.site.url || '').split('#')[0];
  if (!temel) throw new Error('config.js içinde site.url tanımlı değil.');
  return kanal ? temel + (temel.includes('?') ? '&' : '?') + 'kaynak=' + kanal : temel;
}

const vcf = VCard.build(cfg);
writeFileSync(join(kok, 'kartvizit.vcf'), vcf, 'utf8');

const qrAdresi = adres('qr');
const svg = QR.toSvg(qrAdresi, { level: 'M', quietZone: 4, dark: '#0b0c10', light: '#ffffff' });
writeFileSync(join(kok, 'assets/qr-kartvizit.svg'), svg + '\n', 'utf8');

const qr = QR.encode(qrAdresi, { level: 'M' });

console.log('kartvizit.vcf            → %d bayt', VCard.bayt(vcf));
console.log('assets/qr-kartvizit.svg  → sürüm %d, %dx%d modül, maske %d (%s)',
  qr.version, qr.size, qr.size, qr.mask, qrAdresi);

if (!cfg.dogrulanmisBilgiler) {
  console.log('\nUYARI: config.js hâlâ örnek verilerle dolu. Gerçek bilgileri girip');
  console.log('       dogrulanmisBilgiler alanını true yapın, sonra bu betiği tekrar çalıştırın.');
}
