#!/usr/bin/env python3
"""pm.py, CLI over the enriched incident-postmortem index.

Subcommands:
  search   keyword/tag search over the index
  show     print one entry in full (by id)
  fetch    fetch a postmortem's content as plain text (Wayback fallback on failure)
  stats    corpus statistics by category / root-cause / blast-radius
  refresh  re-clone upstream repo, re-parse, merge with existing enrichment

Stdlib only. Index lives at ../data/postmortems.json relative to this file.
"""
import argparse
import html
import html.parser
import json
import re
import subprocess
import sys
import tempfile
import urllib.parse
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "postmortems.json"
EXTRA = Path(__file__).resolve().parent.parent / "data" / "extra_incidents.json"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def load():
    index = json.loads(DATA.read_text(encoding="utf-8"))
    if EXTRA.exists():  # merged for search/show/fetch; refresh never touches EXTRA
        index["categories"].extend(json.loads(EXTRA.read_text(encoding="utf-8"))["categories"])
    return index


def iter_entries(index, category=None):
    for cat in index["categories"]:
        if category and category not in (cat["slug"], cat["name"]):
            continue
        for e in cat["entries"]:
            yield cat, e


def entry_blob(e):
    parts = [e["id"], e["org"], e.get("summary", ""), e.get("trigger", ""), e.get("lesson", ""),
             " ".join(e.get("root_cause_class", [])), " ".join(e.get("blast_radius", [])),
             e.get("suggested_category", "")]
    return " ".join(parts).lower()


def cmd_search(args, index):
    terms = [t.lower() for t in args.terms]
    hits = []
    for cat, e in iter_entries(index, args.category):
        if args.org and args.org.lower() not in e["org"].lower():
            continue
        if args.cause and args.cause not in e.get("root_cause_class", []):
            continue
        if args.blast and args.blast not in e.get("blast_radius", []):
            continue
        blob = entry_blob(e)
        if terms and not all(t in blob for t in terms):
            continue
        hits.append((cat, e))
    if args.json:
        print(json.dumps([{**e, "category": c["slug"]} for c, e in hits],
                         indent=2, ensure_ascii=False))
        return
    for cat, e in hits[: args.limit]:
        status = "" if e.get("alive", True) else " [DEAD LINK, use fetch, it falls back to Wayback]"
        print(f"{e['id']}  ({cat['slug']})  {e['org']}{status}")
        print(f"  cause={','.join(e.get('root_cause_class', []))}  "
              f"blast={','.join(e.get('blast_radius', []))}")
        print(f"  {e.get('summary', '')[:220]}")
        if e.get("lesson"):
            print(f"  LESSON: {e['lesson']}")
        print(f"  {e['url']}")
        print()
    print(f"-- {len(hits)} match(es)" + (f", showing {args.limit}" if len(hits) > args.limit else ""))


def find_entry(index, eid):
    for _, e in iter_entries(index):
        if e["id"] == eid:
            return e
    sys.exit(f"no entry with id {eid!r} (try: pm.py search {eid.split('-')[0]})")


def cmd_show(args, index):
    print(json.dumps(find_entry(index, args.id), indent=2, ensure_ascii=False))


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
    text = "".join(p.out)
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _curl(url):
    r = subprocess.run(["curl", "-sL", "--max-time", "45", "--connect-timeout", "15",
                        "-A", UA, url], capture_output=True, text=True, errors="replace")
    return r.stdout if r.returncode == 0 else ""


def fetch_url(url):
    """Fetch URL as text; on failure/empty, fall back to a Wayback snapshot."""
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


def cmd_fetch(args, index):
    candidates = []
    if args.target.startswith("http"):
        candidates = [args.target]
    else:
        e = find_entry(index, args.target)
        # live original first (archive.org throttles), then archived/canonical, then wayback
        if e.get("original_url"):
            candidates.append(e["original_url"])
        candidates.append(e["url"])
        if e.get("wayback_url"):
            candidates.append(e["wayback_url"])
    src = text = ""
    for url in candidates:
        src, text = fetch_url(url)
        if text:
            break
    if not text:
        tried = " , ".join(candidates)
        sys.exit(f"FAILED to fetch (tried: {tried} + Wayback API). Try WebFetch/browser on: {candidates[0]}")
    if args.out:
        Path(args.out).write_text(f"SOURCE: {src}\n\n{text}", encoding="utf-8")
        print(f"{len(text)} chars from {src} -> {args.out}")
    else:
        print(f"SOURCE: {src}\n\n{text[: args.max_chars]}")


