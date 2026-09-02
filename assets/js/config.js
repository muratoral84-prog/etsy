/*!
 * config.js — Tek düzenleme noktası.
 * Aşağıdaki alanları kendi gerçek bilgilerinizle değiştirin, ardından
 * `dogrulanmisBilgiler` alanını true yapın (uyarı şeridi kaybolur).
 */
(function (root, factory) {
  var cfg = factory();
  if (typeof module === 'object' && module.exports) module.exports = cfg;
  else root.KARTVIZIT = cfg;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  return {
    // Bilgiler gerçek verilerle güncellendiğinde true yapın.
    dogrulanmisBilgiler: false,

    // NFC etiketine yazılacak ve QR koda gömülecek adres.
    // GitHub Pages açıldığında varsayılan adres budur.
    site: {
      url: 'https://muratoral84-prog.github.io/etsy/',
      // Tıklama kaynağını ayırt etmek için sayfaya eklenen parametre.
      nfcParametresi: 'kaynak=nfc'
    },

    marka: {
      ad: 'Murat Oral Medya Ajansı',
      monogram: 'MO',
      slogan: 'Markanızı doğru kanalda, doğru hikâyeyle büyütüyoruz.',
      kurulus: '',
      renk: {
        vurgu: '#ff7a18',
        vurguIkincil: '#ffb648'
      }
    },

    kisi: {
      ad: 'Murat Oral',
      unvan: 'Kurucu & Medya Direktörü',
      soyad: 'Oral',
      onAd: 'Murat'
    },

    iletisim: {
      telefon: '+90 555 000 00 00',        // ÖRNEK VERİ
      whatsapp: '+905550000000',           // ÖRNEK VERİ (yalnız rakam, + ile)
      eposta: 'iletisim@muratoralmedya.com', // ÖRNEK VERİ
      web: 'https://muratoralmedya.com',   // ÖRNEK VERİ
      adres: 'İstanbul, Türkiye',
      harita: 'https://maps.google.com/?q=Istanbul'
    },

    sosyal: [
      { ad: 'Instagram', url: 'https://instagram.com/', kisa: 'IG' },
      { ad: 'LinkedIn', url: 'https://linkedin.com/', kisa: 'in' },
      { ad: 'YouTube', url: 'https://youtube.com/', kisa: 'YT' }
    ],

    hizmetler: [
      'Sosyal medya yönetimi',
      'Performans reklamları',
      'İçerik prodüksiyonu',
      'Marka stratejisi',
      'Influencer iş birlikleri',
      'Web & e-ticaret'
    ],

    // NFC etiketine yazılacak kayıt türü: 'url', 'vcard' veya 'ikisi'
    nfc: {
      varsayilanKayit: 'url',
      // Yaygın etiket kapasiteleri (bayt) — yazma öncesi uyarı için
      etiketKapasiteleri: { 'NTAG213': 144, 'NTAG215': 504, 'NTAG216': 888 }
    }
  };
});
