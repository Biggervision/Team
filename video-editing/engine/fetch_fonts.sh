#!/usr/bin/env bash
# Downloads the Google Fonts (OFL) used by the master style into ./fonts
set -euo pipefail
mkdir -p fonts && cd fonts
base=https://raw.githubusercontent.com/google/fonts/main/ofl
for f in Regular Medium SemiBold Bold ExtraBold; do curl -sSLO "$base/poppins/Poppins-$f.ttf"; done
curl -sSL -o Playfair-Italic.ttf "$base/playfairdisplay/PlayfairDisplay-Italic%5Bwght%5D.ttf"
