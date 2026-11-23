#!/usr/bin/env python3
"""Tiny static-site builder for augello.net (standard library only).

    python3 build.py            build into ./dist and report problems
    python3 build.py --strict   same, but exit 1 if anything is unfinished
                                (yellow placeholders, missing images/links).
                                Use this before every deploy.
    python3 build.py --github   build for GitHub Pages (adds .nojekyll, skips
                                the Apache/nginx/Netlify redirect files)

Flags can be combined: python3 build.py --github --strict

Pages live in src/pages/**.html: a few `key: value` header lines, a line with
---, then the page body. The shared <head>, header and footer come from
src/partials/. Redirects come from redirects.json.
"""
import datetime, html, json, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).parent
SRC, DIST = ROOT / "src", ROOT / "dist"
SITE = "https://augello.net"
STRICT = "--strict" in sys.argv
GITHUB = "--github" in sys.argv   # GitHub Pages: redirect stubs only, no server config files

problems, warnings = [], []


def load(name):
    return (SRC / "partials" / name).read_text(encoding="utf-8")


def fill(template, values):
    return re.sub(r"\{\{(\w+)\}\}", lambda m: str(values.get(m.group(1), m.group(0))), template)


def parse(path):
    raw = path.read_text(encoding="utf-8")
    head, sep, body = raw.partition("\n---\n")
    if not sep:
        sys.exit(f"{path}: missing '---' separator after header lines")
    meta = {}
    for line in head.splitlines():
        if line.strip():
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    for key in ("title", "description", "path"):
        if key not in meta:
            sys.exit(f"{path}: missing '{key}:' header")
    return meta, body


