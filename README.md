# WhereDidItGo

Find a file by what was inside it, not by its name. Everything runs on your computer: no cloud, no account, no AI service.

لاقي الملف بمحتواه مش باسمه. كل حاجة بتشتغل على جهازك.

## Worked example

Folder: [`demo/files/`](demo/files) (a PDF named `doc_0417.pdf`, a photo `IMG_2231.png` of an SVM formula, a scanned bill `scan.pdf`, an Excel sheet `Book1.xlsx`, a Word file, a PowerPoint, an Arabic note). Real output, see [`demo/demo-output.txt`](demo/demo-output.txt):

```
$ wheredidit add demo/files
indexed 7, unchanged 0, failed 0, removed 0

$ wheredidit find "the file that had a comparison of internet company prices"
1. doc_0417.pdf   (modified 2026-11-25)
   Why: matched 2 of 4 words (comparison, internet) in page 1
   "Broadband provider comparison for the office Provider A: 200 GB at 450 EGP per month ..."

$ wheredidit find "the picture of the whiteboard with the SVM formula"
1. IMG_2231.png
   Why: matched 1 of 3 words (svm) in image text (OCR)

$ wheredidit find "عايز الملف بتاع زيادة سعر الاشتراك"
1. ملاحظات.md
   Why: matched 3 of 4 words (زياده, سعر, اشتراك) in part 1
```

The PDF was found although its name says nothing: "internet" matched "Broadband" through a small synonym list.

## Install and use

```
git clone https://github.com/mohamed-elshamy-ai/wheredidit && cd wheredidit
pip install .
wheredidit add ~/Documents          # index a folder (re-run to pick up changes)
wheredidit find "invoice from the electricity company last month"
wheredidit watch                    # keep the index up to date every 30 seconds
```

| System | Status |
|---|---|
| Linux | Tested (Python 3.10). |
| Windows / macOS | Should work, not tested. Use `py -m pip install .` on Windows. |
| Android / browser | Not available: it needs to read your folders. |
| OCR (photos, scanned PDFs) | Needs the free `tesseract` program installed (`sudo apt install tesseract-ocr tesseract-ocr-ara`). Without it, images and scanned pages are skipped, and the tool says nothing about them. Arabic OCR needs the `ara` language data. |

Date words work in the question: `last week`, `yesterday`, `last month`, `امبارح`, `الشهر اللي فات` filter by the file's modified date.

## What it does NOT do (honest)

- It matches words and word forms plus a small hand-made synonym list (about 23 groups, English and Arabic). It does **not** understand meaning. There are no embeddings. "SVM" does not find a file that only says "support vector machine" (the test files show this on purpose).
- Your answer must share words with the file. "The file with the thing about the lecture" will not work.
- OCR quality depends on the image. Handwriting is poor.
- Audio is not supported. There is no window app yet, only the command line.
- Files are re-read when size or modified time changes. `watch` polls; it does not use operating system events.

## Technical notes

[ARCHITECTURE.md](ARCHITECTURE.md), in Arabic and English. Tests: 9 pytest tests (`pytest`), including OCR of an image and a scanned PDF.

## How it works (بالعربي)

بتختار الفولدرات، والأداة بتقرا محتوى كل ملف (PDF وWord وExcel وPowerPoint وصور وPDF متصور بالـ OCR) وتقسمه لأجزاء صغيرة وتخزنها في قاعدة بيانات SQLite على جهازك. لما تسأل بجملة عادية، بتشيل الكلمات الزيادة، وتجيب أصل الكلمات (زيادة/زاد/ارتفع)، وتدور على أقرب الأجزاء وتوريك سبب الاختيار والصفحة اللي فيها الكلام. مفيش نموذج ذكاء اصطناعي: مطابقة كلمات ومرادفات صغيرة، فلازم وصفك يشارك الملف في كلمات.

MIT License.