def cmd_stats(args, index):
    from collections import Counter
    causes, blasts, orgs = Counter(), Counter(), Counter()
    n_alive = n = 0
    for cat in index["categories"]:
        print(f"{cat['slug']}: {cat['count']}")
    for _, e in iter_entries(index):
        n += 1
        n_alive += bool(e.get("alive", True))
        orgs[e["org"]] += 1
        for c in e.get("root_cause_class", []):
            causes[c] += 1
        for b in e.get("blast_radius", []):
            blasts[b] += 1
    print(f"\ntotal={n} alive_links={n_alive}")
    print("\nroot causes:", ", ".join(f"{k}={v}" for k, v in causes.most_common()))
    print("\nblast radius:", ", ".join(f"{k}={v}" for k, v in blasts.most_common()))
    print("\ntop orgs:", ", ".join(f"{k}={v}" for k, v in orgs.most_common(15)))


def cmd_refresh(args, index):
    """Re-clone upstream, re-parse README, merge enrichment for entries that still exist."""
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["git", "clone", "--depth", "1",
                        "https://github.com/danluu/post-mortems", td],
                       check=True, capture_output=True)
        text = (Path(td) / "README.md").read_text(encoding="utf-8")
    old = {e["id"]: e for _, e in iter_entries(index)}
    old_by_url = {e["url"]: e for _, e in iter_entries(index)}
    entry_re = re.compile(r"^\[(?P<org>[^\]]+)\]\((?P<url>[^)\s]+)\)\.?\s*(?P<desc>.*)$", re.S)

    def slugify(s):
        return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")

    new_index = {"source": index["source"], "categories": []}
    seen, added = set(), 0
    for sec in re.split(r"^## ", text, flags=re.M)[1:]:
        title, _, body = sec.partition("\n")
        title = title.strip()
        if title in ("Table of Contents", "Contributors"):
            continue
        entries = []
        for para in re.split(r"\n\s*\n", body):
            m = entry_re.match(para.strip())
            if not m:
                continue
            org, url = m.group("org").strip(), m.group("url").strip()
            desc = re.sub(r"\s+", " ", m.group("desc").strip())
            base = slugify(org)
            eid, i = base, 1
            while eid in seen:
                i += 1
                eid = f"{base}-{i}"
            seen.add(eid)
            prev = old_by_url.get(url) or old.get(eid)
            merged = dict(prev) if prev and prev.get("url") == url else {}
            if not merged:
                added += 1
            merged.update({"id": eid, "org": org, "url": url, "summary": desc,
                           "archived": url.startswith("https://web.archive.org/")})
            entries.append(merged)
        new_index["categories"].append({"name": title, "slug": slugify(title),
                                        "count": len(entries), "entries": entries})
    DATA.write_text(json.dumps(new_index, indent=2, ensure_ascii=False), encoding="utf-8")
    total = sum(c["count"] for c in new_index["categories"])
    print(f"refreshed: {total} entries ({added} new/changed, new ones lack tags; re-run tagging on them)")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="keyword/tag search")
    s.add_argument("terms", nargs="*", help="AND-matched keywords")
    s.add_argument("--category", help="category slug (e.g. config-errors)")
    s.add_argument("--org", help="organization substring")
    s.add_argument("--cause", help="root_cause_class tag")
    s.add_argument("--blast", help="blast_radius tag")
    s.add_argument("--limit", type=int, default=20)
    s.add_argument("--json", action="store_true", help="full JSON output")

    s = sub.add_parser("show", help="print one entry")
    s.add_argument("id")

    s = sub.add_parser("fetch", help="fetch postmortem text (Wayback fallback)")
    s.add_argument("target", help="entry id or URL")
    s.add_argument("--out", help="write to file instead of stdout")
    s.add_argument("--max-chars", type=int, default=20000)

    sub.add_parser("stats", help="corpus statistics")
    sub.add_parser("refresh", help="re-sync index with upstream repo")

    args = ap.parse_args()
    index = load()
    {"search": cmd_search, "show": cmd_show, "fetch": cmd_fetch,
     "stats": cmd_stats, "refresh": cmd_refresh}[args.cmd](args, index)


if __name__ == "__main__":
    main()
