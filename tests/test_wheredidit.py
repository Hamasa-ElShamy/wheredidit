import os, shutil, subprocess, time
from pathlib import Path
import pytest
from wheredidit.index import Index
from wheredidit import text, when, extract

FILES = Path(__file__).resolve().parent.parent / "demo" / "files"


@pytest.fixture()
def ix(tmp_path):
    d = tmp_path / "f"; shutil.copytree(FILES, d)
    i = Index(str(tmp_path / "t.db")); i.add_folder(d); i.d = d
    return i


def names(res): return [Path(r["path"]).name for r in res]


def test_stem_synonym_arabic():
    assert text.stem("growing") == text.stem("rose") == "increase"
    assert text.stem("الإيرادات") == text.stem("مبيعات")
    assert text.tokens("١٢٣ prices") == ["123", text.stem("prices")]


def test_content_not_filename(ix):
    assert names(ix.search("comparison of internet company prices"))[0] == "doc_0417.pdf"


def test_excel_and_arabic(ix):
    assert names(ix.search("table of student grades"))[0] == "Book1.xlsx"
    assert names(ix.search("زيادة سعر الاشتراك"))[0] == "ملاحظات.md"


def test_ocr_image_and_scanned_pdf(ix):
    if not shutil.which("tesseract"):
        pytest.skip("tesseract not installed")
    assert names(ix.search("whiteboard SVM margin"))[0] == "IMG_2231.png"
    assert names(ix.search("electricity bill total"))[0] == "scan.pdf"
    assert "(OCR)" in ix.search("electricity bill")[0]["loc"]


def test_pptx_and_docx(ix):
    assert names(ix.search("sales grew while costs fell"))[0] == "deck_final_v3.pptx"
    assert names(ix.search("hyperplane widest margin"))[0] == "ML_Notes.docx"


def test_reason_explains(ix):
    r = ix.search("internet prices comparison")[0]
    assert "matched" in r["reason"] and "page 1" in r["reason"]


def test_no_match_is_empty(ix):
    assert ix.search("quantum chromodynamics lagrangian") == []


def test_update_detects_change_and_delete(ix):
    (ix.d / "new.txt").write_text("The warranty certificate for the refrigerator expires in June.")
    assert ix.update()["indexed"] == 1
    assert names(ix.search("refrigerator warranty"))[0] == "new.txt"
    (ix.d / "new.txt").unlink()
    assert ix.update()["removed"] == 1
    assert ix.search("refrigerator warranty") == []
    (ix.d / "ML_Notes.docx").write_bytes(b"corrupt")
    assert ix.update()["error"] == 1 and ix.stats()["errors"]


def test_date_phrases(ix):
    now = time.time()
    assert when.parse("last week bills", now)[0] is not None
    assert when.parse("امبارح الفاتورة", now)[0] is not None
    old = ix.d / "scan.pdf"; os.utime(old, (now - 40 * 86400,) * 2)
    assert "scan.pdf" not in names(ix.search("electricity bill last week", now=now))
    assert "scan.pdf" in names(ix.search("electricity bill", now=now))


def test_html_indexed_and_bad_files_explained(tmp_path):
    from wheredidit.index import Index
    (tmp_path / "f.html").write_text("<html><body><script>var x=1</script><p>Pizza size small medium large</p></body></html>")
    (tmp_path / "e.docx").write_bytes(b"")
    (tmp_path / "x.bin").write_bytes(b"abc")
    ix = Index(str(tmp_path / "i.db"))
    r = ix.add_folder(tmp_path)
    assert r["indexed"] == 1 and r["error"] == 1 and ix.skipped == {".bin": 1}
    assert ix.search("pizza size")[0]["path"].endswith("f.html")
    assert "empty" in ix.stats()["errors"][0][1]
