#!/usr/bin/env bash
# Rebuild the RIT talk from talk_content.py.
# Regenerates: build/rit-talk.pptx, ../speaker-notes.md, ../rit-vision-talk.odp
# Optional: pass --preview to also render PNG slide previews into build/preview/
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

PYTHON="${PYTHON:-python3}"

echo "== Building slides (pptx) =="
"$PYTHON" build_deck.py

echo "== Writing speaker notes (markdown) =="
"$PYTHON" gen_notes.py

echo "== Converting pptx -> odp =="
soffice --headless --convert-to odp rit-talk.pptx --outdir . >/dev/null
cp rit-talk.odp ../rit-vision-talk.odp

if [[ "${1:-}" == "--preview" ]]; then
    echo "== Rendering PNG previews =="
    soffice --headless --convert-to pdf rit-talk.odp --outdir . >/dev/null
    mkdir -p preview
    rm -f preview/*.png
    pdftoppm -png -r 80 rit-talk.pdf preview/slide
    echo "Previews in build/preview/"
fi

echo "== Done =="
echo "  ../rit-vision-talk.odp"
echo "  ../speaker-notes.md"
