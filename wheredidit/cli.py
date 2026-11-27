import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

from .index import Index


def _show(res):
    if not res:
        print("No match. Nothing in the indexed files fits that description (try other words; the tool matches words and word forms, not full meaning).")
        return 1
    for i, r in enumerate(res, 1):
        d = datetime.fromtimestamp(r["mtime"]).strftime("%Y-%m-%d")
        print(f"{i}. {Path(r['path']).name}   (modified {d})")
        print(f"   {r['path']}")
        print(f"   Why: {r['reason']}")
        snippet = r["text"].replace("\n", " ")
        print(f"   \"{snippet[:160]}\"")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="wheredidit", description="Find files by what was inside them, not by name. Local only.")
    ap.add_argument("--db")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add", help="index a folder"); a.add_argument("folder")
    sub.add_parser("update", help="re-read changed files in all added folders")
    s = sub.add_parser("find", help="search"); s.add_argument("query", nargs="+"); s.add_argument("-n", type=int, default=5)
    sub.add_parser("status")
    w = sub.add_parser("watch", help="keep the index up to date"); w.add_argument("--every", type=int, default=30)
    args = ap.parse_args(argv)
    try: ix = Index(args.db)
    except Exception as e:
        print(f"wheredidit: cannot open the index database: {e}", file=sys.stderr); return 2
    if args.cmd == "add":
        if not Path(args.folder).is_dir():
            print("Not a folder:", args.folder); return 2
        r = ix.add_folder(args.folder)
        print(f"indexed {r['indexed']}, unchanged {r['unchanged']}, failed {r['error']}, removed {r['removed']}")
        for p, e in ix.stats()["errors"]:
            print("  could not read:", p, "-", e)
        if getattr(ix, "skipped", None):
            print("  skipped (type not supported): " + ", ".join(f"{n} {k}" for k, n in sorted(ix.skipped.items(), key=lambda x: -x[1])[:8]))
    elif args.cmd == "update":
        print(ix.update())
    elif args.cmd == "find":
        q = " ".join(args.query).strip()
        if not q:
            print("wheredidit: say what you remember about the file, for example: wheredidit find \"invoice from the electricity company\"", file=sys.stderr); return 2
        return _show(ix.search(q, limit=args.n))
    elif args.cmd == "status":
        st = ix.stats(); print(f"{st['files']} files, {st['passages']} passages")
    elif args.cmd == "watch":
        print(f"Watching every {args.every}s (Ctrl+C to stop). Uses file size and modified time, not a system file watcher.")
        try:
            while True:
                r = ix.update()
                if r["indexed"] or r["removed"]:
                    print(time.strftime("%H:%M:%S"), r)
                time.sleep(args.every)
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
