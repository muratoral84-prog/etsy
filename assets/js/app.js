/*!
 * app.js — Kartvizit sayfasını config.js'ten oluşturur.
 */
(function () {
  'use strict';

  var cfg = window.KARTVIZIT;
  var $ = function (id) { return document.getElementById(id); };

  var IKON = {
    kisi: 'M12 12a5 5 0 1 0 0-10 5 5 0 0 0 0 10Zm0 2c-4.4 0-8 2.6-8 5.8V22h16v-2.2c0-3.2-3.6-5.8-8-5.8Z',
    telefon: 'M6.6 10.8a15.6 15.6 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.2.4 2.4.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C11.4 21 3 12.6 3 2.9c0-.5.4-1 1-1h3.5c.6 0 1 .5 1 1 0 1.3.2 2.5.6 3.6.1.4 0 .8-.2 1l-2.3 2.3Z',
    whatsapp: 'M12.04 2c-5.5 0-9.96 4.46-9.96 9.96 0 1.76.46 3.48 1.34 5L2 22l5.2-1.36a9.9 9.9 0 0 0 4.84 1.24h.01c5.5 0 9.96-4.46 9.96-9.96S17.54 2 12.04 2Zm5.8 14.06c-.24.68-1.4 1.3-1.94 1.34-.5.06-1.12.08-1.8-.12-.42-.12-.96-.3-1.64-.6-2.9-1.26-4.78-4.16-4.92-4.36-.14-.2-1.18-1.56-1.18-2.98s.74-2.12 1-2.4c.26-.28.58-.36.78-.36l.56.02c.18 0 .42-.06.66.5.24.58.84 2 .92 2.14.08.14.12.3.02.5-.1.2-.16.32-.3.5l-.44.5c-.14.14-.3.3-.12.6.18.3.78 1.3 1.68 2.1 1.16 1.04 2.14 1.36 2.44 1.5.3.16.48.14.66-.08.18-.2.76-.88.96-1.18.2-.3.4-.24.66-.14.28.1 1.7.8 2 .94.3.14.48.22.56.34.08.14.08.72-.16 1.4Z',
    posta: 'M3 5h18c.6 0 1 .4 1 1v12c0 .6-.4 1-1 1H3c-.6 0-1-.4-1-1V6c0-.6.4-1 1-1Zm9 8 8-4.6V7l-8 4.6L4 7v1.4L12 13Z',
    web: 'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm6.9 9h-3a15 15 0 0 0-1.2-5.3A8 8 0 0 1 18.9 11ZM12 4.2c.8 1.1 1.6 3.2 1.8 6.8h-3.6c.2-3.6 1-5.7 1.8-6.8ZM5.1 11a8 8 0 0 1 4.2-5.3A15 15 0 0 0 8.1 11h-3Zm0 2h3a15 15 0 0 0 1.2 5.3A8 8 0 0 1 5.1 13Zm6.9 6.8c-.8-1.1-1.6-3.2-1.8-6.8h3.6c-.2 3.6-1 5.7-1.8 6.8Zm2.7-.5a15 15 0 0 0 1.2-5.3h3a8 8 0 0 1-4.2 5.3Z',
    harita: 'M12 2a7 7 0 0 0-7 7c0 5 7 13 7 13s7-8 7-13a7 7 0 0 0-7-7Zm0 9.5A2.5 2.5 0 1 1 12 6a2.5 2.5 0 0 1 0 5.5Z',
    qr: 'M3 3h8v8H3V3Zm2 2v4h4V5H5Zm8-2h8v8h-8V3Zm2 2v4h4V5h-4ZM3 13h8v8H3v-8Zm2 2v4h4v-4H5Zm8-2h3v3h-3v-3Zm5 0h3v3h-3v-3Zm-5 5h3v3h-3v-3Zm5 0h3v3h-3v-3Z',
    paylas: 'M18 16.1c-.8 0-1.5.3-2 .8l-7.1-4.1c.1-.3.1-.5.1-.8s0-.5-.1-.8L16 7.1c.5.5 1.2.8 2 .8a3 3 0 1 0-3-3c0 .3 0 .5.1.8L8 9.8a3 3 0 1 0 0 4.4l7.1 4.1c-.1.2-.1.5-.1.7a3 3 0 1 0 3-2.9Z',
    nfc: 'M20 2H4c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2Zm-2 16.5h-3.5v-6.2c0-.7-.6-1.3-1.3-1.3s-1.2.6-1.2 1.3v3.4L8.5 12V5.5H12c2.5 0 4.5 2 4.5 4.5v2.3H18v6.2ZM6 5.5h1.5v13H6v-13Z'
  };

  function ikon(yol) {
    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class', 'ikon');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('fill', 'currentColor');
    svg.setAttribute('aria-hidden', 'true');
    var path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', yol);
    svg.appendChild(path);
    return svg;
  }

  function dugme(secenek) {
    var el = document.createElement(secenek.href ? 'a' : 'button');
    el.className = 'dugme' + (secenek.sinif ? ' ' + secenek.sinif : '');
    if (secenek.href) {
      el.href = secenek.href;
      if (secenek.indir) el.setAttribute('download', secenek.indir);
      if (secenek.yeniSekme) { el.target = '_blank'; el.rel = 'noopener'; }
    } else {
      el.type = 'button';
      el.addEventListener('click', secenek.tikla);
    }
    el.appendChild(ikon(secenek.ikon));
    el.appendChild(document.createTextNode(secenek.metin));
    return el;
  }

  /** Kanal etiketi eklenmiş kartvizit adresi. */
  function adres(kanal) {
    var temel = (cfg.site.url || location.href).split('#')[0];
    if (!kanal) return temel;
    return temel + (temel.indexOf('?') === -1 ? '?' : '&') + 'kaynak=' + kanal;
  }

  function telefonSade(numara) {
    return String(numara || '').replace(/[^\d+]/g, '');
  }

  function metinYaz(id, deger) {
    var el = $(id);
    if (!el) return;
    if (deger) el.textContent = deger;
    else el.hidden = true;
  }

  function kur() {
    document.documentElement.style.setProperty('--vurgu', cfg.marka.renk.vurgu);
    document.documentElement.style.setProperty('--vurgu-2', cfg.marka.renk.vurguIkincil);

    $('monogram').textContent = cfg.marka.monogram;
    metinYaz('ad', cfg.kisi.ad);
    metinYaz('unvan', cfg.kisi.unvan);
    metinYaz('ajans', cfg.marka.ad);
    metinYaz('slogan', cfg.marka.slogan);
    metinYaz('adres', cfg.iletisim.adres);
    document.title = cfg.kisi.ad + ' — ' + cfg.marka.ad;

    if (!cfg.dogrulanmisBilgiler) {
      var uyari = $('uyari');
      uyari.hidden = false;
      uyari.textContent = 'Bu sayfa örnek iletişim bilgileriyle yayında. ' +
        'assets/js/config.js dosyasındaki telefon, e-posta ve sosyal medya adreslerini ' +
        'güncelleyip dogrulanmisBilgiler alanını true yapın.';
    }

    var params = new URLSearchParams(location.search);
    if (params.get('kaynak') === 'nfc') $('rozetNfc').hidden = false;

    eylemleriEkle();
    sosyalEkle();
    hizmetleriEkle();
    qrKur();
  }

  function eylemleriEkle() {
    var kap = $('eylemler');
    var i = cfg.iletisim;

    kap.appendChild(dugme({
      metin: 'Rehbere ekle', ikon: IKON.kisi, sinif: 'dugme--birincil',
      href: 'kartvizit.vcf', indir: 'murat-oral.vcf'
    }));

    var satir1 = document.createElement('div');
    satir1.className = 'ikili';
    if (i.telefon) satir1.appendChild(dugme({ metin: 'Ara', ikon: IKON.telefon, href: 'tel:' + telefonSade(i.telefon) }));
    if (i.whatsapp) {
      satir1.appendChild(dugme({
        metin: 'WhatsApp', ikon: IKON.whatsapp, sinif: 'dugme--wp', yeniSekme: true,
        href: 'https://wa.me/' + telefonSade(i.whatsapp).replace(/^\+/, '') +
          '?text=' + encodeURIComponent('Merhaba ' + cfg.kisi.onAd + ', kartvizitinizden ulaşıyorum.')
      }));
    }
    if (satir1.children.length) kap.appendChild(satir1);

    var satir2 = document.createElement('div');
    satir2.className = 'ikili';
    if (i.eposta) satir2.appendChild(dugme({ metin: 'E-posta', ikon: IKON.posta, href: 'mailto:' + i.eposta }));
    if (i.web) satir2.appendChild(dugme({ metin: 'Web sitesi', ikon: IKON.web, href: i.web, yeniSekme: true }));
    if (satir2.children.length) kap.appendChild(satir2);

    if (i.harita) {
      kap.appendChild(dugme({ metin: 'Konumu aç', ikon: IKON.harita, href: i.harita, yeniSekme: true }));
    }

    var satir3 = document.createElement('div');
    satir3.className = 'ikili';
    satir3.appendChild(dugme({ metin: 'QR kod', ikon: IKON.qr, tikla: qrAc }));
    satir3.appendChild(dugme({ metin: 'Paylaş', ikon: IKON.paylas, tikla: paylas }));
    kap.appendChild(satir3);

    if ('NDEFReader' in window) {
      kap.appendChild(dugme({ metin: 'NFC etiketine yaz', ikon: IKON.nfc, href: 'nfc.html' }));
    }
  }

  function sosyalEkle() {
    var kap = $('sosyal');
    (cfg.sosyal || []).forEach(function (s) {
      if (!s.url) return;
      var a = document.createElement('a');
      a.href = s.url;
      a.target = '_blank';
      a.rel = 'noopener';
      var kisa = document.createElement('span');
      kisa.className = 'kisa';
      kisa.textContent = s.kisa || s.ad.slice(0, 2);
      a.appendChild(kisa);
      a.appendChild(document.createTextNode(s.ad));
      kap.appendChild(a);
    });
  }

  function hizmetleriEkle() {
    var kap = $('hizmetler');
    (cfg.hizmetler || []).forEach(function (h) {
      var li = document.createElement('li');
      li.textContent = h;
      kap.appendChild(li);
    });
  }

  /* --- QR --- */
  var qrPencere, qrCanvas;

  function qrKur() {
    qrPencere = $('qrPencere');
    qrCanvas = $('qrCanvas');
    $('qrKapat').addEventListener('click', function () { qrPencere.close(); });
    $('qrIndir').addEventListener('click', qrIndir);
  }

  function qrAc() {
    try {
      window.QR.toCanvas(qrCanvas, adres('qr'), { level: 'M', width: 560, scale: 8 });
      $('qrDurum').textContent = '';
    } catch (e) {
      $('qrDurum').textContent = 'QR üretilemedi: ' + e.message;
    }
    if (typeof qrPencere.showModal === 'function') qrPencere.showModal();
    else qrPencere.setAttribute('open', '');
  }

  function qrIndir() {
    try {
      var a = document.createElement('a');
      a.download = 'murat-oral-kartvizit-qr.png';
      a.href = qrCanvas.toDataURL('image/png');
      a.click();
      $('qrDurum').textContent = 'QR kod indirildi.';
    } catch (e) {
      $('qrDurum').textContent = 'İndirme başarısız: ' + e.message;
    }
  }

  function paylas() {
    var veri = {
      title: cfg.kisi.ad + ' — ' + cfg.marka.ad,
      text: cfg.marka.slogan,
      url: adres('paylasim')
    };
    if (navigator.share) {
      navigator.share(veri).catch(function () { /* kullanıcı vazgeçti */ });
      return;
    }
    if (navigator.clipboard) {
      navigator.clipboard.writeText(veri.url).then(function () {
        alert('Kartvizit bağlantısı kopyalandı:\n' + veri.url);
      });
    } else {
      prompt('Kartvizit bağlantısı:', veri.url);
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', kur);
  else kur();
})();
