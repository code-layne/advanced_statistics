#!/usr/bin/env python3
"""Wrap a slide PDF into a .pptx — one full-bleed page image per slide.

Used by shared/lesson.mk to produce lessonYY_slides.pptx alongside
lessonYY_slides.pdf, so a deck can be opened, presented, and annotated over in
PowerPoint / Keynote / Google Slides on a classroom machine.

Deliberately dependency-free: it shells out to poppler (pdfinfo, pdftoppm),
which the build already requires, and writes the OOXML package by hand with
zipfile. No LibreOffice, no python-pptx, nothing to install.

The slides are page images, not editable text boxes. That is the point — the
Beamer deck is the source of truth, TikZ figures and math render exactly as
they do in the PDF, and the .pptx is a presentation wrapper. Edit the .tex and
rebuild; never edit the .pptx.

    python3 pdf2pptx.py slides.pdf out.pptx [--dpi 300] [--title "Lesson 1.2"]
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

EMU_PER_PT = 12700  # 1 pt = 12700 English Metric Units
EMU_PER_IN = 914400
DEFAULT_DPI = 300

# Beamer's paper is physically small (aspectratio=169 is 160x90mm = 6.30x3.54in).
# A deck that size presents fine but reads as a non-standard canvas everywhere
# else, so the slide is scaled up — aspect preserved — to PowerPoint's standard
# 7.5in height. That lands 16:9 on exactly 13.333x7.5in and 4:3 on 10x7.5in.
STD_SLIDE_HEIGHT_EMU = round(7.5 * EMU_PER_IN)


def fail(msg: str) -> "NoReturn":  # type: ignore[name-defined]
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def require(tool: str) -> str:
    path = shutil.which(tool)
    if not path:
        fail(f"{tool} not found on PATH — install poppler-utils")
    return path


def page_geometry(pdf: Path) -> tuple[int, float, float]:
    """Return (page count, width in pt, height in pt) from pdfinfo."""
    out = subprocess.run([require("pdfinfo"), str(pdf)], capture_output=True,
                         text=True, check=True).stdout
    pages = re.search(r"^Pages:\s+(\d+)", out, re.M)
    size = re.search(r"^Page size:\s+([\d.]+)\s+x\s+([\d.]+)\s+pts", out, re.M)
    if not pages or not size:
        fail(f"could not read page geometry from {pdf}")
    return int(pages.group(1)), float(size.group(1)), float(size.group(2))


def render_pages(pdf: Path, outdir: Path, dpi: int) -> list[Path]:
    """Rasterize every page to PNG, returned in page order."""
    subprocess.run([require("pdftoppm"), "-png", "-r", str(dpi),
                    str(pdf), str(outdir / "slide")], check=True)
    pngs = sorted(outdir.glob("slide-*.png"),
                  key=lambda p: int(re.search(r"-(\d+)\.png$", p.name).group(1)))
    if not pngs:
        fail(f"pdftoppm produced no pages for {pdf}")
    return pngs


# ── OOXML parts ───────────────────────────────────────────────────────────────
# A minimal but spec-complete presentation: one master, one blank layout, one
# theme, and N slides that each hold a single picture filling the whole slide.

XML_DECL = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
NS_P = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" ' \
       'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" ' \
       'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
RT = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def content_types(n: int) -> str:
    overrides = "".join(
        f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType='
        f'"application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, n + 1))
    return XML_DECL + (
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Default Extension="png" ContentType="image/png"/>'
        '<Override PartName="/ppt/presentation.xml" ContentType='
        '"application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>'
        '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType='
        '"application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>'
        '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType='
        '"application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>'
        '<Override PartName="/ppt/theme/theme1.xml" ContentType='
        '"application/vnd.openxmlformats-officedocument.theme+xml"/>'
        f'{overrides}'
        '<Override PartName="/docProps/core.xml" ContentType='
        '"application/vnd.openxmlformats-package.core-properties+xml"/>'
        '<Override PartName="/docProps/app.xml" ContentType='
        '"application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
        '</Types>')


ROOT_RELS = XML_DECL + (
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    f'<Relationship Id="rId1" Type="{RT}/officeDocument" Target="ppt/presentation.xml"/>'
    f'<Relationship Id="rId2" Type="{RT}/metadata/core-properties" Target="docProps/core.xml"/>'
    f'<Relationship Id="rId3" Type="{RT}/extended-properties" Target="docProps/app.xml"/>'
    '</Relationships>')


def core_props(title: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return XML_DECL + (
        '<cp:coreProperties '
        'xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" '
        'xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        f'<dc:title>{escape(title)}</dc:title>'
        '<cp:revision>1</cp:revision>'
        f'<dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>'
        f'<dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>'
        '</cp:coreProperties>')


def app_props(n: int, title: str) -> str:
    titles = "".join(f"<vt:lpstr>{escape(title)} — {i}</vt:lpstr>" for i in range(1, n + 1))
    return XML_DECL + (
        '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
        'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
        f'<Slides>{n}</Slides><Paragraphs>0</Paragraphs><Words>0</Words>'
        '<Application>apstats build (shared/pdf2pptx.py)</Application>'
        '<PresentationFormat>Custom</PresentationFormat>'
        '<TitlesOfParts>'
        f'<vt:vector size="{n + 1}" baseType="lpstr">'
        '<vt:lpstr>Office Theme</vt:lpstr>'
        f'{titles}'
        '</vt:vector></TitlesOfParts>'
        '</Properties>')


def presentation(n: int, w_emu: int, h_emu: int) -> str:
    # rId1 = master, rId2..rId(n+1) = slides, rId(n+2) = theme
    ids = "".join(f'<p:sldId id="{255 + i}" r:id="rId{i + 1}"/>' for i in range(1, n + 1))
    return XML_DECL + (
        f'<p:presentation {NS_P} saveSubsetFonts="1">'
        '<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>'
        f'<p:sldIdLst>{ids}</p:sldIdLst>'
        f'<p:sldSz cx="{w_emu}" cy="{h_emu}"/>'
        f'<p:notesSz cx="{h_emu}" cy="{w_emu}"/>'
        '</p:presentation>')


def presentation_rels(n: int) -> str:
    rels = [f'<Relationship Id="rId1" Type="{RT}/slideMaster" '
            f'Target="slideMasters/slideMaster1.xml"/>']
    rels += [f'<Relationship Id="rId{i + 1}" Type="{RT}/slide" Target="slides/slide{i}.xml"/>'
             for i in range(1, n + 1)]
    rels.append(f'<Relationship Id="rId{n + 2}" Type="{RT}/theme" Target="theme/theme1.xml"/>')
    return XML_DECL + ('<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                       + "".join(rels) + '</Relationships>')


EMPTY_SPTREE = (
    '<p:spTree>'
    '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
    '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
    '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
    '</p:spTree>')

CLR_MAP = ('<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" '
           'accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" '
           'accent6="accent6" hlink="hlink" folHlink="folHlink"/>')

SLIDE_MASTER = XML_DECL + (
    f'<p:sldMaster {NS_P}>'
    f'<p:cSld>{EMPTY_SPTREE}</p:cSld>'
    f'{CLR_MAP}'
    '<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>'
    '</p:sldMaster>')

SLIDE_MASTER_RELS = XML_DECL + (
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    f'<Relationship Id="rId1" Type="{RT}/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
    f'<Relationship Id="rId2" Type="{RT}/theme" Target="../theme/theme1.xml"/>'
    '</Relationships>')

SLIDE_LAYOUT = XML_DECL + (
    f'<p:sldLayout {NS_P} type="blank" preserve="1">'
    f'<p:cSld name="Blank">{EMPTY_SPTREE}</p:cSld>'
    '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>'
    '</p:sldLayout>')

SLIDE_LAYOUT_RELS = XML_DECL + (
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    f'<Relationship Id="rId1" Type="{RT}/slideMaster" Target="../slideMasters/slideMaster1.xml"/>'
    '</Relationships>')


def slide(index: int, w_emu: int, h_emu: int) -> str:
    """One slide: a single picture anchored at the origin, filling the slide."""
    return XML_DECL + (
        f'<p:sld {NS_P}>'
        '<p:cSld><p:spTree>'
        '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
        '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
        '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
        '<p:pic>'
        '<p:nvPicPr>'
        f'<p:cNvPr id="2" name="Slide {index}" descr="Page {index} of the lesson slide deck"/>'
        '<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr>'
        '<p:nvPr/>'
        '</p:nvPicPr>'
        # rId2 is the image; rId1 is the layout (see slide_rels).
        '<p:blipFill><a:blip r:embed="rId2"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
        '<p:spPr>'
        f'<a:xfrm><a:off x="0" y="0"/><a:ext cx="{w_emu}" cy="{h_emu}"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        '</p:spPr>'
        '</p:pic>'
        '</p:spTree></p:cSld>'
        '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>'
        '</p:sld>')


def slide_rels(index: int) -> str:
    return XML_DECL + (
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f'<Relationship Id="rId1" Type="{RT}/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
        f'<Relationship Id="rId2" Type="{RT}/image" Target="../media/image{index}.png"/>'
        '</Relationships>')


def _fill_styles() -> str:
    solid = '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
    return (f'<a:fillStyleLst>{solid}{solid}{solid}</a:fillStyleLst>'
            '<a:lnStyleLst>'
            + ('<a:ln w="9525" cap="flat" cmpd="sng" algn="ctr">'
               '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
               '<a:prstDash val="solid"/></a:ln>') * 3 +
            '</a:lnStyleLst>'
            '<a:effectStyleLst>'
            + '<a:effectStyle><a:effectLst/></a:effectStyle>' * 3 +
            '</a:effectStyleLst>'
            f'<a:bgFillStyleLst>{solid}{solid}{solid}</a:bgFillStyleLst>')


THEME = XML_DECL + (
    '<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Office Theme">'
    '<a:themeElements>'
    '<a:clrScheme name="Office">'
    '<a:dk1><a:sysClr val="windowText" lastClr="000000"/></a:dk1>'
    '<a:lt1><a:sysClr val="window" lastClr="FFFFFF"/></a:lt1>'
    '<a:dk2><a:srgbClr val="44546A"/></a:dk2>'
    '<a:lt2><a:srgbClr val="E7E6E6"/></a:lt2>'
    '<a:accent1><a:srgbClr val="4472C4"/></a:accent1>'
    '<a:accent2><a:srgbClr val="ED7D31"/></a:accent2>'
    '<a:accent3><a:srgbClr val="A5A5A5"/></a:accent3>'
    '<a:accent4><a:srgbClr val="FFC000"/></a:accent4>'
    '<a:accent5><a:srgbClr val="5B9BD5"/></a:accent5>'
    '<a:accent6><a:srgbClr val="70AD47"/></a:accent6>'
    '<a:hlink><a:srgbClr val="0563C1"/></a:hlink>'
    '<a:folHlink><a:srgbClr val="954F72"/></a:folHlink>'
    '</a:clrScheme>'
    '<a:fontScheme name="Office">'
    '<a:majorFont><a:latin typeface="Calibri Light"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont>'
    '<a:minorFont><a:latin typeface="Calibri"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont>'
    '</a:fontScheme>'
    f'<a:fmtScheme name="Office">{_fill_styles()}</a:fmtScheme>'
    '</a:themeElements>'
    '<a:objectDefaults/><a:extraClrSchemeLst/>'
    '</a:theme>')


def build_pptx(pdf: Path, out: Path, dpi: int, title: str, normalize: bool = True) -> int:
    n_pages, w_pt, h_pt = page_geometry(pdf)
    if normalize:
        h_emu = STD_SLIDE_HEIGHT_EMU
        w_emu = round(STD_SLIDE_HEIGHT_EMU * w_pt / h_pt)
    else:
        w_emu = round(w_pt * EMU_PER_PT)
        h_emu = round(h_pt * EMU_PER_PT)

    with tempfile.TemporaryDirectory() as tmp:
        pngs = render_pages(pdf, Path(tmp), dpi)
        if len(pngs) != n_pages:
            fail(f"pdftoppm rendered {len(pngs)} images for a {n_pages}-page PDF")

        out.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", content_types(n_pages))
            z.writestr("_rels/.rels", ROOT_RELS)
            z.writestr("docProps/core.xml", core_props(title))
            z.writestr("docProps/app.xml", app_props(n_pages, title))
            z.writestr("ppt/presentation.xml", presentation(n_pages, w_emu, h_emu))
            z.writestr("ppt/_rels/presentation.xml.rels", presentation_rels(n_pages))
            z.writestr("ppt/theme/theme1.xml", THEME)
            z.writestr("ppt/slideMasters/slideMaster1.xml", SLIDE_MASTER)
            z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", SLIDE_MASTER_RELS)
            z.writestr("ppt/slideLayouts/slideLayout1.xml", SLIDE_LAYOUT)
            z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", SLIDE_LAYOUT_RELS)
            for i, png in enumerate(pngs, start=1):
                z.writestr(f"ppt/slides/slide{i}.xml", slide(i, w_emu, h_emu))
                z.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", slide_rels(i))
                # PNGs are already deflate-compressed; store them to save time.
                z.write(png, f"ppt/media/image{i}.png", compress_type=zipfile.ZIP_STORED)
    return n_pages


def main() -> None:
    p = argparse.ArgumentParser(description="Wrap a slide PDF into a .pptx (one page image per slide).")
    p.add_argument("pdf", type=Path, help="input slide PDF")
    p.add_argument("pptx", type=Path, help="output .pptx")
    p.add_argument("--dpi", type=int, default=DEFAULT_DPI,
                   help=f"rasterization resolution (default {DEFAULT_DPI})")
    p.add_argument("--title", default="", help="deck title for the file properties")
    p.add_argument("--raw-size", action="store_true",
                   help="keep the PDF's physical page size instead of scaling to a 7.5in-tall slide")
    args = p.parse_args()

    if not args.pdf.is_file():
        fail(f"{args.pdf} not found")
    title = args.title or args.pdf.stem
    n = build_pptx(args.pdf, args.pptx, args.dpi, title, normalize=not args.raw_size)
    print(f"  {args.pptx}  ({n} slides @ {args.dpi} dpi)")


if __name__ == "__main__":
    main()
