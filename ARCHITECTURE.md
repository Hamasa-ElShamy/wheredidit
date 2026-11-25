# WhereDidItGo: technical notes / الشرح التقني

## English
**Modules**
- `extract.py`: file to passages `(location, text)`. PDF (PyMuPDF; a page with almost no text is rendered to an image and sent to OCR), Word, Excel (one passage per row), PowerPoint (slides and notes), text/CSV/Markdown, images (OCR). OCR calls the `tesseract` program with `ara+eng` if installed.
- `text.py`: normalisation shared by indexing and queries: stop words, light English stemming, Arabic normalisation (alef and ta marbuta forms, `ال`, plural endings), Arabic digits, and a synonym table that maps each word to the head of its group.
- `when.py`: date phrases to a modified-date range.
- `index.py`: SQLite. Tables `files`, `roots`, `passages` plus a contentless FTS5 table over the normalised text. Ranking: FTS5 `bm25` plus word coverage (share of query words in the passage) plus a bonus for a file-name match; one best passage per file. Passages with fewer than 2 matching words are dropped for queries with 3 or more words.
- `cli.py`: `add`, `update`, `find`, `status`, `watch`.

**Design decisions**: the same normalisation on both sides, so a spelling variant never decides the result; "why" text is built from the matched words and location, never from a model; changed files are found by size and modified time; unreadable files are recorded with their error instead of silently skipped.

**Testing**: 9 tests on generated sample files: filename-independent PDF match, Excel, Arabic, OCR of an image and of a scanned PDF, PowerPoint and Word, no-match, update after add/delete/corrupt file, date phrases.

**Limits**: no semantic search (no embeddings), small synonym list, OCR only if tesseract is installed, polling `watch`.

## بالعربي
**الأجزاء**: `extract.py` بيقرا الملفات (وبيعمل OCR للصور وصفحات PDF المصورة لو tesseract متسطب). `text.py` بيوحد الكلام: بيشيل الكلمات الزيادة وبيرجع الكلمة لأصلها بالإنجليزي والعربي وفيه جدول مرادفات صغير. `when.py` بيفهم "الأسبوع اللي فات" و"امبارح". `index.py` قاعدة SQLite مع بحث FTS5 وترتيب بـ bm25 وتغطية كلمات السؤال وبونص لاسم الملف. `cli.py` الأوامر.
**قرارات التصميم**: نفس المعالجة للسؤال والفهرس، وسبب الاختيار مبني على الكلمات المتطابقة مش على نموذج، والملفات اللي مش بتتقرا بتتسجل بخطئها.
**الحدود**: مفيش بحث بالمعنى (مفيش embeddings)، المرادفات قليلة ومكتوبة يدوي، والـ OCR محتاج tesseract.
