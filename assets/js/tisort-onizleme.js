/*!
 * tisort-onizleme.js — tisort.html arayüzü: tasarım/renk seçimi, mankende
 * önizleme ve SVG indirme. Dış bağımlılık yok.
 */
(function () {
  'use strict';

  var D = window.TASARIMLAR;

  var KUMASLAR = [
    { kod: 'siyah', ad: 'Siyah', renk: '#15181D', koyu: true },
    { kod: 'lacivert', ad: 'Lacivert', renk: '#1C2340', koyu: true },
    { kod: 'haki', ad: 'Haki', renk: '#3D4636', koyu: true },
    { kod: 'beyaz', ad: 'Beyaz', renk: '#F5F5F3', koyu: false },
    { kod: 'kum', ad: 'Kum', renk: '#D9CDBA', koyu: false },
    { kod: 'gri', ad: 'Gri melanj', renk: '#BFC3C7', koyu: false }
  ];

  var secili = { tasarim: D.TASARIMLAR[0].kod, kumas: KUMASLAR[0] };

  var baski = document.getElementById('baski');
  var kumasYolu = document.getElementById('kumas');
  var durum = document.getElementById('durum');

  function paletKodu() { return secili.kumas.koyu ? 'koyu-zemin' : 'acik-zemin'; }

  function ciz() {
    var palet = D.PALETLER[paletKodu()];
    baski.innerHTML = D.bul(secili.tasarim).ciz(palet);
    kumasYolu.setAttribute('fill', secili.kumas.renk);
    durum.textContent = D.bul(secili.tasarim).ad + ' — ' + secili.kumas.ad + ' tişört, ' + palet.kisaAd + '.';

    var dosya = secili.tasarim + '-' + paletKodu() + '.svg';
    var bag = document.getElementById('dosyaBagi');
    bag.href = 'urun/tisort/tasarim/' + dosya;
    bag.setAttribute('download', dosya);
    bag.textContent = 'Üretilmiş dosya';
    bilgiyiYaz();
  }

  function dugmeler(kap, liste, etiket, secildi, esitMi) {
    kap.innerHTML = '';
    liste.forEach(function (oge) {
      var d = document.createElement('button');
      d.type = 'button';
      d.className = 'secenek' + (esitMi(oge) ? ' secili' : '');
      d.setAttribute('role', 'radio');
      d.setAttribute('aria-checked', esitMi(oge) ? 'true' : 'false');
      d.textContent = etiket(oge);
      if (oge.renk) {
        var nokta = document.createElement('span');
        nokta.className = 'nokta';
        nokta.style.background = oge.renk;
        d.prepend(nokta);
      }
      d.addEventListener('click', function () { secildi(oge); });
      kap.appendChild(d);
    });
  }

  function tazele() {
    dugmeler(document.getElementById('tasarimSecimi'), D.TASARIMLAR,
      function (t) { return t.ad; },
      function (t) { secili.tasarim = t.kod; tazele(); },
      function (t) { return t.kod === secili.tasarim; });

    dugmeler(document.getElementById('renkSecimi'), KUMASLAR,
      function (k) { return k.ad; },
      function (k) { secili.kumas = k; tazele(); },
      function (k) { return k.kod === secili.kumas.kod; });

    ciz();
  }

  function bilgiyiYaz() {
    var t = D.bul(secili.tasarim);
    var satirlar = [
      t.aciklama,
      D.TUVAL.en + '×' + D.TUVAL.boy + ' px — ' + (D.TUVAL.en / D.TUVAL.dpi) + '×' + (D.TUVAL.boy / D.TUVAL.dpi) + ' inç @ ' + D.TUVAL.dpi + ' dpi',
      'İki mürekkep: ' + D.PALETLER[paletKodu()].murekkep + ' + ' + D.PALETLER[paletKodu()].vurgu + ' (DTG ve serigrafiye uygun)',
      'Vektörel SVG — yazı tipi gömülü değil, tüm harfler yola çevrilmiştir'
    ];
    var ul = document.getElementById('bilgi');
    ul.innerHTML = '';
    satirlar.forEach(function (s) {
      var li = document.createElement('li');
      li.textContent = s;
      ul.appendChild(li);
    });
  }

  document.getElementById('indir').addEventListener('click', function () {
    var svg = D.toSvg(secili.tasarim, { palet: paletKodu() });
    var bag = document.createElement('a');
    var url = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml' }));
    bag.href = url;
    bag.download = secili.tasarim + '-' + paletKodu() + '.svg';
    document.body.appendChild(bag);
    bag.click();
    bag.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    durum.textContent = bag.download + ' indirildi.';
  });

  tazele();
})();
