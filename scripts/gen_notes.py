import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from talk_content import SLIDES

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "speaker-notes.md")

lines = []
lines.append("# Speaker Notes — Uncertainty, Active Learning, and Safe Control")
lines.append("### A vision for trustworthy AI/ML/robotics — from ground robots to drones")
lines.append("Vikas Dhiman · CVAR Lab, University of Maine · RIT · August 6, 2026\n")
lines.append("---\n")

n = 0
for s in SLIDES:
    n += 1
    t = s.get("title", "")
    sub = s.get("subtitle", "")
    header = f"## Slide {n}: {t}" + (f" — {sub}" if sub else "")
    lines.append(header)

    bullets = s.get("bullets") or s.get("pubs")
    if bullets:
        lines.append("")
        lines.append("**On-slide content:**")
        for b in bullets:
            lines.append(f"- {b}")

    if s.get("pillars"):
        lines.append("")
        lines.append("**On-slide content:** " + " | ".join(p[0].replace(chr(10), " ") for p in s["pillars"]))
    if s.get("items"):
        lines.append("")
        lines.append("**On-slide content:** " + " | ".join(i[0].replace(chr(10), " ") for i in s["items"]))
    if s.get("videos"):
        lines.append("")
        lines.append("**Embedded videos (source credit):**")
        for v in s["videos"]:
            lines.append(f"- [{v['caption']}]({v['url']})")
    if s.get("steps"):
        lines.append("")
        lines.append("**On-slide content (pipeline):** " + " -> ".join(st.replace(chr(10), " ") for st in s["steps"]))

    notes = s.get("notes", "").strip()
    lines.append("")
    lines.append("**Speaker notes:**")
    lines.append("")
    lines.append(notes)
    lines.append("")
    lines.append("---")
    lines.append("")

with open(OUT, "w") as f:
    f.write("\n".join(lines))

print("wrote", OUT, "slides:", n)
