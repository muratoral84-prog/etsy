/*!
 * vcard.js — Yapılandırmadan vCard 3.0 üretir (Android/iOS rehber uyumlu).
 * Tarayıcıda window.VCard, Node'da module.exports.
 */
(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.VCard = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  function esc(value) {
    return String(value == null ? '' : value)
      .replace(/\\/g, '\\\\')
      .replace(/\n/g, '\\n')
      .replace(/,/g, '\\,')
      .replace(/;/g, '\;');
  }

  function baytSayisi(metin) {
    if (typeof TextEncoder !== 'undefined') return new TextEncoder().encode(metin).length;
    return Buffer.byteLength(metin, 'utf8');
  }

  // RFC 6350 3.2: satırlar 75 okteti aşmamalı; devam satırları boşlukla başlar.
  // Ölçüm karakter değil oktet üzerinden yapılır (Türkçe karakterler 2 bayttır).
  function fold(line) {
    var sinir = 75;
    if (baytSayisi(line) <= sinir) return line;

    var parcalar = [], mevcut = '', uzunluk = 0;
    var karakterler = Array.from(line);
    for (var i = 0; i < karakterler.length; i++) {
      var bayt = baytSayisi(karakterler[i]);
      if (uzunluk + bayt > sinir) {
        parcalar.push(mevcut);
        mevcut = ' ';
        uzunluk = 1;
      }
      mevcut += karakterler[i];
      uzunluk += bayt;
    }
    parcalar.push(mevcut);
    return parcalar.join('\r\n');
  }

  function build(cfg) {
    var k = cfg.kisi, i = cfg.iletisim, m = cfg.marka;
    var lines = [
      'BEGIN:VCARD',
      'VERSION:3.0',
      'N:' + esc(k.soyad) + ';' + esc(k.onAd) + ';;;',
      'FN:' + esc(k.ad)
    ];

    if (m.ad) lines.push('ORG:' + esc(m.ad));
    if (k.unvan) lines.push('TITLE:' + esc(k.unvan));
    if (i.telefon) lines.push('TEL;TYPE=CELL,VOICE:' + esc(i.telefon));
    if (i.whatsapp && i.whatsapp !== i.telefon) lines.push('TEL;TYPE=WORK,VOICE:' + esc(i.whatsapp));
    if (i.eposta) lines.push('EMAIL;TYPE=INTERNET,WORK:' + esc(i.eposta));
    if (i.web) lines.push('URL:' + esc(i.web));
    if (cfg.site && cfg.site.url) lines.push('URL:' + esc(cfg.site.url));
    if (i.adres) lines.push('ADR;TYPE=WORK:;;' + esc(i.adres) + ';;;;');

    (cfg.sosyal || []).forEach(function (s) {
      if (s.url) lines.push('X-SOCIALPROFILE;TYPE=' + esc(s.ad.toLowerCase()) + ':' + esc(s.url));
    });

    if (m.slogan) lines.push('NOTE:' + esc(m.slogan));
    lines.push('REV:' + new Date().toISOString().replace(/\.\d{3}/, ''));
    lines.push('END:VCARD');

    return lines.map(fold).join('\r\n') + '\r\n';
  }

  return { build: build, bayt: baytSayisi };
});
