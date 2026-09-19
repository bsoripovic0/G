import pathlib
import re
import subprocess
import os

HERE = pathlib.Path('.').resolve()
CH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CARD_W_PX, CARD_H_PX = 1004, 638          # existing card design, 300 dpi
CARD_W_MM, CARD_H_MM = 85.6, 54.0         # standard business card
SCALE = CARD_W_MM / (CARD_W_PX * 25.4 / 96)   # px -> mm at 96 dpi CSS


def card_markup(n):
    """Take the rendered card html and wrap its body content in a scaled box."""
    src = (HERE / ('card_%d.html' % n)).read_text()
    head = re.search(r'<style>.*?</style>', src, re.S).group(0)
    body = src.split('</style>', 1)[1]
    head = head.replace('body{width:1004px;height:638px;', '.card{width:1004px;height:638px;')
    head = head.replace('.frame{position:absolute', '.card .frame{position:absolute')
    return head, body


def page(n):
    head, body = card_markup(n)
    return """<!doctype html><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=Manrope:wght@300;400;500;600&display=swap">
%s
<style>
@page{size:%.1fmm %.1fmm;margin:0}
html,body{margin:0;padding:0;width:%.1fmm;height:%.1fmm;overflow:hidden}
.holder{width:%.1fmm;height:%.1fmm;overflow:hidden}
.card{transform:scale(%.5f);transform-origin:top left}
</style>
<div class="holder"><div class="card">%s</div></div>
""" % (head, CARD_W_MM, CARD_H_MM, CARD_W_MM, CARD_H_MM, CARD_W_MM, CARD_H_MM, SCALE, body)


def sheet():
    heads, bodies = [], []
    for n in range(1, 7):
        h, b = card_markup(n)
        if n == 1:
            heads.append(h)
        bodies.append(b)
    cards = ''
    for i, b in enumerate(bodies):
        col, row = i % 2, i // 2
        x = 14 + col * (CARD_W_MM + 6 + 8)
        y = 20 + row * (CARD_H_MM + 6 + 8)
        cards += ('<div class="slot" style="left:%.1fmm;top:%.1fmm">'
                  '<span class="m tl"></span><span class="m tr"></span><span class="m bl"></span><span class="m br"></span>'
                  '<div class="holder"><div class="card">%s</div></div></div>' % (x, y, b))
    bleed_w, bleed_h = CARD_W_MM + 6, CARD_H_MM + 6
    bleed_scale = SCALE * bleed_w / CARD_W_MM
    return """<!doctype html><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=Manrope:wght@300;400;500;600&display=swap">
%s
<style>
@page{size:A4;margin:0}
html,body{margin:0;padding:0;width:210mm;height:297mm;background:#fff;position:relative;
  font-family:Manrope,sans-serif}
.slot{position:absolute;width:%.1fmm;height:%.1fmm}
.holder{width:100%%;height:100%%;overflow:hidden}
.card{transform:scale(%.5f);transform-origin:top left}
.m{position:absolute;width:4mm;height:4mm;border:0}
.m.tl{left:-1mm;top:-1mm;border-left:.2mm solid #8A8A8A;border-top:.2mm solid #8A8A8A}
.m.tr{right:-1mm;top:-1mm;border-right:.2mm solid #8A8A8A;border-top:.2mm solid #8A8A8A}
.m.bl{left:-1mm;bottom:-1mm;border-left:.2mm solid #8A8A8A;border-bottom:.2mm solid #8A8A8A}
.m.br{right:-1mm;bottom:-1mm;border-right:.2mm solid #8A8A8A;border-bottom:.2mm solid #8A8A8A}
.note{position:absolute;left:18mm;bottom:12mm;font-size:8pt;color:#8A8A8A;letter-spacing:.06em}
</style>
%s
<div class="note">GALLERY FLOWER BOUTIQUE · 6 kartochka · 85,6 × 54 mm + 3 mm bleed · burchak belgilari bo'yicha kesing</div>
""" % (heads[0], bleed_w, bleed_h, bleed_scale, cards)


for n in range(1, 7):
    (HERE / ('print_%d.html' % n)).write_text(page(n))
(HERE / 'print_sheet.html').write_text(sheet())

out = pathlib.Path.home() / 'Desktop' / 'GALLERY-QR' / 'bosma'
out.mkdir(parents=True, exist_ok=True)
for n in range(1, 7):
    subprocess.run([CH, '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
                    '--print-to-pdf=' + str(out / ('kartochka-%d.pdf' % n)),
                    'file://' + str(HERE / ('print_%d.html' % n))], capture_output=True)
subprocess.run([CH, '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
                '--print-to-pdf=' + str(out / 'A4-6-kartochka.pdf'),
                'file://' + str(HERE / 'print_sheet.html')], capture_output=True)
print('scale', round(SCALE, 4))
for f in sorted(out.iterdir()):
    print(f.name, f.stat().st_size)
