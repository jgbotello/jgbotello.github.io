# Jhon G. Botello — personal research website

An editorial academic portfolio, served as static HTML on GitHub Pages.

## Preview locally

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Open http://localhost:8000. No JavaScript framework, package manager, external
fonts, or server-side runtime is required. The root HTML files also open directly.

## Edit the site

- `templates/layout.html`: shared header, navigation shell, footer, metadata.
- `templates/pages/`: the eight pages' editable content and composition.
- `data/publications.json`: bibliography, research topics, summaries, and links.
- `data/blogs.json`: writing archive and filter metadata.
- `styles.css`: shared design tokens, components, responsive and print styles.
- `scripts.js`: mobile navigation, filtering, search, sorting, citations, and email copy.
- `images/`: portrait, existing article images, and decorative editorial assets.

After editing templates or data, regenerate the root HTML:

```sh
python3 tools/build_site.py
python3 tools/build_site.py --check
python3 tools/validate_site.py
```

The builder uses only Python's standard library. Commit generated HTML together
with its source changes; GitHub Pages serves those files without a build pipeline.
Edit `PAGES` in `tools/build_site.py` to change the global navigation. Research
continues to use `projects.html`, writing uses `blogs.html`, and the existing
resume PDF and `resume.html` remain at their original paths.

## Browser verification

`tools/check_browser.py` uses Python Playwright and an installed Chromium browser.
It starts an isolated local server, tests all pages at five viewport widths, and
checks navigation, filters, search, sorting, citations, downloads, and no-JavaScript
fallbacks. Set `CHROME_BIN` if Chrome is installed at a nonstandard location.
Screenshots are written to a `botello-site-checks` folder in the system temp directory.

```sh
python3 -m venv /tmp/botello-browser-check
/tmp/botello-browser-check/bin/pip install playwright
# Install a Playwright browser if Google Chrome is not already installed:
/tmp/botello-browser-check/bin/playwright install chromium
/tmp/botello-browser-check/bin/python tools/check_browser.py
```

See `DESIGN-NOTES.md` for design choices, content provenance, and known source
limitations. Asset provenance and the image-generation prompt are in
`images/editorial/README.md`.
