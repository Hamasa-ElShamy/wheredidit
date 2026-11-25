"""Text normalisation shared by the indexer and the query: no model, plain rules."""
import re

STOP = set("""a an the of to in on at for and or but is are was were be been it its this that these those with as by from has have had do
does did not no will would can could should may might than then so into over under about after before which who what when where while
also their there they them his her he she we you i our your my file files document documents pdf image picture photo one
هاتلي هات لي الملف اللي كان فيه فيها كانت كنت عايز عاوز ملف ملفات الصورة صورة اللى في من على عن مع ده دي دا هو هي""".split())

SYN_GROUPS = [
    "increase grow rise rose grew gain growth", "decrease fall drop decline fell shrink reduce cut",
    "revenue sales turnover income", "cost expense spending expenditure", "customer client user buyer",
    "employee staff worker headcount", "profit earnings margin", "price pricing rate tariff fee",
    "internet broadband wifi isp", "invoice bill receipt", "contract agreement deal",
    "grade mark score result", "student pupil learner",
    "زيادة ارتفاع نمو زاد ارتفع", "انخفاض نقص تراجع هبوط", "ايرادات مبيعات دخل", "تكلفة مصروفات نفقات", "سعر اسعار تسعيرة",
    "عملاء زبائن", "فاتورة ايصال", "عقد اتفاقية", "درجات نتيجة علامات", "طلاب طلبة",
]
SYN = {}


def norm_ar(w):
    if not re.search(r"[\u0600-\u06FF]", w):
        return w
    w = re.sub("[\u064B-\u0652\u0640]", "", w)
    w = w.translate(str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ى": "ي", "ة": "ه"}))
    for pre in ("وال", "بال", "كال", "فال", "لل", "ال"):
        if w.startswith(pre) and len(w) - len(pre) >= 3:
            w = w[len(pre):]
            break
    for suf in ("ات", "ون", "ين", "ان"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            w = w[: -len(suf)]
            break
    return w


def stem(w):
    w = norm_ar(w)
    if re.search(r"[\u0600-\u06FF]", w):
        return SYN.get(w, w)
    if w in SYN:
        return SYN[w]
    cands = []
    for suf in ("ations", "ation", "ings", "ing", "edly", "ied", "ies", "ed", "es", "ly", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3 and not (suf == "s" and w.endswith("ss")):
            cands.append(w[: -len(suf)] + ("y" if suf in ("ied", "ies") else ""))
    for c in cands + [c + "e" for c in cands]:
        if c in SYN:
            return SYN[c]
    return cands[0] if cands else w


for _g in SYN_GROUPS:
    _ws = _g.split()
    for _w in _ws:
        SYN[norm_ar(_w)] = norm_ar(_ws[0])
        SYN[_w] = norm_ar(_ws[0])

_TOK = re.compile(r"[^\W_]{2,}", re.UNICODE)
AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def tokens(text, keep_stop=False):
    text = text.translate(AR_DIGITS).lower()
    out = []
    for w in _TOK.findall(text):
        if not keep_stop and w in STOP:
            continue
        out.append(stem(w))
    return out


def index_text(text):
    """What goes into the search index: stemmed tokens joined by spaces."""
    return " ".join(tokens(text, keep_stop=True))
