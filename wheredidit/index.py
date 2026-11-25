"""Local SQLite index (FTS5). Nothing leaves the machine."""
import os
import sqlite3
import time
from pathlib import Path

from .extract import SUPPORTED, extract
from .text import index_text, tokens
from . import when


def default_db():
    return os.environ.get("WHEREDIDITGO_DB", str(Path.home() / ".wheredidit.db"))


class Index:
    def __init__(self, path=None):
        self.db = sqlite3.connect(path or default_db())
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS files(path TEXT PRIMARY KEY, mtime REAL, size INTEGER, indexed_at REAL, error TEXT);
        CREATE TABLE IF NOT EXISTS roots(path TEXT PRIMARY KEY);
        CREATE TABLE IF NOT EXISTS passages(id INTEGER PRIMARY KEY, path TEXT, loc TEXT, text TEXT);
        CREATE VIRTUAL TABLE IF NOT EXISTS fts USING fts5(norm, content='');
        CREATE INDEX IF NOT EXISTS pass_path ON passages(path);
        """)

    # ---- indexing ----
    def add_file(self, path, force=False):
        p = Path(path).resolve()
        st = p.stat()
        row = self.db.execute("SELECT mtime,size FROM files WHERE path=?", (str(p),)).fetchone()
        if row and not force and row[0] == st.st_mtime and row[1] == st.st_size:
            return "unchanged"
        self._reset(str(p))
        err = None
        try:
            passages = extract(p)
        except Exception as e:
            passages, err = [], f"{type(e).__name__}: {e}"
        # file name is searchable too
        passages = [("file name", p.stem.replace("_", " ").replace("-", " "))] + passages
        for loc, text in passages:
            cur = self.db.execute("INSERT INTO passages(path,loc,text) VALUES (?,?,?)", (str(p), loc, text))
            self.db.execute("INSERT INTO fts(rowid, norm) VALUES (?,?)", (cur.lastrowid, index_text(text)))
        self.db.execute("INSERT OR REPLACE INTO files VALUES (?,?,?,?,?)", (str(p), st.st_mtime, st.st_size, time.time(), err))
        self.db.commit()
        return "error" if err else "indexed"

    def _reset(self, path):
        # contentless FTS tables need the old text to delete; rebuild from passages table
        for i, text in self.db.execute("SELECT id,text FROM passages WHERE path=?", (path,)).fetchall():
            self.db.execute("INSERT INTO fts(fts, rowid, norm) VALUES('delete', ?, ?)", (i, index_text(text)))
        self.db.execute("DELETE FROM passages WHERE path=?", (path,))

    def remove_file(self, path):
        path = str(Path(path).resolve())
        self._reset(path)
        self.db.execute("DELETE FROM files WHERE path=?", (path,))
        self.db.commit()

    def add_folder(self, folder):
        folder = Path(folder).resolve()
        self.db.execute("INSERT OR IGNORE INTO roots VALUES (?)", (str(folder),))
        res = {"indexed": 0, "unchanged": 0, "error": 0, "removed": 0}
        seen = set()
        for p in sorted(folder.rglob("*")):
            if p.is_file() and p.suffix.lower() in SUPPORTED and not any(x.startswith(".") for x in p.relative_to(folder).parts):
                seen.add(str(p))
                res[self.add_file(p)] += 1
        for (path,) in self.db.execute("SELECT path FROM files WHERE path LIKE ?", (str(folder) + "/%",)).fetchall():
            if path not in seen and not Path(path).exists():
                self.remove_file(path)
                res["removed"] += 1
        self.db.commit()
        return res

    def update(self):
        tot = {"indexed": 0, "unchanged": 0, "error": 0, "removed": 0}
        for (r,) in self.db.execute("SELECT path FROM roots").fetchall():
            if Path(r).exists():
                for k, v in self.add_folder(r).items():
                    tot[k] += v
        return tot

    def stats(self):
        f = self.db.execute("SELECT COUNT(*) FROM files").fetchone()[0]
        p = self.db.execute("SELECT COUNT(*) FROM passages").fetchone()[0]
        e = self.db.execute("SELECT path,error FROM files WHERE error IS NOT NULL").fetchall()
        return {"files": f, "passages": p, "errors": e}

    # ---- search ----
    def search(self, query, limit=8, now=None):
        since, until, q = when.parse(query, now)
        terms = list(dict.fromkeys(tokens(q)))
        if not terms:
            return []
        match = " OR ".join(f'"{t}"' for t in terms)
        rows = self.db.execute(
            "SELECT p.id,p.path,p.loc,p.text,bm25(fts) FROM fts JOIN passages p ON p.id=fts.rowid WHERE fts MATCH ? ORDER BY bm25(fts) LIMIT 400",
            (match,)).fetchall()
        best = {}
        for pid, path, loc, text, bm in rows:
            pt = set(tokens(text, keep_stop=True))
            hit = [t for t in terms if t in pt]
            if not hit:
                continue
            if len(terms) >= 4 and len(hit) < 2:
                continue
            cov = len(hit) / len(terms)
            score = cov * 10 + (-bm) * 0.3
            if loc == "file name":
                score += 3
            try:
                mt = os.stat(path).st_mtime
            except OSError:
                continue
            if since is not None and not (since <= mt < until):
                continue
            cur = best.get(path)
            if not cur or score > cur["score"]:
                best[path] = {"path": path, "loc": loc, "text": text, "score": score, "hit": hit, "terms": terms, "mtime": mt}
        out = sorted(best.values(), key=lambda r: -r["score"])[:limit]
        for r in out:
            r["reason"] = f"matched {len(r['hit'])} of {len(r['terms'])} words ({', '.join(r['hit'])}) in {r['loc']}"
            r["date_filter"] = since is not None
        return out
