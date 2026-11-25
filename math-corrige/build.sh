#!/bin/zsh
# Usage : build.sh corrige.html [sortie.pdf]
# Rend le HTML en PDF A4 (Chrome headless) puis crée <sortie>_apercu.png (planche de toutes les pages) pour contrôle.
set -e
HTML="${1:A}"; OUT="${2:-${HTML:r}.pdf}"; OUT="${OUT:A}"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
  --allow-file-access-from-files --no-pdf-header-footer --virtual-time-budget=8000 \
  --print-to-pdf="$OUT" "file://$HTML" 2>/dev/null
PREV="$(mktemp -d)"
pdftoppm -r 55 -png "$OUT" "$PREV/p"
"${PY:-python3}" - "$PREV" "${OUT:r}_apercu.png" <<'EOF'
import sys,glob
from PIL import Image
ims=[Image.open(f) for f in sorted(glob.glob(sys.argv[1]+'/p-*.png'))]
w,h=ims[0].size; c=min(4,len(ims)); r=(len(ims)+c-1)//c
S=Image.new('RGB',(c*(w+16),r*(h+16)),'#bbb')
for i,im in enumerate(ims): S.paste(im,((i%c)*(w+16)+8,(i//c)*(h+16)+8))
S.save(sys.argv[2]); print(len(ims),'pages ->',sys.argv[2])
EOF
pdffonts "$OUT" | grep -q PatrickHand && echo "police Patrick Hand OK" || echo "ATTENTION : Patrick Hand non embarquée (connexion Google Fonts ?)"
