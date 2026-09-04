/*!
 * tisort.js — Bağımlılıksız tişört baskı tasarımı üreteci.
 *
 * Dışarıdan yazı tipi indirilmez: harfler 100x140 birimlik bir ızgara üzerine
 * kurulu blok/şablon alfabeden vektör yola çevrilir. Böylece üretilen SVG'de
 * <text> kalmaz, baskıcıda yazı tipi eksikliği sorunu çıkmaz.
 *
 * Tuval 3600x4800 px = 12x16 inç @ 300 dpi (DTG baskı alanı).
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.TISORT = factory();
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  /* ---------------------------------------------------------------- alfabe */

  var EN = 100;      // glif kutusu eni
  var BOY = 140;     // glif kutusu boyu
  var K = 26;        // gövde kalınlığı
  var ORT = 57;      // orta bant üst kenarı ((BOY - K) / 2)
  var ARA = 26;      // harf arası
  var BOSLUK = 70;   // boşluk karakterinin eni

  function r(x, y, w, h) { return { t: 'r', v: [x, y, w, h] }; }

  // Tüm gövdeler tek bir <path> içinde birleştiği için sarım yönü aynı olmalı:
  // ters yönlü bir çokgen "nonzero" kuralında üstteki dikdörtgeni deler.
  function p(n) {
    var alan = 0;
    for (var i = 0; i < n.length; i++) {
      var a = n[i], b = n[(i + 1) % n.length];
      alan += a[0] * b[1] - b[0] * a[1];
    }
    return { t: 'p', v: alan < 0 ? n.slice().reverse() : n };
  }

  /** (x1,y1)-(x2,y2) arasında k kalınlığında bant — çapraz gövdeler için. */
  function bant(x1, y1, x2, y2, k) {
    var dx = x2 - x1, dy = y2 - y1, u = Math.sqrt(dx * dx + dy * dy) || 1;
    var ox = (-dy / u) * (k / 2), oy = (dx / u) * (k / 2);
    return p([[x1 + ox, y1 + oy], [x2 + ox, y2 + oy], [x2 - ox, y2 - oy], [x1 - ox, y1 - oy]]);
  }

  var HARFLER = {
    A: [bant(14, BOY - 3, 41, 12, 26), bant(EN - 14, BOY - 3, EN - 41, 12, 26), r(26, 0, EN - 52, 32), r(17, ORT + 24, EN - 34, K)],
    B: [r(0, 0, K, BOY), r(0, 0, EN, K), r(EN - K, 0, K, 83), r(0, ORT, EN, K), r(EN - K, ORT, K, 83), r(0, BOY - K, EN, K)],
    C: [r(0, 0, EN, K), r(0, 0, K, BOY), r(0, BOY - K, EN, K)],
    D: [r(0, 0, K, BOY), r(0, 0, EN, K), r(0, BOY - K, EN, K), r(EN - K, K, K, BOY - 2 * K)],
    E: [r(0, 0, K, BOY), r(0, 0, EN, K), r(0, ORT, 80, K), r(0, BOY - K, EN, K)],
    F: [r(0, 0, K, BOY), r(0, 0, EN, K), r(0, ORT, 80, K)],
    G: [r(0, 0, EN, K), r(0, 0, K, BOY), r(0, BOY - K, EN, K), r(EN - K, ORT, K, 83), r(52, ORT, EN - 52, K)],
    H: [r(0, 0, K, BOY), r(EN - K, 0, K, BOY), r(K, ORT, EN - 2 * K, K)],
    I: [r(37, 0, K, BOY)],
    J: [r(EN - K, 0, K, BOY), r(0, BOY - K, EN, K), r(0, 83, K, ORT)],
    K: [r(0, 0, K, BOY), bant(8, 70, EN - 14, 16, 28), bant(8, 70, EN - 14, BOY - 16, 28), r(16, 52, 26, 36)],
    L: [r(0, 0, K, BOY), r(0, BOY - K, EN, K)],
    M: [r(0, 0, K, BOY), r(EN - K, 0, K, BOY), bant(13, 9, 50, 96, 28), bant(EN - 13, 9, 50, 96, 28), r(36, 66, 28, 34)],
    N: [r(0, 0, K, BOY), r(EN - K, 0, K, BOY), bant(15, 12, EN - 15, BOY - 12, 32)],
    O: [r(0, 0, EN, K), r(0, BOY - K, EN, K), r(0, 0, K, BOY), r(EN - K, 0, K, BOY)],
    P: [r(0, 0, K, BOY), r(0, 0, EN, K), r(EN - K, 0, K, 83), r(0, ORT, EN, K)],
    Q: [r(0, 0, EN, K), r(0, BOY - K, EN, K), r(0, 0, K, BOY), r(EN - K, 0, K, BOY), bant(56, 82, EN - 14, BOY - 10, 26)],
    R: [r(0, 0, K, BOY), r(0, 0, EN, K), r(EN - K, 0, K, 83), r(0, ORT, EN, K), bant(52, 72, 86, BOY - 8, 28)],
    S: [r(0, 0, EN, K), r(0, 0, K, 83), r(0, ORT, EN, K), r(EN - K, ORT, K, 83), r(0, BOY - K, EN, K)],
    T: [r(0, 0, EN, K), r(37, 0, K, BOY)],
    U: [r(0, 0, K, BOY), r(EN - K, 0, K, BOY), r(0, BOY - K, EN, K)],
    V: [bant(15, 6, 50, BOY - 6, 28), bant(EN - 15, 6, 50, BOY - 6, 28), r(32, BOY - 46, 36, 46)],
    W: [r(0, 0, K, BOY), r(EN - K, 0, K, BOY), bant(13, BOY - 9, 50, 44, 28), bant(EN - 13, BOY - 9, 50, 44, 28), r(36, 42, 28, 34)],
    X: [bant(13, 8, EN - 13, BOY - 8, 28), bant(EN - 13, 8, 13, BOY - 8, 28)],
    Y: [bant(13, 8, 50, 84, 28), bant(EN - 13, 8, 50, 84, 28), r(37, 44, K, BOY - 44), r(31, 46, 38, 42)],
    Z: [r(0, 0, EN, K), r(0, BOY - K, EN, K), bant(EN - 15, 14, 15, BOY - 14, 32)],

    '0': [r(0, 0, EN, K), r(0, BOY - K, EN, K), r(0, 0, K, BOY), r(EN - K, 0, K, BOY)],
    '1': [r(37, 0, K, BOY), r(11, BOY - K, 78, K), bant(8, 34, 46, 16, 26)],
    '2': [r(0, 0, EN, K), r(EN - K, 0, K, 83), r(0, ORT, EN, K), r(0, ORT, K, 83), r(0, BOY - K, EN, K)],
    '3': [r(0, 0, EN, K), r(EN - K, 0, K, BOY), r(0, ORT, EN, K), r(0, BOY - K, EN, K)],
    '4': [r(0, 0, K, 83), r(EN - K, 0, K, BOY), r(0, ORT, EN, K)],
    '5': [r(0, 0, EN, K), r(0, 0, K, 83), r(0, ORT, EN, K), r(EN - K, ORT, K, 83), r(0, BOY - K, EN, K)],
    '6': [r(0, 0, EN, K), r(0, 0, K, BOY), r(0, ORT, EN, K), r(EN - K, ORT, K, 83), r(0, BOY - K, EN, K)],
    '7': [r(0, 0, EN, K), r(EN - K, 0, K, BOY)],
    '8': [r(0, 0, EN, K), r(0, ORT, EN, K), r(0, BOY - K, EN, K), r(0, 0, K, BOY), r(EN - K, 0, K, BOY)],
    '9': [r(0, 0, EN, K), r(0, 0, K, 83), r(EN - K, 0, K, BOY), r(0, ORT, EN, K)],

    '.': [r(37, BOY - K, K, K)],
    ',': [r(37, BOY - K, K, K), bant(56, BOY - 26, 36, BOY - 12, 22)],
    '-': [r(10, ORT, 80, K)],
    "'": [r(37, 0, K, 44)],
    '/': [bant(EN - 12, 8, 12, BOY - 8, 26)]
  };

  // Türkçe harfleri alfabedeki karşılıklarına indirger.
  var INDIRGE = { 'İ': 'I', 'I': 'I', 'Ş': 'S', 'Ğ': 'G', 'Ü': 'U', 'Ö': 'O', 'Ç': 'C' };

  function normalize(metin) {
    var s = String(metin).replace(/[İIŞĞÜÖÇ]/g, function (c) { return INDIRGE[c]; });
    return s.toUpperCase().replace(/[İIŞĞÜÖÇ]/g, function (c) { return INDIRGE[c]; });
  }

  function s2(n) { return String(Math.round(n * 100) / 100); }

  /** Metnin ölçeklenmemiş eni (birim). */
  function birimEni(metin) {
    var s = normalize(metin), toplam = 0;
    for (var i = 0; i < s.length; i++) {
      toplam += (s[i] === ' ' ? BOSLUK : EN) + ARA;
    }
    return Math.max(0, toplam - ARA);
  }

  /**
   * Metni tek bir SVG yol verisine çevirir.
   * secenekler: { en | olcek, x, y, hiza: 'sol'|'orta'|'sag' }
   * Döner: { d, en, boy, olcek }
   */
  function yaziYolu(metin, secenekler) {
    var o = secenekler || {};
    var s = normalize(metin);
    var birim = birimEni(s);
    var olcek = o.olcek != null ? o.olcek : (birim ? o.en / birim : 1);
    var toplamEn = birim * olcek;
    var x0 = (o.x || 0);
    if (o.hiza === 'orta') x0 -= toplamEn / 2;
    else if (o.hiza === 'sag') x0 -= toplamEn;
    var y0 = (o.y || 0);

    var d = [], imlec = 0;
    for (var i = 0; i < s.length; i++) {
      var ch = s[i];
      if (ch === ' ') { imlec += BOSLUK + ARA; continue; }
      var g = HARFLER[ch];
      if (!g) throw new Error('Alfabede bulunmayan karakter: ' + ch);
      var gx = x0 + imlec * olcek;
      for (var j = 0; j < g.length; j++) {
        var sekil = g[j];
        if (sekil.t === 'r') {
          var a = sekil.v;
          var x = gx + a[0] * olcek, y = y0 + a[1] * olcek;
          var w = a[2] * olcek, h = a[3] * olcek;
          d.push('M' + s2(x) + ' ' + s2(y) + 'H' + s2(x + w) + 'V' + s2(y + h) + 'H' + s2(x) + 'Z');
        } else {
          var n = sekil.v, par = [];
          for (var m = 0; m < n.length; m++) {
            par.push((m ? 'L' : 'M') + s2(gx + n[m][0] * olcek) + ' ' + s2(y0 + n[m][1] * olcek));
          }
          d.push(par.join('') + 'Z');
        }
      }
      imlec += EN + ARA;
    }
    return { d: d.join(''), en: toplamEn, boy: BOY * olcek, olcek: olcek };
  }

  return {
    EN: EN, BOY: BOY, ARA: ARA, BOSLUK: BOSLUK,
    HARFLER: HARFLER,
    bant: bant,
    normalize: normalize,
    birimEni: birimEni,
    yaziYolu: yaziYolu
  };
});
