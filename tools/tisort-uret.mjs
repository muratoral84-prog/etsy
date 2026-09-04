#!/usr/bin/env node
/**
 * tisort-uret.mjs — Baskıya hazır tişört tasarımlarını üretir.
 *
 *   node tools/tisort-uret.mjs
 *
 * Üretilenler: urun/tisort/tasarim/<tasarım>-<palet>.svg
 */
import { writeFileSync, mkdirSync } from 'node:fs';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const require = createRequire(import.meta.url);
const kok = join(dirname(fileURLToPath(import.meta.url)), '..');
const D = require(join(kok, 'assets/js/tasarimlar.js'));

const hedef = join(kok, 'urun/tisort/tasarim');
mkdirSync(hedef, { recursive: true });

for (const tasarim of D.TASARIMLAR) {
  for (const palet of Object.keys(D.PALETLER)) {
    const svg = D.toSvg(tasarim.kod, { palet });
    const dosya = `${tasarim.kod}-${palet}.svg`;
    writeFileSync(join(hedef, dosya), svg + '\n', 'utf8');
    console.log('urun/tisort/tasarim/%s → %d bayt (%s)', dosya, Buffer.byteLength(svg), D.PALETLER[palet].ad);
  }
}

const { en, boy, dpi } = D.TUVAL;
console.log('\n%d tasarım x %d palet — %dx%d px (%sx%s inç @ %d dpi)',
  D.TASARIMLAR.length, Object.keys(D.PALETLER).length, en, boy, en / dpi, boy / dpi, dpi);
