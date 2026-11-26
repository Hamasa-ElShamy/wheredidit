"""Turn a file into passages: (location, text). Scanned pages and images go through the tesseract program if it is installed."""
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

SUPPORTED = {".pdf", ".docx", ".xlsx", ".pptx", ".txt", ".md", ".csv",
             ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}
IMAGES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}
_SPLIT = re.compile(r"(?<=[.!?؟])\s+|\n+")


def _chunks(text, size=400):
    """Sentences grouped to about `size` characters so a match has context."""
    parts = [s.strip() for s in _SPLIT.split(text) if s.strip()]
    out, cur = [], ""
    for p in parts:
        if cur and len(cur) + len(p) > size:
            out.append(cur)
            cur = p
        else:
            cur = (cur + " " + p).strip()
    if cur:
        out.append(cur)
    return [c for c in out if len(c) > 3]


def ocr_langs():
    if not shutil.which("tesseract"):
        return None
    try:
        out = subprocess.run(["tesseract", "--list-langs"], capture_output=True, text=True, timeout=20).stdout.split()
    except Exception:
        return None
    langs = [l for l in ("ara", "eng") if l in out]
    return "+".join(langs) if langs else None


def ocr_image(path):
    lang = ocr_langs()
    if not lang:
        return ""
    try:
        r = subprocess.run(["tesseract", str(path), "stdout", "-l", lang], capture_output=True, text=True, timeout=120)
        return r.stdout
    except Exception:
        return ""


def extract(path):
    p = Path(path)
    ext = p.suffix.lower()
    out = []
    if ext in (".txt", ".md", ".csv"):
        for i, chunk in enumerate(_chunks(p.read_text(encoding="utf-8", errors="replace")), 1):
            out.append((f"part {i}", chunk))
    elif ext == ".docx":
        import docx
        d = docx.Document(str(p))
        text = "\n".join(x.text for x in d.paragraphs)
        for i, c in enumerate(_chunks(text), 1):
            out.append((f"section {i}", c))
        for ti, t in enumerate(d.tables, 1):
            for ri, row in enumerate(t.rows, 1):
                cells = [c.text.strip() for c in row.cells]
                if any(cells):
                    out.append((f"table {ti} row {ri}", " | ".join(cells)))
    elif ext == ".pptx":
        from pptx import Presentation
        for n, s in enumerate(Presentation(str(p)).slides, 1):
            texts = [sh.text_frame.text for sh in s.shapes if sh.has_text_frame]
            if s.has_notes_slide:
                texts.append(s.notes_slide.notes_text_frame.text)
            for c in _chunks("\n".join(texts)):
                out.append((f"slide {n}", c))
    elif ext == ".xlsx":
        import openpyxl
        wb = openpyxl.load_workbook(str(p), data_only=True, read_only=True)
        for ws in wb.worksheets:
            for ri, row in enumerate(ws.iter_rows(values_only=True), 1):
                cells = [str(c) for c in row if c is not None]
                if cells:
                    out.append((f"sheet {ws.title} row {ri}", " | ".join(cells)))
    elif ext == ".pdf":
        import pypdfium2 as pdfium
        doc = pdfium.PdfDocument(str(p))
        try:
            for n in range(len(doc)):
                page = doc[n]
                tp = page.get_textpage()
                text = tp.get_text_range()
                tp.close()
                if len(text.strip()) < 20 and ocr_langs():  # looks scanned
                    with tempfile.TemporaryDirectory() as td:
                        img = Path(td) / "p.png"
                        page.render(scale=200 / 72).to_pil().save(str(img))  # 200 dpi
                        text = ocr_image(img)
                    where = f"page {n + 1} (OCR)"
                else:
                    where = f"page {n + 1}"
                for c in _chunks(text):
                    out.append((where, c))
                page.close()
        finally:
            doc.close()
    elif ext in IMAGES:
        text = ocr_image(p)
        for c in _chunks(text):
            out.append(("image text (OCR)", c))
    else:
        raise ValueError(f"unsupported type {ext}")
    return out
