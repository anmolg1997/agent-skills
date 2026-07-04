#!/usr/bin/env python3
"""ai.py — CLI over the curated agentic-AI incident corpus.

Subcommands:
  search   keyword/class search over the corpus
  show     print one incident in full (by id)
  fetch    fetch an incident source URL as plain text (Wayback fallback)
  classes  list failure classes with counts

Stdlib only. Corpus lives at ../data/ai_incidents.json relative to this file.
"""
import argparse
import html
import html.parser
import json
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "ai_incidents.json"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def load():
    return json.loads(DATA.read_text(encoding="utf-8"))["entries"]


def blob(e):
    return " ".join([e["id"], e["org"], e["title"], e.get("mechanism", ""), e.get("lesson", ""),
                     e["failure_class"], " ".join(e.get("contributing_classes", []))]).lower()


def cmd_search(args, entries):
    terms = [t.lower() for t in args.terms]
    hits = []
    for e in entries:
        if args.cls and args.cls not in ([e["failure_class"]] + e.get("contributing_classes", [])):
            continue
        if args.org and args.org.lower() not in e["org"].lower():
            continue
        if terms and not all(t in blob(e) for t in terms):
            continue
        hits.append(e)
    if args.json:
        print(json.dumps(hits, indent=2, ensure_ascii=False))
        return
    for e in hits[: args.limit]:
        contrib = ("+" + ",".join(e["contributing_classes"])) if e.get("contributing_classes") else ""
        print(f"{e['id']}  [{e['failure_class']}{contrib}]  {e['org']} ({e['date']})")
        print(f"  {e['title']}")
        print(f"  LESSON: {e['lesson']}")
        print(f"  {e['urls'][0]}")
        print()
    print(f"-- {len(hits)} match(es)" + (f", showing {args.limit}" if len(hits) > args.limit else ""))


def find_entry(entries, eid):
    for e in entries:
        if e["id"] == eid:
            return e
    sys.exit(f"no incident with id {eid!r} (try: ai.py search <keyword>)")


def cmd_show(args, entries):
    print(json.dumps(find_entry(entries, args.id), indent=2, ensure_ascii=False))


class _Text(html.parser.HTMLParser):
    SKIP = {"script", "style", "nav", "header", "footer", "noscript", "svg", "form"}
    BLOCK = {"p", "div", "li", "br", "h1", "h2", "h3", "h4", "h5", "h6", "tr",
             "section", "article", "blockquote", "pre"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self._skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip += 1
        elif tag in self.BLOCK:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._skip:
            self._skip -= 1
        elif tag in self.BLOCK:
            self.out.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self.out.append(data)


def html_to_text(raw):
    p = _Text()
    try:
        p.feed(raw)
    except Exception:
        pass
    text = re.sub(r"[ \t]+", " ", "".join(p.out))
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _curl(url):
    r = subprocess.run(["curl", "-sL", "--max-time", "45", "--connect-timeout", "15",
                        "-A", UA, url], capture_output=True, text=True, errors="replace")
    return r.stdout if r.returncode == 0 else ""


def fetch_url(url):
    raw = _curl(url)
    if raw and len(html_to_text(raw)) > 400:
        return url, html_to_text(raw)
    api = "https://archive.org/wayback/available?url=" + urllib.parse.quote(url, safe="")
    try:
        snap = json.loads(_curl(api)).get("archived_snapshots", {}).get("closest", {})
        if snap.get("available"):
            wb = snap["url"]
            raw = _curl(wb)
            if raw:
                return wb, html_to_text(raw)
    except Exception:
        pass
    return url, html_to_text(raw) if raw else ""


def cmd_fetch(args, entries):
    if args.target.startswith("http"):
        candidates = [args.target]
    else:
        candidates = list(find_entry(entries, args.target)["urls"])
    src = text = ""
    for url in candidates:
        src, text = fetch_url(url)
        if text:
            break
    if not text:
        sys.exit(f"FAILED to fetch (tried: {', '.join(candidates)} + Wayback API). "
                 f"Try WebFetch/browser on: {candidates[0]}")
    if args.out:
        Path(args.out).write_text(f"SOURCE: {src}\n\n{text}", encoding="utf-8")
        print(f"{len(text)} chars from {src} -> {args.out}")
    else:
        print(f"SOURCE: {src}\n\n{text[: args.max_chars]}")


def cmd_classes(args, entries):
    from collections import Counter
    primary, contributing = Counter(), Counter()
    for e in entries:
        primary[e["failure_class"]] += 1
        for c in e.get("contributing_classes", []):
            contributing[c] += 1
    print("primary failure classes:")
    for c, n in primary.most_common():
        print(f"  {c}: {n}")
    print("\ncontributing classes:")
    for c, n in contributing.most_common():
        print(f"  {c}: {n}")
    print(f"\ntotal incidents: {len(entries)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="keyword/class search")
    s.add_argument("terms", nargs="*", help="AND-matched keywords")
    s.add_argument("--class", dest="cls", help="failure class (primary or contributing)")
    s.add_argument("--org", help="organization substring")
    s.add_argument("--limit", type=int, default=20)
    s.add_argument("--json", action="store_true")

    s = sub.add_parser("show", help="print one incident")
    s.add_argument("id")

    s = sub.add_parser("fetch", help="fetch source text (Wayback fallback)")
    s.add_argument("target", help="incident id or URL")
    s.add_argument("--out", help="write to file instead of stdout")
    s.add_argument("--max-chars", type=int, default=20000)

    sub.add_parser("classes", help="failure-class counts")

    args = ap.parse_args()
    entries = load()
    {"search": cmd_search, "show": cmd_show, "fetch": cmd_fetch,
     "classes": cmd_classes}[args.cmd](args, entries)


if __name__ == "__main__":
    main()
