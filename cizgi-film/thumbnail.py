# YouTube küçük resmi: "RENKLER KAYBOLDU!" — yarısı gri, yarısı renkli gökkuşağı
import cairo, math, os
from draw import *

def main(out):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); cr = cairo.Context(s)
    back, front = make_layers("intro")
    cr.set_source_surface(back); cr.paint()
    sun(cr, 1720, 150, 80, 0.3)
    # sol yarı gri, sağ yarı renkli gökkuşağı
    cr.save(); cr.rectangle(0, 0, 1010, H); cr.clip(); rainbow(cr, 1010, 1000, 760, 62, [0] * 7); cr.restore()
    cr.save(); cr.rectangle(1010, 0, W, H); cr.clip(); rainbow(cr, 1010, 1000, 760, 62, [1] * 7); cr.restore()
    cr.set_source_surface(front); cr.paint()
    # sol tarafı soluklaştır (renkler kaybolmuş hissi)
    cr.rectangle(0, 0, 1010, H); cr.set_source_rgba(0.5, 0.5, 0.55, 0.45)
    cr.set_operator(cairo.OPERATOR_SATURATE); cr.fill(); cr.set_operator(cairo.OPERATOR_OVER)
    cr.rectangle(0, 0, 1010, H); cr.set_source_rgba(0.85, 0.85, 0.88, 0.25); cr.fill()
    # renk topları sağdan sepete uçuyor
    for i in range(7):
        k = i / 6
        x, y = 1180 - k * 330, 560 - math.sin(k * PI) * 170 + k * 40
        cr.arc(x, y, 46, 0, 2 * PI); paint(cr, COLORS[i], 6, (1, 1, 1))
        cr.arc(x - 14, y - 16, 12, 0, 2 * PI); cr.set_source_rgba(1, 1, 1, 0.8); cr.fill()
    # büyük, şaşkın Pıtırcık
    hedgehog(cr, 640, 1110, 2.6, 0, mood="surprise", look=(0.5, -0.8))
    bird(cr, 1560, 700, 1.6, 0.2, face=-1)
    # başlık yazısı
    text(cr, "RENKLER", 520, 150, 190, (1, 0.85, 0.15), (0.35, 0.12, 0.35), 34)
    text(cr, "KAYBOLDU!", 600, 330, 190, (1, 1, 1), (0.85, 0.15, 0.25), 34)
    # rozet
    cr.save(); cr.translate(1640, 900); cr.rotate(-0.12)
    rrect(cr, -230, -70, 460, 140, 50); cr.set_source_rgb(0.98, 0.3, 0.45); cr.fill_preserve()
    cr.set_source_rgb(1, 1, 1); cr.set_line_width(8); cr.stroke()
    text(cr, "1 2 3 SAY!", 0, -6, 84, (1, 1, 1), (0.6, 0.1, 0.25), 10)
    cr.restore()
    s.write_to_png(out)

if __name__ == "__main__":
    os.makedirs("build", exist_ok=True)
    main("build/thumb_full.png")
