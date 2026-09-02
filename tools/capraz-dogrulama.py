#!/usr/bin/env python3
"""
capraz-dogrulama.py — QR üretecini bağımsız kütüphanelerle çapraz doğrular.

Kurulum (yalnızca geliştirme için, projenin çalışması için gerekmez):

    pip install segno zxing-cpp opencv-python-headless numpy

Çalıştırma:

    python3 tools/capraz-dogrulama.py

Yaptığı iki kontrol:
  1. Üretilen her QR, zxing-cpp ile taranıp metnin aynen geri okunduğu doğrulanır.
  2. Veri kapasiteyi tam doldurduğunda (dolgu baytı yokken) matris, referans
     uygulama segno'nun ürettiği matrisle bit bit karşılaştırılır. Dolgulu
     durumlarda segno, bayt sınırına oturmuş akışa fazladan bir sıfır bayt
     eklediği için (encoder.write_padding_bits) matrisler kasıtlı olarak farklıdır.
"""
import json
import subprocess
import sys
from pathlib import Path

try:
    import numpy as np
    import segno
    import zxingcpp
except ImportError as exc:  # pragma: no cover
    sys.exit(f'Eksik bağımlılık: {exc.name}. Kurulum: pip install segno zxing-cpp numpy')

KOK = Path(__file__).resolve().parent.parent

NODE_BETIK = r'''
const QR = require(process.argv[1]);
const cikti = [];
const metinler = process.argv.slice(2);
for (const t of metinler) {
  for (const lv of ['L', 'M', 'Q', 'H']) {
    let q;
    try { q = QR.encode(t, { level: lv }); } catch (e) { continue; }
    cikti.push({ text: t, level: lv, version: q.version, mask: q.mask, matrix: q.modules });
  }
}
console.log(JSON.stringify(cikti));
'''


def node_uret(metinler):
    sonuc = subprocess.run(
        ['node', '-e', NODE_BETIK, str(KOK / 'assets/js/qr.js'), *metinler],
        capture_output=True, text=True, check=True)
    return json.loads(sonuc.stdout)


def tam_kapasite_ornekleri():
    """Her sürüm/seviye için kapasiteyi tam dolduran metinler."""
    kapasiteler = node_uret(['x'])  # node erişimini doğrula
    assert kapasiteler
    betik = r'''
const QR = require(process.argv[1]);
const cikti = [];
for (let v = 1; v <= 10; v++) {
  for (const lv of ['L', 'M', 'Q', 'H']) {
    let lo = 1, hi = 400, best = 1;
    while (lo <= hi) {
      const mid = (lo + hi) >> 1;
      let ok = true, q;
      try { q = QR.encode('A'.repeat(mid), { level: lv, minVersion: v }); } catch (e) { ok = false; }
      if (ok && q.version === v) { best = mid; lo = mid + 1; } else hi = mid - 1;
    }
    const t = 'muratoral'.repeat(Math.ceil(best / 9)).slice(0, best);
    const q = QR.encode(t, { level: lv, minVersion: v });
    cikti.push({ text: t, level: lv, version: q.version, mask: q.mask, matrix: q.modules });
  }
}
console.log(JSON.stringify(cikti));
'''
    sonuc = subprocess.run(['node', '-e', betik, str(KOK / 'assets/js/qr.js')],
                           capture_output=True, text=True, check=True)
    return json.loads(sonuc.stdout)


def coz(kayit):
    m = np.array(kayit['matrix'], dtype=np.uint8)
    resim = np.kron(np.pad(1 - m, 4, constant_values=1) * 255,
                    np.ones((6, 6), dtype=np.uint8)).astype(np.uint8)
    okunan = zxingcpp.read_barcode(resim)
    return okunan.text if okunan else None


def main():
    metinler = [
        'https://muratoral84-prog.github.io/etsy/?kaynak=qr',
        'https://muratoralmedya.com',
        'Murat Oral Medya Ajansı — dijital kartvizit',
        'tel:+905550000000',
        'A' * 100,
    ]
    kayitlar = node_uret(metinler)
    hata = 0
    for k in kayitlar:
        if coz(k) != k['text']:
            hata += 1
            print(f'ÇÖZÜLEMEDİ: sürüm {k["version"]} {k["level"]} — {k["text"][:40]!r}')
    print(f'zxing-cpp ile çözüm: {len(kayitlar) - hata}/{len(kayitlar)}')

    tam = tam_kapasite_ornekleri()
    fark = 0
    for k in tam:
        ref = segno.make(k['text'], version=k['version'], error=k['level'],
                         mode='byte', boost_error=False)
        if ref.mask != k['mask'] or [list(r) for r in ref.matrix] != k['matrix']:
            fark += 1
            print(f'FARK: sürüm {k["version"]} {k["level"]} (maske {k["mask"]} / segno {ref.mask})')
    print(f'segno ile birebir matris: {len(tam) - fark}/{len(tam)}')

    return 1 if (hata or fark) else 0


if __name__ == '__main__':
    sys.exit(main())
