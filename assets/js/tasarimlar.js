/*!
 * tasarimlar.js — Tişört baskı tasarımları (tisort.js alfabesini kullanır).
 *
 * Her tasarım 3600x4800 px tuvale çizilir: 12x16 inç @ 300 dpi, yani DTG
 * baskıda yetişkin bedenlerin standart ön baskı alanı. Tasarımlar iki
 * mürekkeple çalışır (ana renk + vurgu), bu yüzden serigrafiye de uygundur.
 *
 * Telif notu: tüm çizimler bu depoda sıfırdan üretilmiştir. Hiçbir gerçek
 * kişinin adı, portresi, imzası, forma numarası-isim birleşimi veya tescilli
 * marka/logo kullanılmaz — jenerik basketbol tipografisi ve geometrisi.
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(require('./tisort.js'));
  else root.TASARIMLAR = factory(root.TISORT);
})(typeof globalThis !== 'undefined' ? globalThis : this, function (T) {
  'use strict';

  var TUVAL = { en: 3600, boy: 4800, dpi: 300 };

  var PALETLER = {
    'acik-zemin': { ad: 'Açık zeminli tişört (beyaz, bej, gri)', kisaAd: 'koyu mürekkep', murekkep: '#12141A', vurgu: '#E4572E' },
    'koyu-zemin': { ad: 'Koyu zeminli tişört (siyah, lacivert, haki)', kisaAd: 'açık mürekkep', murekkep: '#FFFFFF', vurgu: '#FF7A18' }
  };

  function s2(n) { return String(Math.round(n * 100) / 100); }

  /** Blok alfabeyle yazı öğesi. */
  function metin(icerik, o) {
    var y = T.yaziYolu(icerik, o);
    return '<path d="' + y.d + '" fill="' + o.renk + '"/>';
  }

  /** Basketbol topu: vurgu renginde gövde, mürekkep dikişler. */
  function top(cx, cy, yaricap, palet, kalinlik) {
    var k = kalinlik == null ? Math.max(12, yaricap * 0.055) : kalinlik;
    var r = yaricap - k / 2;
    var c = [];
    c.push('<circle cx="' + s2(cx) + '" cy="' + s2(cy) + '" r="' + s2(r) + '" fill="' + palet.vurgu + '"/>');
    c.push('<g fill="none" stroke="' + palet.murekkep + '" stroke-width="' + s2(k) + '" stroke-linecap="round">');
    c.push('<circle cx="' + s2(cx) + '" cy="' + s2(cy) + '" r="' + s2(r) + '"/>');
    c.push('<path d="M' + s2(cx - r) + ' ' + s2(cy) + 'H' + s2(cx + r) + '"/>');
    c.push('<path d="M' + s2(cx) + ' ' + s2(cy - r) + 'V' + s2(cy + r) + '"/>');
    c.push('<path d="M' + s2(cx) + ' ' + s2(cy - r) + 'Q' + s2(cx - r * 1.12) + ' ' + s2(cy) + ' ' + s2(cx) + ' ' + s2(cy + r) + '"/>');
    c.push('<path d="M' + s2(cx) + ' ' + s2(cy - r) + 'Q' + s2(cx + r * 1.12) + ' ' + s2(cy) + ' ' + s2(cx) + ' ' + s2(cy + r) + '"/>');
    c.push('</g>');
    return c.join('');
  }

  /** Pota filesi: üst elipsten alt elipse çapraz örgü. */
  function file(cx, cy, rx, ry, altCy, altRx, altRy, adet, renk, kalinlik) {
    function nokta(r1, r2, y, i) {
      var t = (i / adet) * Math.PI * 2;
      return [cx + r1 * Math.cos(t), y + r2 * Math.sin(t)];
    }
    var c = ['<g fill="none" stroke="' + renk + '" stroke-width="' + s2(kalinlik) + '" stroke-linecap="round">'];
    for (var i = 0; i < adet; i++) {
      var u = nokta(rx, ry, cy, i);
      var a1 = nokta(altRx, altRy, altCy, i + 0.5);
      var a2 = nokta(altRx, altRy, altCy, i - 0.5);
      c.push('<path d="M' + s2(u[0]) + ' ' + s2(u[1]) + 'L' + s2(a1[0]) + ' ' + s2(a1[1]) + '"/>');
      c.push('<path d="M' + s2(u[0]) + ' ' + s2(u[1]) + 'L' + s2(a2[0]) + ' ' + s2(a2[1]) + '"/>');
    }
    c.push('<ellipse cx="' + s2(cx) + '" cy="' + s2(altCy) + '" rx="' + s2(altRx) + '" ry="' + s2(altRy) + '"/>');
    c.push('</g>');
    return c.join('');
  }

  var TASARIMLAR = [
    {
      kod: 'hang-time',
      ad: 'Hang Time',
      aciklama: 'Havalanan topun yörüngesi ve iki satır blok tipografi.',
      metinler: ['HANG', 'TIME', 'HARDWOOD CLASSICS'],
      ciz: function (p) {
        var c = [];
        c.push('<g fill="none" stroke="' + p.vurgu + '" stroke-width="34" stroke-linecap="round" stroke-dasharray="130 96">');
        c.push('<path d="M240 2060Q640 900 1160 640"/>');
        c.push('<path d="M2440 640Q2960 900 3360 2060"/>');
        c.push('</g>');
        c.push(top(1800, 1080, 560, p));
        c.push(metin('HANG', { en: 2900, x: 1800, y: 1880, hiza: 'orta', renk: p.murekkep }));
        c.push(metin('TIME', { en: 2900, x: 1800, y: 2830, hiza: 'orta', renk: p.murekkep }));
        c.push('<rect x="360" y="3880" width="740" height="34" fill="' + p.vurgu + '"/>');
        c.push('<rect x="2500" y="3880" width="740" height="34" fill="' + p.vurgu + '"/>');
        c.push(metin('HARDWOOD CLASSICS', { en: 2200, x: 1800, y: 3820, hiza: 'orta', renk: p.murekkep }));
        return c.join('');
      }
    },
    {
      kod: 'yirmi-uc',
      ad: 'Yirmi Üç',
      aciklama: 'Halka içinde dev 23 numara, üstte ve altta blok yazı.',
      metinler: ['HARDWOOD', '23', 'GREATEST OF ALL TIME', 'TWENTY THREE'],
      ciz: function (p) {
        var c = [];
        c.push(metin('HARDWOOD', { en: 2700, x: 1800, y: 480, hiza: 'orta', renk: p.murekkep }));
        c.push('<rect x="450" y="980" width="2700" height="40" fill="' + p.vurgu + '"/>');
        c.push('<circle cx="1800" cy="2300" r="1020" fill="none" stroke="' + p.murekkep + '" stroke-width="72"/>');
        c.push('<circle cx="1800" cy="2300" r="1136" fill="none" stroke="' + p.vurgu + '" stroke-width="18" stroke-dasharray="70 54"/>');
        c.push(metin('23', { en: 1400, x: 1800, y: 1866, hiza: 'orta', renk: p.murekkep }));
        c.push(metin('GREATEST OF ALL TIME', { en: 2200, x: 1800, y: 3560, hiza: 'orta', renk: p.vurgu }));
        c.push(metin('TWENTY THREE', { en: 2400, x: 1800, y: 3810, hiza: 'orta', renk: p.murekkep }));
        return c.join('');
      }
    },
    {
      kod: 'pota',
      ad: 'Pota',
      aciklama: 'Panya, çember, file ve fileden düşen top; altında iki satır yazı.',
      metinler: ['NOTHING', 'BUT NET'],
      ciz: function (p) {
        var c = [];
        c.push('<rect x="850" y="520" width="1900" height="1220" rx="24" fill="none" stroke="' + p.murekkep + '" stroke-width="52"/>');
        c.push('<rect x="1440" y="1080" width="720" height="520" rx="12" fill="none" stroke="' + p.vurgu + '" stroke-width="44"/>');
        c.push('<path d="M1560 1740H2040" stroke="' + p.murekkep + '" stroke-width="44" stroke-linecap="round"/>');
        c.push('<ellipse cx="1800" cy="1860" rx="470" ry="120" fill="none" stroke="' + p.vurgu + '" stroke-width="54"/>');
        c.push(file(1800, 1860, 470, 120, 2560, 250, 64, 12, p.murekkep, 20));
        c.push(top(1800, 2990, 250, p));
        c.push(metin('NOTHING', { en: 2700, x: 1800, y: 3400, hiza: 'orta', renk: p.murekkep }));
        c.push(metin('BUT NET', { en: 2700, x: 1800, y: 3930, hiza: 'orta', renk: p.vurgu }));
        return c.join('');
      }
    }
  ];

  function bul(kod) {
    for (var i = 0; i < TASARIMLAR.length; i++) if (TASARIMLAR[i].kod === kod) return TASARIMLAR[i];
    throw new Error('Bilinmeyen tasarım: ' + kod);
  }

  /**
   * Baskıya hazır SVG döndürür.
   * secenekler: { palet: 'acik-zemin'|'koyu-zemin', zemin: '#rrggbb' (yalnız önizleme) }
   */
  function toSvg(kod, secenekler) {
    var o = secenekler || {};
    var t = bul(kod);
    var paletKodu = o.palet || 'acik-zemin';
    var p = PALETLER[paletKodu];
    if (!p) throw new Error('Bilinmeyen palet: ' + paletKodu);

    var bas = '<svg xmlns="http://www.w3.org/2000/svg" width="' + (TUVAL.en / TUVAL.dpi) + 'in" height="' +
      (TUVAL.boy / TUVAL.dpi) + 'in" viewBox="0 0 ' + TUVAL.en + ' ' + TUVAL.boy + '" role="img">' +
      '<title>' + t.ad + ' — basketbol temalı tişört baskısı</title>' +
      '<desc>' + t.aciklama + ' ' + p.ad + '. ' + (TUVAL.en / TUVAL.dpi) + 'x' + (TUVAL.boy / TUVAL.dpi) +
      ' inç, ' + TUVAL.dpi + ' dpi. Özgün tasarım; hiçbir marka veya kişi hakkı içermez.</desc>';
    var zemin = o.zemin ? '<rect width="' + TUVAL.en + '" height="' + TUVAL.boy + '" fill="' + o.zemin + '"/>' : '';
    return bas + zemin + t.ciz(p) + '</svg>';
  }

  return { TUVAL: TUVAL, PALETLER: PALETLER, TASARIMLAR: TASARIMLAR, bul: bul, toSvg: toSvg };
});
