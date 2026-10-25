"""Assemble reviewed slide PNGs into a PDF when native PDF export is unavailable.

This PDF contains rendered slides; edit the native PowerPoint for content edits.
Optional dependency: ReportLab. PNGs are produced by build_slides.mjs.
"""
import argparse
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", default="tmp/slides")
    args = parser.parse_args()
    slides = sorted((ROOT / args.input_dir).glob("slide-*.png"))
    if len(slides) != 12:
        raise ValueError("Expected 12 rendered slide PNGs. Run build_slides.mjs first.")
    target = ROOT / "output/presentation/BTL1_Thuyet_trinh.pdf"
    target.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(target), pagesize=(960, 540), pageCompression=1)
    pdf.setTitle("BTL1 - Pipes & Light Up - DFS & Greedy")
    pdf.setAuthor("Mạch - Logic Lab")
    for index, slide in enumerate(slides, 1):
        pdf.bookmarkPage(f"slide-{index}")
        pdf.addOutlineEntry(f"Slide {index}", f"slide-{index}")
        pdf.drawImage(ImageReader(str(slide)), 0, 0, width=960, height=540)
        pdf.showPage()
    pdf.save()
    print(f"Saved {target}")


if __name__ == "__main__":
    main()
