/*!
 * qr.js — bagimliliksiz QR kod ureteci (byte modu, surum 1-10, ISO/IEC 18004)
 * Tarayicida window.QR, Node'da module.exports olarak calisir.
 */
(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.QR = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  // Bicim bilgisi icin hata duzeltme seviyesi bitleri
  var ECC_BITS = { L: 1, M: 0, Q: 3, H: 2 };

  // Surum -> seviye -> [blok basina EC kod sozcugu, [[blok sayisi, veri kod sozcugu], ...]]
  var BLOCKS = {
    1:  { L: [7,  [[1, 19]]],            M: [10, [[1, 16]]],            Q: [13, [[1, 13]]],            H: [17, [[1, 9]]] },
    2:  { L: [10, [[1, 34]]],            M: [16, [[1, 28]]],            Q: [22, [[1, 22]]],            H: [28, [[1, 16]]] },
    3:  { L: [15, [[1, 55]]],            M: [26, [[1, 44]]],            Q: [18, [[2, 17]]],            H: [22, [[2, 13]]] },
    4:  { L: [20, [[1, 80]]],            M: [18, [[2, 32]]],            Q: [26, [[2, 24]]],            H: [16, [[4, 9]]] },
    5:  { L: [26, [[1, 108]]],           M: [24, [[2, 43]]],            Q: [18, [[2, 15], [2, 16]]],   H: [22, [[2, 11], [2, 12]]] },
    6:  { L: [18, [[2, 68]]],            M: [16, [[4, 27]]],            Q: [24, [[4, 19]]],            H: [28, [[4, 15]]] },
    7:  { L: [20, [[2, 78]]],            M: [18, [[4, 31]]],            Q: [18, [[2, 14], [4, 15]]],   H: [26, [[4, 13], [1, 14]]] },
    8:  { L: [24, [[2, 97]]],            M: [22, [[2, 38], [2, 39]]],   Q: [22, [[4, 18], [2, 19]]],   H: [26, [[4, 14], [2, 15]]] },
    9:  { L: [30, [[2, 116]]],           M: [22, [[3, 36], [2, 37]]],   Q: [20, [[4, 16], [4, 17]]],   H: [24, [[4, 12], [4, 13]]] },
    10: { L: [18, [[2, 68], [2, 69]]],   M: [26, [[4, 43], [1, 44]]],   Q: [24, [[6, 19], [2, 20]]],   H: [28, [[6, 15], [2, 16]]] }
  };

  var ALIGN = {
    1: [], 2: [6, 18], 3: [6, 22], 4: [6, 26], 5: [6, 30],
    6: [6, 34], 7: [6, 22, 38], 8: [6, 24, 42], 9: [6, 26, 46], 10: [6, 28, 50]
  };

  // --- GF(256) aritmetigi (ilkel polinom 0x11D) ---
  var EXP = new Uint8Array(512), LOG = new Uint8Array(256);
  (function () {
    var x = 1;
    for (var i = 0; i < 255; i++) {
      EXP[i] = x; LOG[x] = i;
      x <<= 1;
      if (x & 0x100) x ^= 0x11d;
    }
    for (var j = 255; j < 512; j++) EXP[j] = EXP[j - 255];
  })();

  function gmul(a, b) {
    if (a === 0 || b === 0) return 0;
    return EXP[LOG[a] + LOG[b]];
  }

  function generatorPoly(degree) {
    var poly = [1];
    for (var d = 0; d < degree; d++) {
      var next = new Array(poly.length + 1).fill(0);
      for (var i = 0; i < poly.length; i++) {
        next[i] ^= gmul(poly[i], 1);
        next[i + 1] ^= gmul(poly[i], EXP[d]);
      }
      poly = next;
    }
    return poly;
  }

  function ecCodewords(data, ecLen) {
    var gen = generatorPoly(ecLen);
    var rem = new Array(ecLen).fill(0);
    for (var i = 0; i < data.length; i++) {
      var factor = data[i] ^ rem[0];
      rem.shift();
      rem.push(0);
      for (var j = 0; j < ecLen; j++) rem[j] ^= gmul(gen[j + 1], factor);
    }
    return rem;
  }

  // --- Metin -> UTF-8 bayt dizisi ---
  function toBytes(text) {
    if (typeof TextEncoder !== 'undefined') return Array.from(new TextEncoder().encode(text));
    return Array.from(Buffer.from(text, 'utf8'));
  }

  function capacity(version, level) {
    var spec = BLOCKS[version][level];
    var total = 0;
    spec[1].forEach(function (g) { total += g[0] * g[1]; });
    return total;
  }

  function pickVersion(byteLen, level, minVersion) {
    for (var v = minVersion || 1; v <= 10; v++) {
      var countBits = v < 10 ? 8 : 16;
      var needed = Math.ceil((4 + countBits + byteLen * 8) / 8);
      if (needed <= capacity(v, level)) return v;
    }
    throw new Error('Veri cok uzun: QR surum 1-10 (byte modu) sinirini asiyor.');
  }

  // --- Bit akisi -> araliksiz kod sozcukleri ---
  function buildCodewords(bytes, version, level) {
    var countBits = version < 10 ? 8 : 16;
    var bits = [];
    function push(value, len) {
      for (var i = len - 1; i >= 0; i--) bits.push((value >> i) & 1);
    }
    push(0x4, 4);                 // byte modu
    push(bytes.length, countBits);
    bytes.forEach(function (b) { push(b, 8); });

    var totalData = capacity(version, level);
    var maxBits = totalData * 8;
    for (var t = 0; t < 4 && bits.length < maxBits; t++) bits.push(0);
    while (bits.length % 8 !== 0) bits.push(0);

    var data = [];
    for (var i = 0; i < bits.length; i += 8) {
      var byte = 0;
      for (var j = 0; j < 8; j++) byte = (byte << 1) | bits[i + j];
      data.push(byte);
    }
    var pad = [0xec, 0x11], p = 0;
    while (data.length < totalData) data.push(pad[p++ % 2]);

    // Bloklara bol, EC hesapla, araliklandir
    var spec = BLOCKS[version][level], ecLen = spec[0];
    var dataBlocks = [], ecBlocks = [], pos = 0;
    spec[1].forEach(function (group) {
      for (var b = 0; b < group[0]; b++) {
        var block = data.slice(pos, pos + group[1]);
        pos += group[1];
        dataBlocks.push(block);
        ecBlocks.push(ecCodewords(block, ecLen));
      }
    });

    var out = [], maxData = Math.max.apply(null, dataBlocks.map(function (b) { return b.length; }));
    for (var i2 = 0; i2 < maxData; i2++) {
      for (var b2 = 0; b2 < dataBlocks.length; b2++) {
        if (i2 < dataBlocks[b2].length) out.push(dataBlocks[b2][i2]);
      }
    }
    for (var i3 = 0; i3 < ecLen; i3++) {
      for (var b3 = 0; b3 < ecBlocks.length; b3++) out.push(ecBlocks[b3][i3]);
    }
    return out;
  }

  // --- Matris kurulumu ---
  function newGrid(size, value) {
    var g = [];
    for (var r = 0; r < size; r++) g.push(new Array(size).fill(value));
    return g;
  }

  function placeFunctionPatterns(m, fn, version) {
    var size = m.length;

    function setF(r, c, v) { m[r][c] = v; fn[r][c] = true; }

    function finder(r0, c0) {
      for (var r = -1; r <= 7; r++) {
        for (var c = -1; c <= 7; c++) {
          var rr = r0 + r, cc = c0 + c;
          if (rr < 0 || rr >= size || cc < 0 || cc >= size) continue;
          var inRing = (r >= 0 && r <= 6 && (c === 0 || c === 6)) || (c >= 0 && c <= 6 && (r === 0 || r === 6));
          var inCore = r >= 2 && r <= 4 && c >= 2 && c <= 4;
          setF(rr, cc, inRing || inCore ? 1 : 0);
        }
      }
    }
    finder(0, 0); finder(0, size - 7); finder(size - 7, 0);

    for (var i = 8; i < size - 8; i++) {
      var bit = i % 2 === 0 ? 1 : 0;
      setF(6, i, bit); setF(i, 6, bit);
    }

    var centers = ALIGN[version];
    for (var a = 0; a < centers.length; a++) {
      for (var b = 0; b < centers.length; b++) {
        var cr = centers[a], cc2 = centers[b];
        if ((cr === 6 && cc2 === 6) || (cr === 6 && cc2 === size - 7) || (cr === size - 7 && cc2 === 6)) continue;
        for (var dr = -2; dr <= 2; dr++) {
          for (var dc = -2; dc <= 2; dc++) {
            var ring = Math.max(Math.abs(dr), Math.abs(dc));
            setF(cr + dr, cc2 + dc, ring === 1 ? 0 : 1);
          }
        }
      }
    }

    // Koyu modul yalnizca alan olarak ayrilir; degeri placeFormat icinde yazilir
    // (ISO/IEC 18004:2015 7.8 -- maske degerlendirmesi bicim bilgisi olmadan yapilir).
    fn[size - 8][8] = true;

    // Bicim bilgisi alanlari (icerik sonra yazilir)
    for (var k = 0; k <= 8; k++) {
      if (k !== 6) { fn[8][k] = true; fn[k][8] = true; }
    }
    fn[8][8] = true;
    for (var k2 = 0; k2 < 8; k2++) { fn[8][size - 1 - k2] = true; fn[size - 1 - k2][8] = true; }

    // Surum bilgisi alani (7 ve uzeri): yalnizca ayrilir, degeri sonra yazilir
    if (version >= 7) {
      for (var i2 = 0; i2 < 18; i2++) {
        var r2 = Math.floor(i2 / 3), c2 = size - 11 + (i2 % 3);
        fn[r2][c2] = true; fn[c2][r2] = true;
      }
    }
  }

  function placeVersion(m, version) {
    if (version < 7) return;
    var size = m.length, bits = versionBits(version);
    for (var i = 0; i < 18; i++) {
      var bit = (bits >> i) & 1;
      var r = Math.floor(i / 3), c = size - 11 + (i % 3);
      m[r][c] = bit; m[c][r] = bit;
    }
  }

  function versionBits(version) {
    var rem = version;
    for (var i = 0; i < 12; i++) rem = (rem << 1) ^ ((rem >>> 11) * 0x1f25);
    return (version << 12) | rem;
  }

  function formatBits(level, mask) {
    var data = (ECC_BITS[level] << 3) | mask;
    var rem = data;
    for (var i = 0; i < 10; i++) rem = (rem << 1) ^ ((rem >>> 9) * 0x537);
    return ((data << 10) | rem) ^ 0x5412;
  }

  function placeFormat(m, level, mask) {
    var size = m.length, bits = formatBits(level, mask);
    function bit(i) { return (bits >> i) & 1; }

    // Birinci kopya: sol ust kose
    for (var i = 0; i <= 5; i++) m[i][8] = bit(i);
    m[7][8] = bit(6);
    m[8][8] = bit(7);
    m[8][7] = bit(8);
    for (var j = 9; j < 15; j++) m[8][14 - j] = bit(j);

    // Ikinci kopya: sol alt ve sag ust
    for (var k = 0; k < 8; k++) m[8][size - 1 - k] = bit(k);
    for (var l = 8; l < 15; l++) m[size - 15 + l][8] = bit(l);
    m[size - 8][8] = 1; // koyu modul

  }

  function placeData(m, fn, codewords) {
    var size = m.length, bitIndex = 0, upward = true;
    for (var right = size - 1; right >= 1; right -= 2) {
      if (right === 6) right = 5;
      for (var step = 0; step < size; step++) {
        var row = upward ? size - 1 - step : step;
        for (var c = 0; c < 2; c++) {
          var col = right - c;
          if (fn[row][col]) continue;
          var bit = 0;
          if (bitIndex < codewords.length * 8) {
            bit = (codewords[bitIndex >> 3] >> (7 - (bitIndex & 7))) & 1;
          }
          m[row][col] = bit;
          bitIndex++;
        }
      }
      upward = !upward;
    }
  }

  function maskFn(mask, r, c) {
    switch (mask) {
      case 0: return (r + c) % 2 === 0;
      case 1: return r % 2 === 0;
      case 2: return c % 3 === 0;
      case 3: return (r + c) % 3 === 0;
      case 4: return (Math.floor(r / 2) + Math.floor(c / 3)) % 2 === 0;
      case 5: return ((r * c) % 2) + ((r * c) % 3) === 0;
      case 6: return (((r * c) % 2) + ((r * c) % 3)) % 2 === 0;
      default: return (((r + c) % 2) + ((r * c) % 3)) % 2 === 0;
    }
  }

  // ISO/IEC 18004:2015 7.8.3.1 -- 1:1:3:1:1 orani (N3) icin desen taramasi
  function n3Skoru(dizi, size) {
    var desen = '1011101', skor = 0, idx = dizi.indexOf(desen);
    while (idx !== -1) {
      var son = idx + 7;
      var oncesi = dizi.slice(Math.max(idx - 4, 0), idx);
      var sonrasi = dizi.slice(son, Math.min(son + 4, size));
      if (idx === 0 || idx === size - 7 || oncesi.indexOf('1') === -1 || sonrasi.indexOf('1') === -1) {
        skor += 40;
      } else {
        son = idx + 4; // ortak koyu moduller yeni eslesme baslatabilir
      }
      idx = dizi.indexOf(desen, son);
    }
    return skor;
  }

  function penalty(m) {
    var size = m.length, n1 = 0, n2 = 0, n3 = 0, koyu = 0;

    for (var i = 0; i < size; i++) {
      var satir = '', sutun = '';
      var satirRun = 1, sutunRun = 1;
      for (var j = 0; j < size; j++) {
        var sDeger = m[i][j], cDeger = m[j][i];
        satir += sDeger; sutun += cDeger;
        koyu += sDeger;

        if (j > 0) {
          // N1 -- satir ve sutun boyunca ayni renkli diziler
          if (sDeger === m[i][j - 1]) satirRun++;
          else { if (satirRun >= 5) n1 += satirRun - 2; satirRun = 1; }
          if (cDeger === m[j - 1][i]) sutunRun++;
          else { if (sutunRun >= 5) n1 += sutunRun - 2; sutunRun = 1; }

          // N2 -- 2x2 ayni renkli bloklar
          if (i > 0 && sDeger === m[i][j - 1] && sDeger === m[i - 1][j] && sDeger === m[i - 1][j - 1]) n2 += 3;
        }
      }
      if (satirRun >= 5) n1 += satirRun - 2;
      if (sutunRun >= 5) n1 += sutunRun - 2;
      n3 += n3Skoru(satir, size) + n3Skoru(sutun, size);
    }

    // N4 -- koyu modul oraninin %50'den sapmasi
    var oran = (koyu * 100) / (size * size);
    var n4 = 10 * Math.floor(Math.abs(oran - 50) / 5);
    return n1 + n2 + n3 + n4;
  }

  /**
   * @param {string} text kodlanacak metin (UTF-8)
   * @param {{level?:'L'|'M'|'Q'|'H', minVersion?:number, mask?:number}} [opts]
   * @returns {{size:number, modules:number[][], version:number, level:string, mask:number}}
   */
  function encode(text, opts) {
    opts = opts || {};
    var level = opts.level || 'M';
    if (!ECC_BITS.hasOwnProperty(level)) throw new Error('Gecersiz hata duzeltme seviyesi: ' + level);
    var bytes = toBytes(String(text));
    var version = pickVersion(bytes.length, level, opts.minVersion);
    var codewords = buildCodewords(bytes, version, level);
    var size = version * 4 + 17;

    var base = newGrid(size, 0), fn = newGrid(size, false);
    placeFunctionPatterns(base, fn, version);
    placeData(base, fn, codewords);

    var best = null;
    var masks = typeof opts.mask === 'number' ? [opts.mask] : [0, 1, 2, 3, 4, 5, 6, 7];
    masks.forEach(function (mask) {
      var m = base.map(function (row) { return row.slice(); });
      for (var r = 0; r < size; r++) {
        for (var c = 0; c < size; c++) {
          if (!fn[r][c] && maskFn(mask, r, c)) m[r][c] ^= 1;
        }
      }
      // ISO/IEC 18004:2015 7.8 -- degerlendirme bicim/surum bilgisi yazilmadan yapilir
      var score = masks.length === 1 ? 0 : penalty(m);
      if (!best || score < best.score) best = { score: score, modules: m, mask: mask };
    });

    placeFormat(best.modules, level, best.mask);
    placeVersion(best.modules, version);
    return { size: size, modules: best.modules, version: version, level: level, mask: best.mask };
  }

  /** QR'i SVG dizesine cevirir. */
  function toSvg(text, opts) {
    opts = opts || {};
    var qr = encode(text, opts);
    var quiet = opts.quietZone == null ? 4 : opts.quietZone;
    var dim = qr.size + quiet * 2;
    var dark = opts.dark || '#000000';
    var light = opts.light || '#ffffff';
    var path = [];
    for (var r = 0; r < qr.size; r++) {
      for (var c = 0; c < qr.size; c++) {
        if (qr.modules[r][c]) path.push('M' + (c + quiet) + ' ' + (r + quiet) + 'h1v1h-1z');
      }
    }
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + dim + ' ' + dim + '" shape-rendering="crispEdges" role="img" aria-label="QR kod">' +
      '<rect width="' + dim + '" height="' + dim + '" fill="' + light + '"/>' +
      '<path fill="' + dark + '" d="' + path.join('') + '"/></svg>';
  }

  /** QR'i canvas uzerine cizer (tarayici). */
  function toCanvas(canvas, text, opts) {
    opts = opts || {};
    var qr = encode(text, opts);
    var quiet = opts.quietZone == null ? 4 : opts.quietZone;
    var dim = qr.size + quiet * 2;
    var scale = opts.scale || Math.max(2, Math.floor((opts.width || 320) / dim));
    canvas.width = dim * scale;
    canvas.height = dim * scale;
    var ctx = canvas.getContext('2d');
    ctx.fillStyle = opts.light || '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = opts.dark || '#000000';
    for (var r = 0; r < qr.size; r++) {
      for (var c = 0; c < qr.size; c++) {
        if (qr.modules[r][c]) ctx.fillRect((c + quiet) * scale, (r + quiet) * scale, scale, scale);
      }
    }
    return qr;
  }

  return { encode: encode, toSvg: toSvg, toCanvas: toCanvas };
});
