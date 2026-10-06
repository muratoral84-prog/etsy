# Pıtırcık ve Gökkuşağının Kayıp Renkleri

3–6 yaş için ~10 dakikalık Türkçe eğitici çizgi film (renkler, sayma, yardımlaşma).

- `cikti/pitircik_gokkusagi.mp4` — 1920x1080, 24 fps, 10:23
- `cikti/thumbnail.png`, `cikti/altyazi.srt`, `YOUTUBE.md` — yükleme materyalleri

## Yeniden üretmek
```
pip install pycairo numpy
python3 timeline.py      # sesleri cümlelere hizalar (audio/*.mp3)
python3 render.py        # kareleri çizer (build/part*.mp4)
python3 audio_mix.py     # müzik + efekt + anlatım
ffmpeg -f concat -safe 0 -i build/parts.txt -i build/final_audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest cikti/pitircik_gokkusagi.mp4
```
Küçük resim: `python3 thumbnail.py`. Senaryo `script.py` içinde; `render.py --png 60 135` ile tek kare önizleme alınabilir.
Yazı tipi: Baloo 2 (OFL).
