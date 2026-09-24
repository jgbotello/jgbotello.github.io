"""Export only the homepage and its referenced assets for a staged launch."""
import argparse
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from build_site import ROOT, render


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    destination = parser.parse_args().destination.resolve()
    if destination.exists() and any(destination.iterdir()):
        raise SystemExit('Choose an empty destination directory.')
    document = render()[ROOT / 'index.html']
    # Remove calls to action and navigation to pages not included in this launch.
    document = re.sub(r'<li>\s*<a\b[^>]*href="(?!index\.html)[^"#:]+\.html[^\"]*"[^>]*>.*?</a>\s*</li>', '', document, flags=re.S)
    document = re.sub(r'<a\b[^>]*href="(?!index\.html)[^"#:]+\.html[^\"]*"[^>]*>.*?</a>', '', document, flags=re.S)
    document = re.sub(r'<div class="hero-actions">\s*</div>', '', document)
    document = re.sub(r'<button class="menu-toggle".*?</button>', '', document, flags=re.S)
    # With just Home in the navigation, no mobile menu is needed.
    document = document.replace('styles.css?v=footer-icons', 'styles.css?v=home-launch')
    assets = set()

    class References(HTMLParser):
        def handle_starttag(self, tag, attrs):
            for key, value in attrs:
                if key not in ('href', 'src') or not value:
                    continue
                url = urlsplit(value)
                if not url.scheme and not url.netloc and url.path:
                    assets.add(unquote(url.path))

    References().feed(document)
    destination.mkdir(parents=True, exist_ok=True)
    for asset in sorted(assets - {'index.html'}):
        source = (ROOT / asset).resolve()
        assert source.is_relative_to(ROOT) and source.is_file(), asset
        assert source.suffix != '.html', asset
        target = destination / asset
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    (destination / 'index.html').write_text(document)
    with (destination / 'styles.css').open('a') as css:
        css.write('\n/* Homepage-only launch: keep Home visible on mobile. */\n.js .site-nav { display: block; }\n')
    (destination / '.nojekyll').touch()
    assert list(destination.rglob('*.html')) == [destination / 'index.html']
    print(f'Exported Home and {len(assets) - 1} assets to {destination}')


if __name__ == '__main__':
    main()
