#!/bin/bash
# GALLERY — yangi videoga sahifa + QR + kartochka yasaydi.
#
#   ./yangi-video.sh ~/Desktop/IMG_1234.MP4
#
# Keyingi bo'sh raqamni o'zi topadi (7, 8, 9 ...), videoni siqadi,
# sahifani yasaydi, GitHub'ga yuboradi va QR/kartochkani
# ~/Desktop/GALLERY-QR ichiga qo'yadi.

set -euo pipefail

SITE="$HOME/gallery-qr-site"
TOOLS="/private/tmp/claude-501/-Users-shukurullayevbilol/8aa47248-7fa8-46ce-a8b2-debcf10cf965/scratchpad/gallery"
OUT="$HOME/Desktop/GALLERY-QR"
PY="/tmp/qrenv/bin/python"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

SRC="${1:-}"
if [ -z "$SRC" ] || [ ! -f "$SRC" ]; then
  echo "Video faylni ko'rsating:  ./yangi-video.sh ~/Desktop/IMG_1234.MP4" >&2
  exit 1
fi

# keyingi bo'sh raqam
N=1
while [ -d "$SITE/$N" ]; do N=$((N + 1)); done
echo "→ yangi sahifa: /G/$N"

mkdir -p "$SITE/$N"
ffmpeg -loglevel error -y -i "$SRC" \
  -vf "scale='min(720,iw)':'min(1280,ih)':force_original_aspect_ratio=decrease:force_divisible_by=2" \
  -c:v libx264 -crf 28 -preset medium -profile:v high \
  -c:a aac -b:a 96k -movflags +faststart "$SITE/$N/v.mp4"
ffmpeg -loglevel error -y -ss 0.8 -i "$SITE/$N/v.mp4" -frames:v 1 -q:v 5 "$SITE/$N/p.jpg"
cp "$TOOLS/page_tpl.html" "$SITE/$N/index.html"
echo "→ video tayyor: $(du -h "$SITE/$N/v.mp4" | cut -f1)"

# QR + kartochka
cd "$TOOLS"
URL="HTTPS://BSORIPOVIC0.GITHUB.IO/G/$N"
"$PY" - "$N" "$URL" <<'PYEOF'
import sys, re, pathlib, segno
n, url = sys.argv[1], sys.argv[2]
S = 10.0
q = segno.make(url, error='h'); m = [list(r) for r in q.matrix]; k = len(m)
pad = 4 * S; W = k * S + 2 * pad; cx = cy = k // 2
cells = ''.join('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f"/>' % (pad + c * S, pad + r * S, S, S)
                for r in range(k) for c in range(k)
                if m[r][c] and not (abs(c - cx) <= 1 and abs(r - cy) <= 1))
leaf = ('<g transform="translate(%.1f,%.1f)"><circle r="%.1f" fill="#FFFFFF"/>'
        '<path d="M0 -10 C6 -6 7.3 2.3 0 9 C-7.3 2.3 -6 -6 0 -10 Z" fill="none" stroke="#C9A550" stroke-width="1.8"/>'
        '<path d="M0 -7 L0 6.8" stroke="#C9A550" stroke-width="1.5" stroke-linecap="round"/></g>'
        % (pad + cx * S + S / 2, pad + cy * S + S / 2, 1.7 * S))
pathlib.Path('qr_%s.svg' % n).write_text(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.0f %.0f">'
    '<rect width="%.0f" height="%.0f" fill="#FFFFFF"/><g fill="#0F1B4C">%s</g>%s</svg>'
    % (W, W, W, W, cells, leaf))
pathlib.Path('card_%s.html' % n).write_text(
    pathlib.Path('card_tpl.html').read_text().replace('QRFILE', 'qr_%s.svg' % n))
print('   QR:', q.version, 'versiya,', k, 'katak')
PYEOF

"$CHROME" --headless=new --disable-gpu --hide-scrollbars --allow-file-access-from-files \
  --window-size=1004,638 --screenshot="$TOOLS/karta_$N.png" "file://$TOOLS/card_$N.html" >/dev/null 2>&1

mkdir -p "$OUT"
cp "$TOOLS/karta_$N.png" "$OUT/kartochka-$N.png"
cp "$TOOLS/qr_$N.svg" "$OUT/qr-$N.svg"
echo "$N -> https://bsoripovic0.github.io/G/$N" >> "$OUT/HAVOLALAR.txt"

cd "$SITE"
git add -A
git -c user.email=bs.oripovic@gmail.com -c user.name="Bilol" commit -qm "yangi video: /G/$N"
git push -q origin main

echo "✓ tayyor: https://bsoripovic0.github.io/G/$N"
echo "  kartochka: $OUT/kartochka-$N.png"
echo "  (sahifa 1–3 daqiqada ochiladi — GitHub yangilashi uchun vaqt kerak)"
