"""Render a talk_content.py-style SLIDES list to a PowerPoint/ODP-ready .pptx.

Usage:
    python3 scripts/build_deck.py [path/to/talk_content.py] [output.pptx]

With no arguments, uses talk_content.py next to this script (the original
RIT talk) and writes rit-talk.pptx next to it. Any other talk_content.py
(e.g. chapters/.../deck/talk_content.py) can be passed explicitly, with an
optional explicit output path as the second argument.
"""
import sys, os, re, importlib.util

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_content(path):
    spec = importlib.util.spec_from_file_location("talk_content", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.SLIDES, mod.MEDIA


CONTENT_PATH = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(SCRIPT_DIR, "talk_content.py")
CONTENT_DIR = os.path.dirname(CONTENT_PATH)
SLIDES, MEDIA = load_content(CONTENT_PATH)

if len(sys.argv) > 2:
    OUT_PPTX = os.path.abspath(sys.argv[2])
else:
    OUT_PPTX = os.path.join(CONTENT_DIR, "rit-talk.pptx")

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.oxml.ns import qn, nsdecls
from pptx.oxml import parse_xml
from PIL import Image

# ---- palette ----
NAVY = RGBColor(0x14, 0x1F, 0x38)
NAVY_LIGHT = RGBColor(0x24, 0x3B, 0x64)
BLUE = RGBColor(0x2E, 0x6F, 0xB8)
TEAL = RGBColor(0x1E, 0x8A, 0x7A)
ORANGE = RGBColor(0xE0, 0x7A, 0x2C)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_BG = RGBColor(0xF5, 0xF6, 0xF8)
GREY_TXT = RGBColor(0x3A, 0x3F, 0x4B)
LINE_GREY = RGBColor(0xCE, 0xD3, 0xDA)
CODE_BG = RGBColor(0x1E, 0x24, 0x30)
CODE_TXT = RGBColor(0xE8, 0xEA, 0xED)
MUTED = RGBColor(0x8A, 0x90, 0x9C)

FONT = "Calibri"
MONO = "Consolas"

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H
BLANK = prs.slide_layouts[6]


def add_slide():
    return prs.slides.add_slide(BLANK)


def set_bg(slide, color=WHITE):
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = color


def add_rect(slide, x, y, w, h, color, line=False):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    if line:
        shp.line.color.rgb = color
        shp.line.width = Pt(0.5)
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def _preserve_space(run):
    """Force xml:space="preserve" on a run's <a:t>, belt-and-suspenders
    alongside NBSP substitution in add_code_block -- without one of these,
    PowerPoint/LibreOffice are both free to collapse leading/repeated
    whitespace in a run's text, which silently destroys code indentation."""
    t = run._r.find(qn("a:t"))
    if t is not None:
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")


def add_text(slide, x, y, w, h, text, size=18, bold=False, color=GREY_TXT,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, font=FONT, italic=False,
             line_spacing=1.0):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        r = p.add_run()
        r.text = ln
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.name = font
        r.font.color.rgb = color
    return tb


def add_linked_paragraph(p, text, size, color, font=FONT, link_color=BLUE):
    """Add runs to paragraph p, turning [label](url) into a real hyperlink run."""
    pos = 0
    for m in LINK_RE.finditer(text):
        if m.start() > pos:
            r = p.add_run(); r.text = text[pos:m.start()]
            r.font.size = Pt(size); r.font.name = font; r.font.color.rgb = color
        label, url = m.group(1), m.group(2)
        r = p.add_run(); r.text = label
        r.font.size = Pt(size); r.font.name = font; r.font.color.rgb = link_color
        r.font.underline = True
        r.hyperlink.address = url
        pos = m.end()
    if pos < len(text):
        r = p.add_run(); r.text = text[pos:]
        r.font.size = Pt(size); r.font.name = font; r.font.color.rgb = color


def add_bullets(slide, x, y, w, h, items, size=17, color=GREY_TXT, space_after=10, font=FONT):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(space_after)
        p.line_spacing = 1.05
        r = p.add_run(); r.text = "•  "
        r.font.size = Pt(size); r.font.name = font; r.font.color.rgb = color
        add_linked_paragraph(p, item, size, color, font=font)
    return tb


def add_kicker_title(slide, title, kicker=None, dark=False):
    txt_color = WHITE if dark else NAVY
    add_rect(slide, 0, 0, SLIDE_W, Inches(0.14), ORANGE)
    if kicker:
        add_text(slide, Inches(0.55), Inches(0.32), Inches(10), Inches(0.35), kicker.upper(),
                  size=13, bold=True, color=ORANGE, font=FONT)
        title_y = Inches(0.62)
    else:
        title_y = Inches(0.38)
    add_text(slide, Inches(0.55), title_y, Inches(12.2), Inches(0.9), title,
              size=28, bold=True, color=txt_color, font=FONT)
    add_rect(slide, Inches(0.55), title_y + Inches(0.78), Inches(1.3), Pt(3), ORANGE)
    return title_y + Inches(1.0)


def add_footer(slide, page_num, footer_text):
    add_text(slide, Inches(0.55), SLIDE_H - Inches(0.4), Inches(9.5), Inches(0.3),
              footer_text, size=10, color=MUTED)
    add_text(slide, SLIDE_W - Inches(1.2), SLIDE_H - Inches(0.4), Inches(0.7), Inches(0.3),
              str(page_num), size=10, color=MUTED, align=PP_ALIGN.RIGHT)


def fit_picture(slide, path, max_x, max_y, max_w, max_h):
    with Image.open(path) as im:
        iw, ih = im.size
    ar = iw / ih
    box_ar = max_w / max_h
    if ar > box_ar:
        w = max_w
        h = int(max_w / ar)
    else:
        h = max_h
        w = int(max_h * ar)
    x = max_x + (max_w - w) // 2
    y = max_y + (max_h - h) // 2
    pic = slide.shapes.add_picture(path, x, y, width=w, height=h)
    pic.line.color.rgb = LINE_GREY
    pic.line.width = Pt(0.75)
    return pic


def add_code_block(slide, x, y, w, h, code, size=13):
    """A monospace code box.

    PowerPoint/LibreOffice are both allowed to collapse leading and repeated
    whitespace inside a text run unless it's marked non-collapsible, which
    silently destroys Python indentation. Fixed two ways: every space is
    swapped for a non-breaking space (U+00A0, never collapsed by any
    renderer), and xml:space="preserve" is set on the run for good measure.
    """
    box = add_rect(slide, x, y, w, h, CODE_BG)
    tf = box.text_frame
    tf.word_wrap = False
    tf.margin_left = Inches(0.15); tf.margin_right = Inches(0.15)
    tf.margin_top = Inches(0.12); tf.margin_bottom = Inches(0.12)
    lines = code.split("\n")
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.line_spacing = 1.12
        r = p.add_run()
        r.text = (ln if ln.strip() else " ").replace(" ", " ")
        r.font.size = Pt(size); r.font.name = MONO; r.font.color.rgb = CODE_TXT
        _preserve_space(r)
    return box


def set_notes(slide, text):
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = text


def set_media_pause_on_load(slide, shape_ids):
    """Stop embedded videos from autoplaying when the slide loads.

    python-pptx's add_movie() writes a minimal <p:timing> using the compact
    <p:video>/<p:cMediaNode delay="indefinite"> shorthand for "click to
    play". PowerPoint honors that fine, but LibreOffice Impress's PPTX
    importer does not reliably treat delay="indefinite" as "wait for a
    click" and can autoplay the video on slide entry instead. This replaces
    that block with the fuller timing tree PowerPoint itself emits for
    Animation Pane > Add Effect > Media > Pause > Start: With Previous.
    """
    if not shape_ids:
        return
    sld = slide._element
    existing = sld.find(qn("p:timing"))
    if existing is not None:
        sld.remove(existing)

    par_blocks, bld_blocks = [], []
    next_id = 3
    for spid in shape_ids:
        outer_id, inner_id, cmd_id = next_id, next_id + 1, next_id + 2
        next_id += 3
        par_blocks.append(f"""
          <p:par>
            <p:cTn id="{outer_id}" fill="hold">
              <p:stCondLst><p:cond delay="0"/></p:stCondLst>
              <p:childTnLst>
                <p:par>
                  <p:cTn id="{inner_id}" presetID="1" presetClass="mediacall" presetSubtype="0" fill="hold" nodeType="withEffect">
                    <p:stCondLst><p:cond delay="0"/></p:stCondLst>
                    <p:childTnLst>
                      <p:cmd type="call" cmd="togglePause">
                        <p:cBhvr>
                          <p:cTn id="{cmd_id}" dur="1" fill="hold"/>
                          <p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>
                        </p:cBhvr>
                      </p:cmd>
                    </p:childTnLst>
                  </p:cTn>
                </p:par>
              </p:childTnLst>
            </p:cTn>
          </p:par>""")
        bld_blocks.append(f'<p:bldMedia spid="{spid}"/>')

    timing_xml = f"""<p:timing {nsdecls('p')}>
      <p:tnLst>
        <p:par>
          <p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">
            <p:childTnLst>
              <p:seq concurrent="1" nextAc="seek">
                <p:cTn id="2" dur="indefinite" nodeType="mainSeq">
                  <p:childTnLst>
                    {''.join(par_blocks)}
                  </p:childTnLst>
                </p:cTn>
                <p:prevCondLst>
                  <p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond>
                </p:prevCondLst>
                <p:nextCondLst>
                  <p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond>
                </p:nextCondLst>
              </p:seq>
            </p:childTnLst>
          </p:cTn>
        </p:par>
      </p:tnLst>
      <p:bldLst>
        {''.join(bld_blocks)}
      </p:bldLst>
    </p:timing>"""

    sld.append(parse_xml(timing_xml))


FOOTER_TEXT = f"{os.path.basename(CONTENT_DIR.rstrip('/')) or 'Talk'}  —  {SLIDES[0].get('footer', '') if SLIDES else ''}"

page = 0

for s in SLIDES:
    page += 1
    typ = s["type"]
    slide = add_slide()
    set_bg(slide, WHITE)

    if typ == "title":
        set_bg(slide, NAVY)
        add_rect(slide, 0, Inches(6.55), SLIDE_W, Inches(0.95), NAVY_LIGHT)
        add_rect(slide, 0, 0, Inches(0.18), SLIDE_H, ORANGE)
        add_text(slide, Inches(1.0), Inches(2.2), Inches(11.3), Inches(2.0),
                  s["title"], size=40, bold=True, color=WHITE, font=FONT)
        add_text(slide, Inches(1.0), Inches(3.55), Inches(11.0), Inches(1.0),
                  s["subtitle"], size=20, color=RGBColor(0xC9, 0xD3, 0xE6), italic=True)
        add_rect(slide, Inches(1.0), Inches(4.35), Inches(1.6), Pt(3), ORANGE)
        add_text(slide, Inches(1.0), Inches(6.75), Inches(11.3), Inches(0.6),
                  s["footer"], size=15, color=RGBColor(0xC9, 0xD3, 0xE6))
        logo_path = f"{MEDIA}/umaine-logo.png"
        if os.path.isfile(logo_path):
            try:
                logo_h = Inches(0.55)
                with Image.open(logo_path) as _im:
                    logo_ar = _im.size[0] / _im.size[1]
                logo_w = int(logo_h * logo_ar)
                slide.shapes.add_picture(logo_path, SLIDE_W - Inches(0.5) - logo_w, Inches(0.45),
                                          width=logo_w, height=logo_h)
            except Exception:
                pass

    elif typ == "section":
        set_bg(slide, NAVY)
        add_rect(slide, 0, Inches(3.55), SLIDE_W, Pt(3), ORANGE)
        add_text(slide, Inches(1.0), Inches(2.6), Inches(11.0), Inches(0.7),
                  s["title"].upper(), size=20, bold=True, color=ORANGE)
        add_text(slide, Inches(1.0), Inches(3.75), Inches(11.0), Inches(1.3),
                  s["subtitle"], size=40, bold=True, color=WHITE)

    elif typ == "bio":
        add_kicker_title(slide, s["title"], s.get("kicker"))
        try:
            fit_picture(slide, s["img"], Inches(0.6), Inches(1.7), Inches(3.4), Inches(4.6))
        except Exception:
            pass
        add_bullets(slide, Inches(4.35), Inches(1.75), Inches(8.4), Inches(4.9), s["bullets"], size=19, space_after=16)
        add_footer(slide, page, FOOTER_TEXT)

    elif typ == "content":
        add_kicker_title(slide, s["title"], s.get("kicker"))
        add_bullets(slide, Inches(0.65), Inches(1.75), Inches(11.9), Inches(4.9), s["bullets"], size=18, space_after=18)
        add_footer(slide, page, FOOTER_TEXT)

    elif typ == "content_img":
        add_kicker_title(slide, s["title"], s.get("kicker"))
        add_bullets(slide, Inches(0.6), Inches(1.75), Inches(6.15), Inches(4.9), s["bullets"], size=15.5, space_after=13)
        try:
            fit_picture(slide, s["img"], Inches(6.95), Inches(1.75), Inches(5.85), Inches(4.9))
        except Exception:
            pass
        add_footer(slide, page, FOOTER_TEXT)

    elif typ == "image_full":
        add_kicker_title(slide, s["title"], s.get("kicker"))
        try:
            fit_picture(slide, s["img"], Inches(1.4), Inches(1.65), Inches(10.55), Inches(4.55))
        except Exception:
            pass
        add_text(slide, Inches(1.0), Inches(6.3), Inches(11.3), Inches(0.75), s["caption"],
                  size=13.5, italic=True, color=GREY_TXT, align=PP_ALIGN.CENTER)
        add_footer(slide, page, FOOTER_TEXT)

    elif typ == "code":
        add_kicker_title(slide, s["title"], s.get("kicker"))
        y = Inches(1.7)
        has_img = bool(s.get("img"))
        code_w = Inches(7.6) if has_img else Inches(12.15)
        bullets = s.get("bullets") or []
        if bullets:
            add_bullets(slide, Inches(0.6), y, code_w, Inches(1.0), bullets, size=13.5, space_after=6)
            code_y = y + Inches(0.35 * len(bullets) + 0.25)
        else:
            code_y = y
        code_h = SLIDE_H - code_y - Inches(0.85)
        add_code_block(slide, Inches(0.6), code_y, code_w, code_h, s["code"], size=13)
        if s.get("colab_note"):
            note_txt = LINK_RE.sub(r"\1", s["colab_note"])
            add_text(slide, Inches(0.6), code_y + code_h + Inches(0.06), code_w, Inches(0.3),
                      note_txt, size=11, italic=True, color=MUTED)
        if has_img:
            try:
                fit_picture(slide, s["img"], Inches(8.5), y, Inches(4.25), Inches(4.9))
            except Exception:
                pass
        add_footer(slide, page, FOOTER_TEXT)

    elif typ == "gallery":
        add_kicker_title(slide, s["title"], s.get("kicker"))
        imgs = s["images"]
        n = len(imgs)
        gap = Inches(0.3)
        total_w = SLIDE_W - Inches(1.2)
        card_w = int((total_w - gap * (n - 1)) / n)
        x = Inches(0.6)
        y = Inches(1.85)
        card_h = Inches(3.9)
        for path, caption in imgs:
            try:
                fit_picture(slide, path, x, y, card_w, card_h)
            except Exception:
                pass
            add_text(slide, x, y + card_h + Inches(0.1), card_w, Inches(0.8), caption,
                      size=11.5, color=GREY_TXT, align=PP_ALIGN.CENTER)
            x += card_w + gap
        add_footer(slide, page, FOOTER_TEXT)

    elif typ == "demo":
        set_bg(slide, TEAL)
        add_rect(slide, 0, 0, Inches(0.18), SLIDE_H, ORANGE)
        add_text(slide, Inches(0.7), Inches(0.5), Inches(8), Inches(0.35), "LIVE DEMO",
                  size=14, bold=True, color=RGBColor(0xFF, 0xD9, 0xA8))
        add_text(slide, Inches(0.7), Inches(0.85), Inches(11.5), Inches(0.9), s["title"],
                  size=28, bold=True, color=WHITE)
        add_rect(slide, Inches(0.7), Inches(1.65), Inches(1.3), Pt(3), ORANGE)
        has_img = bool(s.get("img"))
        text_w = Inches(7.4) if has_img else Inches(11.5)
        add_bullets(slide, Inches(0.7), Inches(2.1), text_w, Inches(3.2), s["bullets"],
                     size=17, color=WHITE, space_after=14)
        link_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(5.7),
                                           Inches(3.3), Inches(0.6))
        link_box.fill.solid(); link_box.fill.fore_color.rgb = ORANGE
        link_box.line.fill.background(); link_box.shadow.inherit = False
        tf = link_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = "▶  Open in Colab"
        r.font.size = Pt(16); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = FONT
        r.hyperlink.address = s["colab_url"]
        if has_img:
            try:
                fit_picture(slide, s["img"], Inches(8.35), Inches(2.1), Inches(4.35), Inches(4.4))
            except Exception:
                pass

    elif typ == "pillars":
        add_kicker_title(slide, s["title"], s.get("kicker"))
        add_text(slide, Inches(0.6), Inches(1.55), Inches(12.1), Inches(0.8), s["lead"],
                  size=15, italic=True, color=GREY_TXT)
        colors = [BLUE, TEAL, ORANGE]
        n = len(s["pillars"])
        box_w = Inches(3.4)
        gap = Inches(0.5)
        total_w = box_w * n + gap * (n - 1)
        start_x = int((SLIDE_W - total_w) / 2)
        y = Inches(2.7)
        h = Inches(2.6)
        centers = []
        for i, (name, desc) in enumerate(s["pillars"]):
            x = start_x + i * (box_w + gap)
            box = add_rect(slide, x, y, box_w, h, colors[i])
            box.shadow.inherit = False
            tf = box.text_frame
            tf.word_wrap = True
            tf.vertical_anchor = MSO_ANCHOR.TOP
            tf.margin_left = Inches(0.25); tf.margin_right = Inches(0.25)
            tf.margin_top = Inches(0.3)
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run(); r.text = name
            r.font.size = Pt(22); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = FONT
            p2 = tf.add_paragraph()
            p2.alignment = PP_ALIGN.CENTER
            p2.space_before = Pt(14)
            r2 = p2.add_run(); r2.text = desc
            r2.font.size = Pt(14); r2.font.color.rgb = WHITE; r2.font.name = FONT
            centers.append(x + box_w // 2)
        out_y = y + h + Inches(0.45)
        for cx in centers:
            conn = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, cx, y + h, cx, out_y)
            conn.line.color.rgb = NAVY
            conn.line.width = Pt(1.5)
        out_box = add_rect(slide, start_x, out_y, total_w, Inches(0.65), NAVY)
        tf = out_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = s["outcome"]
        r.font.size = Pt(19); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = FONT
        add_footer(slide, page, FOOTER_TEXT)

    elif typ == "triad":
        add_kicker_title(slide, s["title"], s.get("kicker"))
        colors = [RGBColor(0xB5, 0x3A, 0x3A), TEAL, RGBColor(0xB0, 0x7A, 0x1E)]
        n = len(s["items"])
        box_w = Inches(3.75)
        gap = Inches(0.4)
        total_w = box_w * n + gap * (n - 1)
        start_x = int((SLIDE_W - total_w) / 2)
        y = Inches(2.3)
        h = Inches(3.4)
        for i, (name, desc) in enumerate(s["items"]):
            x = start_x + i * (box_w + gap)
            box = add_rect(slide, x, y, box_w, h, LIGHT_BG, line=True)
            box.line.color.rgb = colors[i]
            box.line.width = Pt(2.25)
            top = add_rect(slide, x, y, box_w, Inches(0.15), colors[i])
            tf = box.text_frame
            tf.word_wrap = True
            tf.margin_left = Inches(0.28); tf.margin_right = Inches(0.28); tf.margin_top = Inches(0.4)
            p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
            r = p.add_run(); r.text = name
            r.font.size = Pt(19); r.font.bold = True; r.font.color.rgb = colors[i]; r.font.name = FONT
            p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.CENTER; p2.space_before = Pt(20)
            r2 = p2.add_run(); r2.text = desc
            r2.font.size = Pt(14.5); r2.font.color.rgb = GREY_TXT; r2.font.name = FONT
            if i == 1:
                add_text(slide, x, y + h + Inches(0.1), box_w, Inches(0.4), "✓ the target",
                         size=14, bold=True, color=TEAL, align=PP_ALIGN.CENTER)
        add_footer(slide, page, FOOTER_TEXT)

    elif typ == "pipeline":
        add_kicker_title(slide, s["title"], s.get("kicker"))
        steps = s["steps"]
        n = len(steps)
        y = Inches(2.3)
        h = Inches(3.5)
        gap = Inches(0.35)
        arrow_w = Inches(0.35)
        box_w = int((SLIDE_W - Inches(1.0) - gap * (n - 1) - arrow_w * (n - 1)) / n)
        x = Inches(0.5)
        colors = [NAVY_LIGHT, BLUE, TEAL, ORANGE, RGBColor(0x7A, 0x3E, 0x9E)]
        for i, step in enumerate(steps):
            box = add_rect(slide, x, y, box_w, h, colors[i % len(colors)])
            tf = box.text_frame
            tf.word_wrap = True
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf.margin_left = Inches(0.14); tf.margin_right = Inches(0.14)
            p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
            r = p.add_run(); r.text = str(i + 1)
            r.font.size = Pt(16); r.font.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xC8, 0x7A); r.font.name = FONT
            p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.CENTER; p2.space_before = Pt(8)
            r2 = p2.add_run(); r2.text = step
            r2.font.size = Pt(13); r2.font.bold = True; r2.font.color.rgb = WHITE; r2.font.name = FONT
            x += box_w
            if i < n - 1:
                cy = y + h // 2
                arrow = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x, cy - Inches(0.15), arrow_w, Inches(0.3))
                arrow.fill.solid(); arrow.fill.fore_color.rgb = NAVY
                arrow.line.fill.background()
                x += arrow_w
            x += gap if i < n - 1 else 0
        add_text(slide, Inches(0.5), y + h + Inches(0.35), Inches(12.3), Inches(0.5),
                  s["loop_label"], size=15, italic=True, color=GREY_TXT, align=PP_ALIGN.CENTER)
        add_footer(slide, page, FOOTER_TEXT)

    elif typ == "videos":
        add_kicker_title(slide, s["title"], s.get("kicker"))
        add_bullets(slide, Inches(0.6), Inches(1.55), Inches(12.15), Inches(1.95), s["bullets"], size=14.5, space_after=8)
        vids = s["videos"]
        n = len(vids)
        thumb_w = Inches(3.75)
        thumb_h = Inches(2.11)
        gap = Inches(0.4)
        total_w = thumb_w * n + gap * (n - 1)
        start_x = int((SLIDE_W - total_w) / 2)
        y = Inches(3.75)
        movie_shape_ids = []
        for i, v in enumerate(vids):
            x = start_x + i * (thumb_w + gap)
            movie_shape = slide.shapes.add_movie(
                        v["video"], x, y, thumb_w, thumb_h,
                        poster_frame_image=v["thumb"], mime_type="video/mp4"
                        )
            movie_shape_ids.append(movie_shape.shape_id)
            add_text(slide, x, y + thumb_h + Inches(0.08), thumb_w, Inches(0.5), v["caption"],
                     size=12.5, bold=True, color=NAVY, align=PP_ALIGN.CENTER, line_spacing=1.0)
            src_tb = add_text(slide, x, y + thumb_h + Inches(0.78), thumb_w, Inches(0.3), v["url"],
                               size=9, color=RGBColor(0xAA, 0xAF, 0xB8), align=PP_ALIGN.CENTER)
            for para in src_tb.text_frame.paragraphs:
                for run in para.runs:
                    run.hyperlink.address = v["url"]
        set_media_pause_on_load(slide, movie_shape_ids)
        add_footer(slide, page, FOOTER_TEXT)

    elif typ == "team":
        add_kicker_title(slide, s["title"], s.get("kicker"))
        imgs = s["imgs"]
        n = len(imgs)
        thumb = Inches(2.1)
        gap = Inches(0.35)
        total_w = thumb * n + gap * (n - 1)
        start_x = int((Inches(6.2) - total_w) / 2) + Inches(0.3)
        y = Inches(1.9)
        for i, img in enumerate(imgs):
            try:
                fit_picture(slide, img, start_x + i * (thumb + gap), y, thumb, thumb)
            except Exception:
                pass
        add_bullets(slide, Inches(6.9), Inches(1.9), Inches(5.9), Inches(4.5), s["bullets"], size=16.5, space_after=14)
        add_footer(slide, page, FOOTER_TEXT)

    elif typ == "pubs":
        add_kicker_title(slide, s["title"], s.get("kicker"))
        add_bullets(slide, Inches(0.65), Inches(1.75), Inches(11.9), Inches(4.9), s["pubs"], size=15.5, space_after=15)
        add_footer(slide, page, FOOTER_TEXT)

    elif typ == "end":
        set_bg(slide, NAVY)
        add_rect(slide, 0, 0, Inches(0.18), SLIDE_H, ORANGE)
        add_text(slide, Inches(1.0), Inches(2.7), Inches(11.0), Inches(1.2), s["title"],
                  size=44, bold=True, color=WHITE)
        add_text(slide, Inches(1.0), Inches(3.85), Inches(11.0), Inches(0.7), s["subtitle"],
                  size=22, color=RGBColor(0xC9, 0xD3, 0xE6), italic=True)
        add_rect(slide, Inches(1.0), Inches(4.6), Inches(1.6), Pt(3), ORANGE)
        add_text(slide, Inches(1.0), Inches(5.9), Inches(11.0), Inches(0.6), s["contact"],
                  size=16, color=RGBColor(0xC9, 0xD3, 0xE6))

    else:
        raise ValueError(f"unhandled slide type: {typ}")

    set_notes(slide, s.get("notes", "").strip())

os.makedirs(os.path.dirname(OUT_PPTX), exist_ok=True)
prs.save(OUT_PPTX)
print("Saved", OUT_PPTX, "slides:", len(prs.slides.__iter__.__self__._sldIdLst))
