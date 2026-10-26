"""Build a clean submission ZIP with source, measurements and final documents."""
import argparse
import hashlib
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="output/BTL1_submission.zip")
    args = parser.parse_args()
    files = {}
    for name in ("README.md", "app.py", "start.ps1", "benchmark.py", "wsgi.py", "requirements.txt", "render.yaml", ".gitignore", ".gitattributes"):
        files[name] = ROOT / name
    for name in ("logic_lab", "web", "tests", "docs", "results", "inputs", "tools", ".github"):
        for file in (ROOT / name).rglob("*"):
            if (file.is_file() and not any(part in {"__pycache__", "node_modules"} for part in file.parts)
                    and file.suffix not in {".pyc", ".log"}
                    and not file.name.startswith(".env")):
                files[file.relative_to(ROOT).as_posix()] = file
    for name, source in (("Bao_cao.pdf", "output/pdf/BTL1_Bao_cao.pdf"),
                         ("Slides.pptx", "output/presentation/BTL1_Thuyet_trinh.pptx"),
                         ("Slides.pdf", "output/presentation/BTL1_Thuyet_trinh.pdf")):
        files[name] = ROOT / source
        # Preserve README links as well as the convenient top-level deliverables.
        files[source] = ROOT / source
    missing = [str(file) for file in files.values() if not file.exists()]
    if missing:
        parser.error("Missing deliverables: " + ", ".join(missing))
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest = []
    with ZipFile(output, "w", ZIP_DEFLATED, compresslevel=9) as archive:
        for name, file in sorted(files.items()):
            raw = file.read_bytes()
            archive.writestr("BTL1/" + name, raw)
            manifest.append(hashlib.sha256(raw).hexdigest() + "  " + name)
        archive.writestr("BTL1/MANIFEST.sha256", "\n".join(manifest) + "\n")
    with ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("ZIP CRC verification failed")
    print(f"Saved {output}: {len(files)} files plus manifest; {output.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
