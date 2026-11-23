# augello.net: static site

Ten pages: home, three case studies, a process index with four process pages, and a 404. They share one header, footer, `<head>` and stylesheet. A small Python script (`build.py`, no installs) turns the files in `src/` into the finished site.

Three ways to use this project:

- **On your own web server (your current plan):** GitHub builds the finished site for you and you upload it to your server. No Python needed on your computer. See [Hosting on your own server](#hosting-on-your-own-server).
- **On GitHub Pages:** GitHub builds and publishes it for you. See [Publishing on GitHub Pages](#publishing-on-github-pages).
- **On your own computer:** see [Building locally](#building-locally).

---

## What you need to fill in (yellow highlights)

The build lists everything unfinished. Yellow marks details only you can supply:

- **Experience timeline** on the home page: employers, titles, years, one line each
- **Testimonial titles** for Bennish B. and Richard P.
- **Toolkit:** add analytics and testing tools you use
- **Booking link** (optional; delete the line if you don't want one)
- **Visuals** for each case study (one yellow note per page; delete the note when added)
- **Optional notes** on how ~60%/~30% were measured, and team adoption of the design system
- **Design-system "Environment":** your old page said "Average enterprise"; confirm the wording I proposed
- **Resume PDF:** save as `src/assets/Charles-Augello-Resume.pdf`
- **Images:** see `tools/image-list.md` (no Python) or `tools/fetch_images.py` (with Python)

Review the alt text on the process-page images too. I wrote it from your original captions without seeing the images.

To edit a page, open it in `src/pages/`. Each file has a few header lines (title, description, path), a `---` line, then the page body in HTML. To remove a yellow placeholder, replace the whole `<span class="todo">…</span>` with your text.

## Where things live

| To change… | Edit |
|---|---|
| Nav links, footer | `src/partials/header.html`, `footer.html` (every page updates) |
| Colors, fonts, spacing | top of `src/assets/css/site.css` (`:root` variables; dark mode is automatic) |
| A page's text | `src/pages/…` |
| Add a page | copy an existing file in `src/pages/`, set `path:`, link to it from the nav or home page |
| Old-URL redirects | `redirects.json` |

---

## Publishing on GitHub Pages

### 1. Create the repository

1. Sign in at github.com and choose **New repository**.
2. Name it exactly `YOURUSERNAME.github.io`, replacing `YOURUSERNAME` with your GitHub username (for example `janedoe.github.io`).
3. Choose **Public**, tick **Add a README file**, and create it.

The name matters. A repository with any other name publishes at `…github.io/repo-name/`, and this site's links and images assume it lives at the root.

### 2. Upload the project

1. Unzip `augello-site.zip` on your computer.
2. In the repository, choose **Add file → Upload files** and drag in everything *inside* the unzipped folder (the `src` and `tools` folders, `build.py`, `redirects.json`, `README.md` and the rest). Commit.
3. Hidden folders (names starting with a dot, like `.github`) often don't upload by drag and drop, so create the workflow by hand:
   - **Add file → Create new file**
   - In the name box type `.github/workflows/pages.yml` (typing the slashes creates the folders)
   - Paste in the contents of `pages-workflow.yml` from the unzipped folder, and commit.

If you use GitHub Desktop instead, you can add the whole folder, including hidden files, in one go.

### 3. Turn on publishing

In the repository: **Settings → Pages → Build and deployment → Source: GitHub Actions**.

Every commit to the `main` branch now rebuilds and publishes the site. Watch progress in the **Actions** tab. The first run takes about a minute. Your site appears at `https://YOURUSERNAME.github.io`.

### 4. Add your images, resume and details

- Images: download them using `tools/image-list.md` and upload them to `src/assets/img/` (**Add file → Upload files**, then go into that folder first).
- Resume: upload to `src/assets/` as `Charles-Augello-Resume.pdf`.
- Text: open a file in `src/pages/`, click the pencil icon, edit, and commit. The site republishes automatically.

If a run fails, open it in the **Actions** tab and read the "Build the site" step. It lists exactly what is missing.

### 5. Connect augello.net

Do this only after the GitHub preview looks right, and keep WordPress running until then.

1. In **Settings → Pages**, enter `augello.net` under **Custom domain** and save. (Add it here *before* changing DNS so nobody else can claim it.)
2. At the company where you registered the domain, open the DNS settings and:
   - remove any default `A`, `AAAA` or `CNAME` records the registrar added for the apex domain
   - add four **A records** for host `@`: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - add a **CNAME record** for host `www` pointing to `YOURUSERNAME.github.io`
3. Wait for DNS to update (it can take up to 24 hours), then return to **Settings → Pages** and tick **Enforce HTTPS** once it becomes available.
4. Don't use wildcard DNS records (`*.augello.net`).

### 6. Switch on the launch check

Open `.github/workflows/pages.yml` and change `STRICT_LAUNCH_CHECK: "false"` to `"true"`. From then on, a deploy fails (and the previous good site stays up) if any yellow placeholder, missing image or broken link slips back in.

### 7. Tell Google

Add `https://augello.net` in Google Search Console and submit `https://augello.net/sitemap.xml`. Update the links on your LinkedIn profile and resume to the new URLs.

### Redirects on GitHub Pages

GitHub Pages can't do server-side (301) redirects. Instead the build creates a small "page moved" page at each of your 8 old WordPress URLs. It sends visitors to the new page immediately and names the new page as the canonical one for search engines. This is a weaker signal than a true 301 but is the workable option on this host.

| Old | New |
|---|---|
| `/home/` | `/` |
| `/home/product-design/` | `/process/product-design/` |
| `/home/ui-design/` | `/process/ui-design/` |
| `/home/ux-design/` | `/process/ux-design/` |
| `/home/user-research/` | `/process/user-research/` |
| `/home/case-study-enterprise-journey-mapping-…/` | `/case-studies/journey-mapping/` |
| `/home/case-study-designing-a-decision-support-dashboard-…/` | `/case-studies/decision-support-dashboard/` |
| `/home/case-study-building-an-enterprise-design-system-…/` | `/case-studies/design-system/` |

After the domain is live, open each old URL in a browser and confirm it lands on the new page.

### If something goes wrong

- **Actions run is red:** open it, read the "Build the site" step. A line starting `-` names the file or placeholder to fix. If you turned on the launch check, this is the check doing its job.
- **Site is blank or unstyled:** confirm the repository is named exactly `YOURUSERNAME.github.io` and Source is set to **GitHub Actions**.
- **Images missing:** the file name must match exactly, including lowercase letters, and the files must be in `src/assets/img/`.
- **Warnings about action versions:** GitHub occasionally retires old versions of the helper steps in `pages.yml` (lines starting `uses:`). The warning names the newer version; change the number and commit.
- **Custom domain shows an error:** DNS changes can take up to 24 hours. Re-check the records against step 5.

---

## Hosting on your own server

**What your technician needs to know:** this is a static site, so it is plain HTML, CSS, images and a PDF. There is no PHP, database or WordPress. Any Apache or nginx web server can host it.

### 1. Get the finished site from GitHub

1. In your repository, open the **Actions** tab and choose **Build site for own server** on the left.
2. Click **Run workflow**. Tick **strict** only for the final upload (it stops if a yellow placeholder, missing image or broken link remains). Click the green button.
3. After about a minute, open the finished run, scroll to **Artifacts**, and download **augello-site-for-server**. Unzip it. This folder is the finished site (not the source files).

If the workflow isn't listed, create it once: **Add file → Create new file**, name it `.github/workflows/build-for-server.yml`, paste in the contents of `build-for-server-workflow.yml` from this project, and commit.

### 2. Upload to the server

1. **Back up first:** have the technician (or your host's panel) back up the WordPress files and database.
2. Upload everything *inside* the unzipped folder to the site's web root (often `public_html`, `www` or `htdocs`) with an SFTP/FTP program or the host's File Manager.
3. Remove or move the old WordPress files (`wp-admin`, `wp-content`, `wp-includes`, `index.php` and the other `wp-*` files) so they don't compete with the new pages. Replace any old `.htaccess` with the new one.

### 3. Server settings (Apache)

The folder already contains an `.htaccess` file, which does the server's work:

- forces HTTPS and moves `www` to `augello.net`
- redirects your old WordPress URLs to the new pages
- serves the custom 404 page
- turns on compression and caching, and adds light security headers

Some upload tools and file managers hide files that start with a dot. If you don't see `.htaccess` on the server, upload `htaccess.txt` and rename it to `.htaccess`.

Ask your technician to confirm:

- `.htaccess` files are honored (`AllowOverride` set to `All`, or at least `FileInfo` and `Options`)
- the modules `mod_rewrite`, `mod_alias`, `mod_headers`, `mod_expires` and `mod_deflate` are enabled (the last three are optional; the file skips them safely if absent)
- **HTTPS is installed.** The pages declare `https://augello.net` as their address, so a certificate (the host's free AutoSSL or Let's Encrypt) must be in place before launch.

If the technician says the server is nginx after all, tell me and I'll adapt the files.

### 4. DNS

Point `augello.net` (an `A` record) and `www` at your server, which your technician will do. Also **remove the forwarding rule** at your registrar that currently sends augello.net to `charles-augello.github.io`; otherwise it will override the new DNS records. Changes can take up to 24 hours to spread.

### 5. Check it works

- `https://augello.net` loads with styling and images
- `http://augello.net` and `https://www.augello.net` both land on `https://augello.net`
- An old address returns a permanent redirect: `curl -I https://augello.net/home/ux-design/` should show `301` and `/process/ux-design/`
- `https://augello.net/robots.txt` and `https://augello.net/sitemap.xml` open
- A made-up address such as `https://augello.net/nothing` shows the custom 404 page
- The resume PDF link works

Then submit `sitemap.xml` in Google Search Console and update the links on LinkedIn and your resume.

### If something goes wrong

- **"500 Internal Server Error" right after uploading:** the server is rejecting a line in `.htaccess`. Rename the file to `htaccess-off.txt` so the site loads again, then ask the technician to read the server's error log. The usual cause is the line `Options -Indexes` when the server doesn't allow it in `.htaccess`; deleting that one line fixes it.
- **"Too many redirects":** the host or a CDN is already forcing HTTPS. Delete the block in `.htaccess` that starts `<IfModule mod_rewrite.c>`.
- **Pages load but without styling:** the `assets` folder didn't upload, or it landed one folder too deep. `index.html` and `assets` should sit side by side in the web root.
- **Old WordPress pages still show:** old files are still in the web root. Remove them (step 2).
- **Old addresses don't redirect:** `.htaccess` isn't being read (see the checks above).

### 6. After launch

- **Updating the site:** edit the files on GitHub as before, run **Build site for own server** again, and upload the new folder (or only the changed files).
- **The GitHub Pages copy:** the pages name `augello.net` as the preferred address, so search engines will favor your server's copy. Once you're happy, you can switch the GitHub copy off in **Settings → Pages**.
- Keep the WordPress backup for a few months.

## Building locally

Needs Python 3 only.

```bash
python3 tools/fetch_images.py     # pull your images from WordPress (run before you shut it down)
python3 build.py                  # build into ./dist and list anything unfinished
python3 build.py --strict         # same, but fails until everything is done
python3 build.py --github         # GitHub Pages build (redirect pages only, adds .nojekyll)
```

Preview: `cd dist && python3 -m http.server 8000`, then open http://localhost:8000.

On a host with real redirect support (your own server, Netlify, Cloudflare Pages), the default build also writes `_redirects` (Netlify/Cloudflare), `.htaccess` (Apache) and `nginx-redirects.conf` (nginx, include inside your `server { }` block), plus `redirects.csv`. Use the one for your host and ignore the others. Test with `curl -I https://augello.net/home/ux-design/`; you should see `301` and the new location.

## Notes on content

- Case-study text is your original wording with small edits: typos fixed and "Day 2–3" style ranges tidied. The metrics are unchanged.
- The home page dashboard card uses the real details from your dashboard case study (UX Lead & Interaction Designer, ~15 business days, ~35% fewer follow-up requests).
- Your phone number is not on the public pages (the footer says "available on request"). Put it back in `src/partials/footer.html` if you prefer.
- The site is set to be indexed. Your WordPress pages were sending `noindex, nofollow`, which hid them from search; that is gone here (only the 404 page is noindex).
