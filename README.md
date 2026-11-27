# WhereDidItGo

[![tests](https://github.com/mohamed-elshamy-ai/wheredidit/actions/workflows/tests.yml/badge.svg)](https://github.com/mohamed-elshamy-ai/wheredidit/actions/workflows/tests.yml) ![tests: 10 passing](https://img.shields.io/badge/tests-10%20passing-brightgreen) ![license: MIT](https://img.shields.io/badge/license-MIT-blue)

Find a file by what was inside it, not by its name. Everything runs on your computer: no cloud, no account, no AI service.

PDF reading uses [pypdfium2](https://github.com/pypdfium2-team/pypdfium2) (Apache-2.0 / BSD, PDFium). No AGPL code is installed.

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

The last query is Arabic for "the file about the subscription price increase"; it finds `ملاحظات.md` ("notes.md") by content.

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

Date words work in the question: `last week`, `yesterday`, `last month`, `امبارح` (yesterday), `الشهر اللي فات` (last month) filter by the file's modified date.

## Limitations

- It matches words and word forms plus a small hand-made synonym list (23 groups, English and Arabic). It does **not** understand meaning. There are no embeddings. "SVM" does not find a file that only says "support vector machine" (the test files show this on purpose).
- Your answer must share words with the file. "The file with the thing about the lecture" will not work.
- OCR quality depends on the image. Handwriting is poor.
- Audio is not supported. There is no window app yet, only the command line.
- Files are re-read when size or modified time changes. `watch` polls; it does not use operating system events.

## Related tools

Desktop search tools exist: [DocFetcher](https://docfetcher.sourceforge.io/) and [Recoll](https://www.recoll.org/) search file contents, and AI file finders such as [semsearch](https://github.com/a303990366/semsearch) search by describing the file using embeddings. Those can understand meaning; WhereDidItGo cannot. Its differences are a small install with no model download, Arabic and Egyptian-dialect handling, date phrases, and a plain 'why this matched' line.

## Technical notes

[ARCHITECTURE.md](ARCHITECTURE.md), in Arabic and English. Tests: 9 pytest tests (`pytest`), including OCR of an image and a scanned PDF.

## How it works

You choose the folders. WhereDidItGo reads the content of each file (PDF, Word, Excel, PowerPoint, images, and scanned PDFs through OCR), splits it into small passages and stores them in a SQLite database on your computer. When you ask in a plain sentence, it removes filler words, reduces words to their stems (for example the Arabic variants of "increase"), finds the closest passages, and shows why each one was chosen and which page holds the text. There is no AI model: it is word matching plus a small synonym list, so your description has to share some words with the file.
