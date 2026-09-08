"""Render a talk_content.py-style SLIDES list to a self-contained reveal.js deck.

Usage:
    python3 scripts/build_reveal.py [path/to/talk_content.py]

With no argument, uses talk_content.py next to this script (the original RIT
talk). Any other talk_content.py (e.g. chapters/.../deck/talk_content.py) can
be passed explicitly -- each deck keeps its own content module, output is
written to <content-dir>/slides/index.html, next to that content module.
"""
import sys, os, html, re, importlib.util

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_content(path):
    spec = importlib.util.spec_from_file_location("talk_content", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.SLIDES, mod.MEDIA


CONTENT_PATH = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(SCRIPT_DIR, "talk_content.py")
CONTENT_DIR = os.path.dirname(CONTENT_PATH)
SLIDES, MEDIA = load_content(CONTENT_PATH)

SLIDES_DIR = os.path.join(CONTENT_DIR, "slides")
OUT = os.path.join(SLIDES_DIR, "index.html")

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def rel(path):
    """Path relative to slides/index.html, for use as an HTML src/href."""
    return os.path.relpath(path, start=SLIDES_DIR)


def esc(text):
    return html.escape(text, quote=False)


def linkify(text):
    """Escape text but turn [label](url) into a real <a> link."""
    out, pos = [], 0
    for m in LINK_RE.finditer(text):
        out.append(esc(text[pos:m.start()]))
        label, url = m.group(1), m.group(2)
        out.append(f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(label)}</a>')
        pos = m.end()
    out.append(esc(text[pos:]))
    return "".join(out)


def notes_html(s):
    notes = s.get("notes", "").strip()
    if not notes:
        return ""
    paras = "".join(f"<p>{esc(p.strip())}</p>" for p in notes.split("\n\n") if p.strip())
    return f'<aside class="notes">{paras}</aside>'


def bullets_html(items, cls="bullets", fragments=True):
    li_cls = ' class="fragment"' if fragments else ""
    lis = "\n".join(f"      <li{li_cls}>{linkify(b)}</li>" for b in items)
    return f'<ul class="{cls}">\n{lis}\n    </ul>'


def kicker_title(title, kicker=None):
    k = f'<div class="kicker">{esc(kicker.upper())}</div>' if kicker else ""
    return f'{k}<h2>{esc(title)}</h2><div class="underline"></div>'


def render_slide(s, idx):
    typ = s["type"]
    notes = notes_html(s)

    if typ == "title":
        logo = f'<img class="logo" src="{rel(f"{MEDIA}/umaine-logo.png")}" alt="UMaine logo">' \
            if os.path.isfile(f"{MEDIA}/umaine-logo.png") else ""
        return f'''<section class="s-title" data-background-color="#141F38">
  {logo}
  <h1>{esc(s["title"])}</h1>
  <p class="subtitle">{esc(s["subtitle"])}</p>
  <div class="rule"></div>
  <p class="footer-line">{esc(s["footer"])}</p>
  {notes}
</section>'''

    if typ == "section":
        return f'''<section class="s-section" data-background-color="#141F38">
  <div class="rule-top"></div>
  <div class="kicker">{esc(s["title"].upper())}</div>
  <h1>{esc(s["subtitle"])}</h1>
  {notes}
</section>'''

    if typ == "bio":
        img = f'<img class="bio-photo" src="{rel(s["img"])}" alt="">'
        return f'''<section>
  {kicker_title(s["title"], s.get("kicker"))}
  <div class="row">
    <div class="col-img">{img}</div>
    <div class="col-text">{bullets_html(s["bullets"], fragments=s.get("fragments", True))}</div>
  </div>
  {notes}
</section>'''

    if typ == "content":
        return f'''<section>
  {kicker_title(s["title"], s.get("kicker"))}
  {bullets_html(s["bullets"], cls="bullets wide", fragments=s.get("fragments", True))}
  {notes}
</section>'''

    if typ == "content_img":
        img = f'<img src="{rel(s["img"])}" alt="">'
        return f'''<section>
  {kicker_title(s["title"], s.get("kicker"))}
  <div class="row">
    <div class="col-text">{bullets_html(s["bullets"], fragments=s.get("fragments", True))}</div>
    <div class="col-img">{img}</div>
  </div>
  {notes}
</section>'''

    if typ == "image_full":
        return f'''<section>
  {kicker_title(s["title"], s.get("kicker"))}
  <div class="full-img-wrap"><img src="{rel(s["img"])}" alt=""></div>
  <p class="caption">{esc(s["caption"])}</p>
  {notes}
</section>'''

    if typ == "code":
        bullets = bullets_html(s["bullets"], cls="bullets small", fragments=False) if s.get("bullets") else ""
        code_block = f'<pre class="code-block"><code>{esc(s["code"])}</code></pre>'
        colab = f'<p class="colab-note">{linkify(s["colab_note"])}</p>' if s.get("colab_note") else ""
        if s.get("img"):
            body = f'''<div class="row code-row">
    <div class="col-code">{bullets}{code_block}{colab}</div>
    <div class="col-img"><img src="{rel(s["img"])}" alt=""></div>
  </div>'''
        else:
            body = f'{bullets}{code_block}{colab}'
        return f'''<section>
  {kicker_title(s["title"], s.get("kicker"))}
  {body}
  {notes}
</section>'''

    if typ == "gallery":
        cards = ""
        for path, caption in s["images"]:
            cards += f'''<div class="gallery-card">
        <img src="{rel(path)}" alt="">
        <div class="gallery-caption">{esc(caption)}</div>
      </div>'''
        return f'''<section>
  {kicker_title(s["title"], s.get("kicker"))}
  <div class="gallery-row">{cards}</div>
  {notes}
</section>'''

    if typ == "demo":
        bullets = bullets_html(s["bullets"], cls="bullets wide", fragments=s.get("fragments", True))
        img = f'<div class="col-img"><img src="{rel(s["img"])}" alt=""></div>' if s.get("img") else ""
        link = (f'<a class="demo-link" href="{esc(s["colab_url"])}" target="_blank" rel="noopener">'
                f'&#9654; Open in Colab</a>')
        return f'''<section class="s-demo" data-background-color="#1E8A7A">
  <div class="kicker">LIVE DEMO</div>
  <h2>{esc(s["title"])}</h2>
  <div class="underline"></div>
  <div class="row">
    <div class="col-text">{bullets}{link}</div>
    {img}
  </div>
  {notes}
</section>'''

    if typ == "pillars":
        colors = ["#2E6FB8", "#1E8A7A", "#E07A2C"]
        boxes = ""
        for i, (name, desc) in enumerate(s["pillars"]):
            boxes += f'''<div class="pillar-box" style="background:{colors[i % 3]}">
        <div class="pillar-name">{esc(name)}</div>
        <div class="pillar-desc">{esc(desc)}</div>
      </div>'''
        return f'''<section>
  {kicker_title(s["title"], s.get("kicker"))}
  <p class="lead">{esc(s["lead"])}</p>
  <div class="pillars-row">{boxes}</div>
  <div class="pillars-outcome">{esc(s["outcome"])}</div>
  {notes}
</section>'''

    if typ == "triad":
        colors = ["#B53A3A", "#1E8A7A", "#B07A1E"]
        boxes = ""
        for i, (name, desc) in enumerate(s["items"]):
            check = '<div class="triad-check">&#10003; the target</div>' if i == 1 else ""
            boxes += f'''<div class="triad-box" style="border-color:{colors[i % 3]}">
        <div class="triad-top" style="background:{colors[i % 3]}"></div>
        <div class="triad-name" style="color:{colors[i % 3]}">{esc(name)}</div>
        <div class="triad-desc">{esc(desc)}</div>
        {check}
      </div>'''
        return f'''<section>
  {kicker_title(s["title"], s.get("kicker"))}
  <div class="triad-row">{boxes}</div>
  {notes}
</section>'''

    if typ == "pipeline":
        colors = ["#243B64", "#2E6FB8", "#1E8A7A", "#E07A2C", "#7A3E9E"]
        steps = ""
        n = len(s["steps"])
        for i, step in enumerate(s["steps"]):
            steps += f'''<div class="pipe-box" style="background:{colors[i % 5]}">
        <div class="pipe-num">{i + 1}</div>
        <div class="pipe-text">{esc(step)}</div>
      </div>'''
            if i < n - 1:
                steps += '<div class="pipe-arrow">&#9654;</div>'
        return f'''<section>
  {kicker_title(s["title"], s.get("kicker"))}
  <div class="pipe-row">{steps}</div>
  <p class="lead center">{esc(s["loop_label"])}</p>
  {notes}
</section>'''

    if typ == "videos":
        cards = ""
        for v in s["videos"]:
            cards += f'''<div class="video-card fragment">
        <video controls preload="metadata" data-autoplay poster="{rel(v["thumb"])}">
          <source src="{rel(v["video"])}" type="video/mp4">
        </video>
        <div class="video-caption">{esc(v["caption"])}</div>
        <a class="video-src" href="{esc(v["url"])}" target="_blank" rel="noopener">{esc(v["url"])}</a>
      </div>'''
        return f'''<section>
  {kicker_title(s["title"], s.get("kicker"))}
  {bullets_html(s["bullets"], cls="bullets small", fragments=s.get("fragments", True))}
  <div class="video-row">{cards}</div>
  {notes}
</section>'''

    if typ == "team":
        imgs = "".join(f'<img class="team-photo" src="{rel(p)}" alt="">' for p in s["imgs"])
        return f'''<section>
  {kicker_title(s["title"], s.get("kicker"))}
  <div class="row">
    <div class="col-img team-photos">{imgs}</div>
    <div class="col-text">{bullets_html(s["bullets"], fragments=s.get("fragments", True))}</div>
  </div>
  {notes}
</section>'''

    if typ == "pubs":
        return f'''<section>
  {kicker_title(s["title"], s.get("kicker"))}
  {bullets_html(s["pubs"], cls="bullets pubs", fragments=s.get("fragments", True))}
  {notes}
</section>'''

    if typ == "end":
        return f'''<section class="s-title" data-background-color="#141F38">
  <h1>{esc(s["title"])}</h1>
  <p class="subtitle">{esc(s["subtitle"])}</p>
  <div class="rule"></div>
  <p class="footer-line">{esc(s["contact"])}</p>
  {notes}
</section>'''

    raise ValueError(f"unhandled slide type: {typ}")

CSS = """
:root{
  --navy:#141F38; --navy-light:#243B64; --blue:#2E6FB8; --teal:#1E8A7A;
  --orange:#E07A2C; --grey:#3A3F4B; --light-bg:#F5F6F8; --line-grey:#CED3DA;
  --muted:#8A909C;
}
.reveal{font-family:'Calibri','Segoe UI',Helvetica,Arial,sans-serif;color:var(--grey);}
.reveal .slides{text-align:left;}
.reveal .slides section{padding-top:0.6em;}
.reveal h1,.reveal h2,.reveal h3{font-family:inherit;text-transform:none;letter-spacing:0;}
.reveal a{color:var(--blue);}

.kicker{color:var(--orange);font-weight:700;font-size:.5em;letter-spacing:.06em;margin-bottom:.15em;}
.reveal h2{color:var(--navy);font-size:1.35em;font-weight:700;margin:0 0 .1em 0;}
.underline{width:70px;height:4px;background:var(--orange);margin:.15em 0 .5em 0;}

.reveal ul.bullets{list-style:none;margin:0;padding:0;}
.reveal ul.bullets li{position:relative;padding-left:1em;margin-bottom:.5em;font-size:.62em;line-height:1.3;}
.reveal ul.bullets li::before{content:"\\2022";position:absolute;left:0;color:var(--blue);}
.reveal ul.bullets.wide li{font-size:.6em;margin-bottom:.55em;}
.reveal ul.bullets.small li{font-size:.48em;margin-bottom:.3em;}
.reveal ul.bullets.pubs li{font-size:.5em;margin-bottom:.55em;}

.row{display:flex;gap:1.2em;align-items:flex-start;}
.col-img{flex:0 0 34%;}
.col-text{flex:1;}
.col-img img,.bio-photo{width:100%;border-radius:4px;border:1px solid var(--line-grey);}

.full-img-wrap{text-align:center;margin:.4em 0;}
.full-img-wrap img{max-height:56vh;max-width:100%;border:1px solid var(--line-grey);}
.caption{font-size:.42em;font-style:italic;color:var(--grey);text-align:center;}

.lead{font-size:.5em;font-style:italic;color:var(--grey);margin:.3em 0 .6em 0;}
.lead.center{text-align:center;}

.pillars-row{display:flex;gap:.6em;margin-top:.6em;}
.pillar-box{flex:1;color:#fff;border-radius:4px;padding:1em .8em;text-align:center;}
.pillar-name{font-size:.7em;font-weight:700;white-space:pre-line;margin-bottom:.5em;}
.pillar-desc{font-size:.42em;line-height:1.3;}
.pillars-outcome{margin-top:.5em;background:var(--navy);color:#fff;text-align:center;
  padding:.5em;border-radius:4px;font-weight:700;font-size:.55em;}

.triad-row{display:flex;gap:.5em;margin-top:1em;}
.triad-box{flex:1;background:var(--light-bg);border:2px solid;border-radius:4px;
  padding-bottom:1em;position:relative;text-align:center;}
.triad-top{height:6px;border-radius:2px 2px 0 0;}
.triad-name{font-weight:700;font-size:.55em;margin:.6em .3em .5em .3em;white-space:pre-line;}
.triad-desc{font-size:.4em;padding:0 .8em;line-height:1.3;color:var(--grey);}
.triad-check{color:var(--teal);font-weight:700;font-size:.4em;margin-top:.6em;}

.pipe-row{display:flex;align-items:center;margin-top:.8em;}
.pipe-box{flex:1;color:#fff;border-radius:4px;padding:.9em .5em;text-align:center;min-height:6em;
  display:flex;flex-direction:column;justify-content:center;}
.pipe-num{color:#FFC87A;font-weight:700;font-size:.5em;margin-bottom:.4em;}
.pipe-text{font-size:.36em;white-space:pre-line;line-height:1.25;font-weight:600;}
.pipe-arrow{color:var(--navy);font-size:.5em;padding:0 .15em;}

.video-row{display:flex;gap:.6em;margin-top:.5em;}
.video-card{flex:1;text-align:center;}
.video-card video{width:100%;aspect-ratio:16/9;background:#000;border:1px solid var(--line-grey);}
.video-caption{font-weight:700;font-size:.42em;color:var(--navy);margin-top:.4em;}
.video-src{display:block;font-size:.32em;color:var(--muted);margin-top:.15em;word-break:break-all;}

.team-photos{display:flex;flex:0 0 40%;gap:.4em;}
.team-photo{width:32%;border-radius:4px;border:1px solid var(--line-grey);object-fit:cover;aspect-ratio:1/1;}

/* code slides */
.code-row .col-code{flex:1.3;}
.code-row .col-img{flex:0 0 32%;}
pre.code-block{background:#1E2430;color:#E8EAED;border-radius:5px;padding:.5em .7em;
  font-size:.40em;line-height:1.35;overflow:auto;max-height:56vh;}
pre.code-block code{font-family:'Consolas','Menlo',monospace;white-space:pre;}
p.colab-note{font-size:.36em;font-style:italic;color:var(--muted);margin-top:.4em;}

/* gallery */
.gallery-row{display:flex;gap:.5em;margin-top:.6em;flex-wrap:wrap;}
.gallery-card{flex:1;min-width:20%;text-align:center;}
.gallery-card img{width:100%;border:1px solid var(--line-grey);border-radius:4px;}
.gallery-caption{font-size:.34em;color:var(--grey);margin-top:.3em;}

/* demo slides */
.s-demo{color:#fff;}
.s-demo .kicker{color:#FFD9A8;}
.s-demo h2{color:#fff;}
.s-demo .bullets li{color:#fff;font-size:.6em;}
.s-demo .bullets li::before{color:#FFD9A8;}
.s-demo .col-img img{border:2px solid rgba(255,255,255,.5);}
a.demo-link{display:inline-block;margin-top:.7em;background:var(--orange);color:#fff !important;
  font-weight:700;font-size:.55em;padding:.5em 1em;border-radius:4px;text-decoration:none;}

/* title / section / end slides */
.s-title, .s-section{color:#fff;}
.s-title h1{font-size:1.5em;font-weight:700;color:#fff;margin-bottom:.25em;}
.s-title .subtitle{font-size:.65em;font-style:italic;color:#C9D3E6;margin:0 0 .5em 0;}
.s-title .rule{width:90px;height:4px;background:var(--orange);margin-bottom:1.2em;}
.s-title .footer-line{font-size:.5em;color:#C9D3E6;}
.s-title .logo{
position:absolute;bottom:.6em;right:.6em;height:1.3em;background-color:#fff}

.s-section .rule-top{position:absolute;top:42%;left:0;right:0;height:3px;background:var(--orange);}
.s-section .kicker{position:absolute;top:calc(42% - 1.6em);left:0;color:var(--orange);font-size:.5em;}
.s-section h1{position:absolute;top:calc(42% + .5em);left:0;right:0;font-size:1.3em;font-weight:700;color:#fff;}

.reveal .slide-number{color:var(--muted);background-color:#fff;}
"""

HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="vendor/reveal/reset.css">
<link rel="stylesheet" href="vendor/reveal/reveal.css">
<link rel="stylesheet" href="vendor/reveal/theme/white.css">
<style>{css}</style>
</head>
<body>
<div class="reveal">
  <div class="slides">
{slides}
  </div>
</div>
<script src="vendor/reveal/reveal.js"></script>
<script src="vendor/reveal/plugin/notes.js"></script>
<script>
  Reveal.initialize({{
    width: 1280,
    height: 720,
    margin: 0.06,
    center : true,
    progress: true,
    slideNumber: 'c/t',
    transition: 'fade',
	plugins: [ RevealNotes ],
  }}).then(() => {{
    // Videos on a "videos" slide are revealed one at a time as fragments
    // (data-autoplay on <video>, class="fragment" on the card). Reveal.js
    // core already autoplays a fragment's video once it becomes visible and
    // pauses it when it's hidden again (stepping backward) -- see
    // js/controllers/fragments.js + slidecontent.js's startEmbeddedContent/
    // stopEmbeddedContent. What's not built in is enforcing "just one plays
    // at a time": whenever a video fragment appears, pause every other
    // video. Re-entering a slide backward (Reveal.prev() from the *next*
    // slide) marks all of that slide's fragments visible in one shot rather
    // than firing fragmentshown per-fragment, so it needs its own handler:
    // keep only the last (highest-index) visible fragment's video playing.
    const pauseAllBut = keep => document.querySelectorAll('.reveal video').forEach(v => {{
      if (v !== keep) v.pause();
    }});

    Reveal.on('fragmentshown', event => {{
      const shown = event.fragment.matches('video') ? event.fragment
                    : event.fragment.querySelector('video');
      if (shown) pauseAllBut(shown);
    }});

    Reveal.on('slidechanged', event => {{
      setTimeout(() => {{
        const visible = Array.from(event.currentSlide.querySelectorAll('.fragment.visible'));
        const last = visible[visible.length - 1];
        const video = last && (last.matches('video') ? last : last.querySelector('video'));
        if (video) pauseAllBut(video);
      }}, 0);
    }});
  }});
</script>
</body>
</html>
"""


def main():
    os.makedirs(SLIDES_DIR, exist_ok=True)
    slides_html = "\n".join(render_slide(s, i) for i, s in enumerate(SLIDES))
    doc = HTML_TEMPLATE.format(
        title=os.path.basename(CONTENT_DIR) or "Talk",
        css=CSS,
        slides=slides_html,
    )
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(doc)
    print("wrote", OUT, "slides:", len(SLIDES))


if __name__ == "__main__":
    main()
