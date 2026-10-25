"""Export the repository report and current benchmark appendix to a Unicode PDF.

Optional authoring dependency: reportlab. The application itself needs none.
Pass --font-dir containing arial.ttf/arialbd.ttf/ariali.ttf, or DejaVu Sans.
"""
import argparse
import html
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak


ROOT = Path(__file__).resolve().parents[1]


def register_fonts(font_dir=None):
    directories = [Path(font_dir)] if font_dir else [Path("C:/Windows/Fonts"), Path("/usr/share/fonts/truetype/dejavu")]
    for directory in directories:
        for filenames in (("arial.ttf", "arialbd.ttf", "ariali.ttf"),
                          ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans-Oblique.ttf")):
            files = [directory / name for name in filenames]
            if all(file.exists() for file in files):
                for name, file in zip(("Body", "Body-Bold", "Body-Italic"), files):
                    pdfmetrics.registerFont(TTFont(name, str(file)))
                pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-Bold", italic="Body-Italic", boldItalic="Body-Bold")
                return
    raise ValueError("Unicode fonts not found. Pass --font-dir with Arial or DejaVu Sans fonts.")


def inline(text):
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r'<font color="#244e42">\1</font>', text)
    text = re.sub(r"(https?://[^\s<]+)", r'<link href="\1" color="#244e42">\1</link>', text)
    return text


def markdown_flow(text, styles, width):
    result, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("```"):
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(html.escape(lines[i]).replace(" ", "&#160;"))
                i += 1
            result.append(Paragraph("<br/>".join(code), styles["code"]))
            i += 1
            continue
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [value.strip() for value in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", value) for value in cells):
                    rows.append([Paragraph(inline(c), styles["table"]) for c in cells])
                i += 1
            columns = len(rows[0])
            widths = [width * .26] + [width * .74 / (columns - 1)] * (columns - 1) if columns == 7 else [width * .31, width * .69]
            table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5eddc")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f8f2")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LINEBELOW", (0, 0), (-1, 0), .7, colors.HexColor("#92a67e")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ]))
            result.extend([table, Spacer(1, 12)])
            continue
        heading = re.match(r"^(#{1,3})\s+(.+)$", line)
        if heading:
            result.append(Paragraph(inline(heading[2]), styles[f"h{len(heading[1])}"]))
            i += 1
            continue
        paragraph = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#|\||```)", lines[i]):
            paragraph.append(lines[i].strip())
            i += 1
        result.append(Paragraph(inline(" ".join(paragraph)), styles["body"]))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font-dir")
    parser.add_argument("--output", default="output/pdf/BTL1_Bao_cao.pdf")
    args = parser.parse_args()
    register_fonts(args.font_dir)
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    ink = colors.HexColor("#203d35")
    base = dict(fontName="Body", textColor=ink, alignment=TA_LEFT, splitLongWords=1)
    styles = {
        "body": ParagraphStyle("Body", fontSize=10.2, leading=16, spaceAfter=9, **base),
        "h1": ParagraphStyle("Title", fontSize=28, leading=34, spaceAfter=18, keepWithNext=True, **base),
        "h2": ParagraphStyle("Heading", fontSize=16, leading=22, spaceBefore=18, spaceAfter=10, keepWithNext=True, **base),
        "h3": ParagraphStyle("Subheading", fontSize=12.2, leading=18, spaceBefore=12, spaceAfter=7, keepWithNext=True, **base),
        "table": ParagraphStyle("Table", fontSize=8.4, leading=12, **base),
        "code": ParagraphStyle("Code", fontSize=8.3, leading=13, spaceBefore=6, spaceAfter=12,
                               backColor=colors.HexColor("#f0f3e9"), borderPadding=9, **base),
    }
    for key in ("h1", "h2", "h3"):
        styles[key].fontName = "Body-Bold"
    doc = SimpleDocTemplate(str(output), pagesize=A4, leftMargin=48, rightMargin=48,
                            topMargin=52, bottomMargin=48, title="BTL1 - Mạch Logic Lab",
                            author="Mạch - Logic Lab", pageCompression=1)
    story = markdown_flow((ROOT / "docs/REPORT.md").read_text(encoding="utf-8"), styles, doc.width)
    story.append(PageBreak())
    story.extend(markdown_flow((ROOT / "docs/BENCHMARK.md").read_text(encoding="utf-8"), styles, doc.width))

    def page_chrome(canvas, _doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#dce4d3"))
        canvas.line(48, A4[1] - 32, A4[0] - 48, A4[1] - 32)
        canvas.setFont("Body", 8)
        canvas.setFillColor(colors.HexColor("#61745d"))
        canvas.drawString(48, A4[1] - 24, "MẠCH / LOGIC LAB")
        canvas.drawRightString(A4[0] - 48, A4[1] - 24, "BTL1 - TÌM KIẾM")
        canvas.drawString(48, 27, "Pipes & Light Up | DFS & Greedy")
        canvas.drawRightString(A4[0] - 48, 27, str(canvas.getPageNumber()))
        canvas.restoreState()

    doc.build(story, onFirstPage=page_chrome, onLaterPages=page_chrome)
    print(f"Saved {output}")


if __name__ == "__main__":
    main()
