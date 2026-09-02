/*!
 * nfc.js — Web NFC ile kartvizit etiketi yazma, okuma ve kilitleme.
 */
(function () {
  'use strict';

  var cfg = window.KARTVIZIT;
  var $ = function (id) { return document.getElementById(id); };
  var okuyucu = null;
  var durdurucu = null;

  function gunluk(mesaj, tur) {
    var kap = $('gunluk');
    var satir = document.createElement('div');
    if (tur) satir.className = tur;
    var saat = new Date().toLocaleTimeString('tr-TR');
    satir.textContent = '[' + saat + '] ' + mesaj;
    kap.appendChild(satir);
    kap.scrollTop = kap.scrollHeight;
  }

  function nfcAdresi() {
    var temel = (cfg.site.url || location.origin + location.pathname.replace(/nfc\.html$/, '')).split('#')[0];
    var ek = cfg.site.nfcParametresi;
    if (!ek) return temel;
    return temel + (temel.indexOf('?') === -1 ? '?' : '&') + ek;
  }

  function baytUzunlugu(metin) {
    return new TextEncoder().encode(metin).length;
  }

  /** NDEF mesajının yaklaşık etiket üzerindeki boyutu (bayt). */
  function tahminiBoyut(kayitlar) {
    var toplam = 2; // TLV başlık + sonlandırıcı
    kayitlar.forEach(function (k) {
      if (k.recordType === 'url') {
        // "https://" ön eki tek bayta kısaltılır
        var kisaltilmis = k.data.replace(/^https:\/\/(www\.)?/, '').replace(/^http:\/\/(www\.)?/, '');
        toplam += baytUzunlugu(kisaltilmis) + 1 + 4;
      } else {
        toplam += k.data.length + baytUzunlugu(k.mediaType || '') + 6;
      }
    });
    return toplam;
  }

  function kayitlariHazirla() {
    var tur = $('kayitTuru').value;
    var url = $('urlAlani').value.trim();
    var kayitlar = [];

    if (tur === 'url' || tur === 'ikisi') {
      if (!/^https?:\/\//i.test(url)) throw new Error('Adres http:// veya https:// ile başlamalı.');
      kayitlar.push({ recordType: 'url', data: url });
    }
    if (tur === 'vcard' || tur === 'ikisi') {
      var vcf = window.VCard.build(cfg);
      kayitlar.push({
        recordType: 'mime',
        mediaType: 'text/vcard',
        data: new TextEncoder().encode(vcf)
      });
    }
    return kayitlar;
  }

  function boyutuGuncelle() {
    try {
      var kayitlar = kayitlariHazirla();
      var boyut = tahminiBoyut(kayitlar);
      var kapasiteler = cfg.nfc.etiketKapasiteleri || {};
      var uyanlar = Object.keys(kapasiteler).filter(function (ad) { return boyut <= kapasiteler[ad]; });
      var metin = 'Tahmini NDEF boyutu: ~' + boyut + ' bayt. ';
      metin += uyanlar.length
        ? 'Şu etiketlere sığar: ' + uyanlar.join(', ') + '.'
        : 'Uyarı: listelenen etiketlerin hiçbirine sığmıyor, daha kısa bir kayıt seçin.';
      $('boyutBilgi').textContent = metin;
    } catch (e) {
      $('boyutBilgi').textContent = e.message;
    }
  }

  function destekVar() {
    if (!('NDEFReader' in window)) {
      var u = $('destekUyari');
      u.hidden = false;
      u.textContent = 'Bu tarayıcı Web NFC desteklemiyor. Android telefonda Chrome ile ' +
        'https:// adresinden açın; iPhone kullanıyorsanız Kestirmeler uygulamasının NFC eylemiyle ' +
        'aşağıdaki adresi etikete yazın.';
      return false;
    }
    return true;
  }

  async function yaz() {
    if (!destekVar()) return;
    var kayitlar;
    try {
      kayitlar = kayitlariHazirla();
    } catch (e) {
      gunluk(e.message, 'hata');
      return;
    }

    var kilitle = $('kilitOnay').checked;
    if (kilitle && !confirm('Etiket kalıcı olarak salt okunur yapılacak. Bu işlem GERİ ALINAMAZ. Devam edilsin mi?')) {
      return;
    }

    gunluk('Telefonu etikete yaklaştırın…');
    try {
      var yazici = new NDEFReader();
      await yazici.write({ records: kayitlar });
      gunluk('Etikete yazıldı (' + kayitlar.length + ' kayıt, ~' + tahminiBoyut(kayitlar) + ' bayt).', 'basari');

      if (kilitle) {
        await yazici.makeReadOnly();
        gunluk('Etiket kalıcı olarak salt okunur yapıldı.', 'basari');
      }
    } catch (e) {
      gunluk('Yazma başarısız: ' + e.message, 'hata');
    }
  }

  async function oku() {
    if (!destekVar()) return;
    if (okuyucu) { gunluk('Tarama zaten sürüyor.'); return; }

    try {
      okuyucu = new NDEFReader();
      durdurucu = new AbortController();
      await okuyucu.scan({ signal: durdurucu.signal });
      $('durdurButonu').hidden = false;
      gunluk('Tarama başladı. Etiketi telefona yaklaştırın…');

      okuyucu.onreadingerror = function () {
        gunluk('Etiket okunamadı. Etiketi biraz daha yakın tutun.', 'hata');
      };

      okuyucu.onreading = function (olay) {
        $('etiketBilgi').textContent = 'Seri no: ' + (olay.serialNumber || 'bilinmiyor');
        var liste = $('okunanKayitlar');
        liste.replaceChildren();
        gunluk('Etiket okundu: ' + olay.message.records.length + ' kayıt.', 'basari');

        olay.message.records.forEach(function (kayit) {
          var li = document.createElement('li');
          var tur = document.createElement('span');
          tur.className = 'tur';
          tur.textContent = kayit.recordType + (kayit.mediaType ? ' · ' + kayit.mediaType : '');
          li.appendChild(tur);

          var icerik = '';
          try {
            if (kayit.recordType === 'url' || kayit.recordType === 'text') {
              icerik = new TextDecoder(kayit.encoding || 'utf-8').decode(kayit.data);
            } else if (kayit.recordType === 'mime') {
              icerik = new TextDecoder().decode(kayit.data);
            } else {
              icerik = kayit.data ? kayit.data.byteLength + ' bayt ham veri' : '(boş)';
            }
          } catch (e) {
            icerik = 'Çözümlenemedi: ' + e.message;
          }
          li.appendChild(document.createTextNode(icerik));
          liste.appendChild(li);
        });
      };
    } catch (e) {
      okuyucu = null;
      gunluk('Tarama başlatılamadı: ' + e.message, 'hata');
    }
  }

  function durdur() {
    if (durdurucu) durdurucu.abort();
    okuyucu = null;
    durdurucu = null;
    $('durdurButonu').hidden = true;
    gunluk('Tarama durduruldu.');
  }

  function kur() {
    $('urlAlani').value = nfcAdresi();
    destekVar();
    boyutuGuncelle();
    $('kayitTuru').addEventListener('change', boyutuGuncelle);
    $('urlAlani').addEventListener('input', boyutuGuncelle);
    $('yazButonu').addEventListener('click', yaz);
    $('okuButonu').addEventListener('click', oku);
    $('durdurButonu').addEventListener('click', durdur);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', kur);
  else kur();
})();