def out_file(url_path):
    if url_path.endswith(".html"):
        return DIST / url_path.lstrip("/")
    return DIST / url_path.strip("/") / "index.html" if url_path != "/" else DIST / "index.html"


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    if (SRC / "assets").exists():
        shutil.copytree(SRC / "assets", DIST / "assets")

    head_t, header_t, footer_t = load("head.html"), load("header.html"), load("footer.html")
    year = datetime.date.today().year
    pages = []

    for f in sorted((SRC / "pages").rglob("*.html")):
        meta, body = parse(f)
        nav = meta.get("nav", "none")
        canonical = SITE + meta["path"] if not meta["path"].endswith(".html") else SITE + "/"
        values = {
            "title": html.escape(meta["title"], quote=True),
            "description": html.escape(meta["description"], quote=True),
            "robots": meta.get("robots", "index, follow, max-image-preview:large"),
            "canonical": SITE + meta["path"],
            "og_type": meta.get("og_type", "website"),
            "extra_head": "",
            "c_work": ' aria-current="page"' if nav == "work" else "",
            "c_process": ' aria-current="page"' if nav == "process" else "",
            "year": year,
        }
        if meta["path"].endswith(".html"):  # e.g. 404: no canonical needed
            head = fill(head_t, values).replace(f'<link rel="canonical" href="{values["canonical"]}">\n', "")
        else:
            head = fill(head_t, values)
        page = (
            '<!doctype html>\n<html lang="en">\n<head>\n' + head + "</head>\n<body>\n"
            '<a class="skip" href="#main">Skip to content</a>\n'
            + fill(header_t, values) + '<main id="main">\n' + body.strip() + "\n</main>\n"
            + fill(footer_t, values) + "</body>\n</html>\n"
        )
        target = out_file(meta["path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page, encoding="utf-8")
        pages.append((meta, target, page))

        # per-page checks
        label = meta["path"]
        if len(re.findall(r"<h1[ >]", page)) != 1:
            problems.append(f"{label}: needs exactly one <h1>")
        if len(meta["description"]) > 170:
            warnings.append(f"{label}: description is {len(meta['description'])} chars (aim for <=160)")
        if len(meta["title"]) > 75:
            warnings.append(f"{label}: title is {len(meta['title'])} chars (aim for <=70)")
        n = page.count('class="todo"')
        if n:
            problems.append(f"{label}: {n} yellow placeholder(s) still to fill in")

    write_seo_files(pages)
    write_redirects()
    check_links(pages)
    report(pages)


def write_seo_files(pages):
    today = datetime.date.today().isoformat()
    urls = [m["path"] for m, _, _ in pages if m.get("sitemap", "true") != "false" and m.get("robots", "").find("noindex") < 0]
    entries = "".join(
        f"  <url>\n    <loc>{SITE}{u}</loc>\n    <lastmod>{today}</lastmod>\n"
        f"    <priority>{'1.0' if u == '/' else '0.8' if u.startswith('/case-studies') else '0.6'}</priority>\n  </url>\n"
        for u in urls
    )
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + entries + "</urlset>\n", encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")


def write_redirects():
    rules = json.loads((ROOT / "redirects.json").read_text(encoding="utf-8"))
    pairs = []
    for r in rules:
        old = r["from"]
        pairs.append((old, r["to"]))
        if old != "/" and old.endswith("/"):  # also match the no-trailing-slash form
            pairs.append((old.rstrip("/"), r["to"]))

    # Redirect stub pages. Hosts that cannot do server-side redirects (GitHub
    # Pages) serve these: an instant meta refresh plus a canonical link, which
    # search engines treat as a move. On hosts with real 301 rules the server
    # answers first, so the stubs are harmless there.
    for r in rules:
        old, new = r["from"], r["to"]
        stub = DIST / old.strip("/") / "index.html" if old != "/" else None
        if stub is None:
            continue
        stub.parent.mkdir(parents=True, exist_ok=True)
        stub.write_text(
            '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            "<title>Page moved</title>\n"
            f'<link rel="canonical" href="{SITE}{new}">\n'
            f'<meta http-equiv="refresh" content="0; url={new}">\n'
            f'<script>location.replace("{new}")</script>\n'
            "</head>\n<body>\n"
            f'<p>This page has moved to <a href="{new}">{SITE}{new}</a>.</p>\n'
            "</body>\n</html>\n", encoding="utf-8")

    # human-readable map
    (DIST / "redirects.csv").write_text(
        "old_url,new_url\n" + "".join(f"{SITE}{r['from']},{SITE}{r['to']}\n" for r in rules), encoding="utf-8")

    if GITHUB:
        # GitHub Pages: no server rules, and no Jekyll processing of the files
        (DIST / ".nojekyll").write_text("", encoding="utf-8")
    else:
        # Netlify / Cloudflare Pages
        (DIST / "_redirects").write_text(
            "".join(f"{o}  {t}  301\n" for o, t in pairs), encoding="utf-8")

        # Apache (.htaccess): HTTPS + bare domain, exact-match redirects, 404 page,
        # compression, caching and light security headers.
        host = SITE.split("//", 1)[1]
        ht = [
            "# Generated by build.py. Upload as .htaccess in the web root",
            "# (or upload htaccess.txt and rename it to .htaccess).",
            "Options -Indexes",
            "DirectoryIndex index.html",
            "ErrorDocument 404 /404.html",
            "",
            f"# Send every request to https://{host} (this also moves www to the bare domain).",
            "# If your host or CDN already handles HTTPS and you see a redirect loop, delete this block.",
            "<IfModule mod_rewrite.c>",
            "RewriteEngine On",
            "RewriteCond %{HTTPS} off [OR]",
            "RewriteCond %{HTTP_HOST} ^www\\. [NC]",
            f"RewriteRule ^ https://{host}%{{REQUEST_URI}} [L,R=301]",
            "</IfModule>",
            "",
            "# Old WordPress URLs -> new pages (exact matches only, with or without trailing slash)",
        ]
        ht += [f"RedirectMatch 301 ^{re.escape(r['from'].rstrip('/'))}/?$ {SITE}{r['to']}" for r in rules]
        ht += [
            "",
            "<IfModule mod_deflate.c>",
            "AddOutputFilterByType DEFLATE text/html text/css text/plain application/javascript application/xml image/svg+xml",
            "</IfModule>",
            "",
            "<IfModule mod_expires.c>",
            "ExpiresActive On",
            'ExpiresByType text/html "access plus 10 minutes"',
            'ExpiresByType text/css "access plus 1 week"',
            'ExpiresByType image/png "access plus 1 month"',
            'ExpiresByType image/jpeg "access plus 1 month"',
            'ExpiresByType image/gif "access plus 1 month"',
            'ExpiresByType application/pdf "access plus 1 week"',
            "</IfModule>",
            "",
            "<IfModule mod_headers.c>",
            'Header always set X-Content-Type-Options "nosniff"',
            'Header always set Referrer-Policy "strict-origin-when-cross-origin"',
            'Header always set X-Frame-Options "SAMEORIGIN"',
            "</IfModule>",
        ]
        htaccess = "\n".join(ht) + "\n"
        (DIST / ".htaccess").write_text(htaccess, encoding="utf-8")
        # many upload tools hide files starting with a dot, so also ship a visible copy
        (DIST / "htaccess.txt").write_text(htaccess, encoding="utf-8")

        # nginx snippet: include inside your server { } block
        ng = ["# Generated by build.py. Include inside server { }"]
        ng += [f"location = {o} {{ return 301 {t}; }}" for o, t in pairs if o != "/"]
        ng += ["error_page 404 /404.html;"]
        (DIST / "nginx-redirects.conf").write_text("\n".join(ng) + "\n", encoding="utf-8")

    # redirect targets must exist
    for r in rules:
        if not out_file(r["to"]).exists():
            problems.append(f"redirects.json: target {r['to']} does not exist")


ATTR = re.compile(r'(?:href|src)="([^"]+)"')


def check_links(pages):
    ids = {}
    for _, f, page in pages:
        ids[f] = set(re.findall(r'\sid="([^"]+)"', page))
    for meta, f, page in pages:
        for ref in sorted(set(ATTR.findall(page))):
            if re.match(r"(https?:|mailto:|tel:|data:)", ref):
                continue
            path, _, frag = ref.partition("#")
            path = path.split("?")[0]
            if path == "":
                tgt = f
            elif path.startswith("/"):
                tgt = out_file(path) if not Path(path).suffix else DIST / path.lstrip("/")
            else:
                problems.append(f"{meta['path']}: relative link '{ref}' (use root-relative /paths)")
                continue
            if not tgt.exists():
                problems.append(f"{meta['path']}: missing file for '{ref}'")
            elif frag and tgt.suffix == ".html" and frag not in ids.get(tgt, set()):
                problems.append(f"{meta['path']}: no #{frag} anchor on {path or 'this page'}")


def report(pages):
    print(f"Built {len(pages)} pages into {DIST.relative_to(ROOT)}/")
    for w in warnings:
        print("  warning:", w)
    if problems:
        print(f"\n{len(problems)} thing(s) to finish before launch:")
        for p in problems:
            print("  -", p)
    else:
        print("No problems found.")
    if STRICT and problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
