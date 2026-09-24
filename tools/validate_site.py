#!/usr/bin/env python3
"""Validate the rendered site's structure, local routes, and source data."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_site import PAGES, render


class Document(HTMLParser):
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.ids, self.links, self.labels = [], set(), [], []
        self.h1, self.main, self.active = 0, 0, 0
        self.doctype = False

    def handle_decl(self, value):
        self.doctype = value.lower() == 'doctype html'

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag not in self.VOID:
            self.stack.append(tag)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, f'Duplicate id {attrs["id"]}'
            self.ids.add(attrs['id'])
        self.h1 += tag == 'h1'
        self.main += tag == 'main'
        self.active += attrs.get('aria-current') == 'page'
        if tag == 'img':
            assert 'alt' in attrs, 'Image missing alt attribute'
        if tag == 'iframe':
            assert attrs.get('title'), 'Iframe missing title'
        if tag in {'input', 'select', 'textarea'}:
            self.labels.append(attrs.get('id'))
        for key in ('href', 'src'):
            if attrs.get(key):
                self.links.append(attrs[key])
        if attrs.get('target') == '_blank':
            assert 'noopener' in attrs.get('rel', ''), 'External window missing noopener'

    def handle_endtag(self, tag):
        assert self.stack and self.stack.pop() == tag, f'Unbalanced closing tag: {tag}'


def luminance(color):
    rgb = [int(color[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    channels = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in rgb]
    return sum(c * weight for c, weight in zip(channels, (.2126, .7152, .0722)))


def main():
    rendered = render()
    documents = {}
    for name in PAGES:
        path = ROOT / f'{name}.html'
        assert path.read_text() == rendered[path], f'{name} is not up to date'
        doc = Document()
        doc.feed(path.read_text())
        assert doc.doctype and not doc.stack, name
        assert (doc.h1, doc.main, doc.active) == (1, 1, 0 if name == 'contact' else 1), name
        for control in doc.labels:
            assert control and f'for="{control}"' in path.read_text(), f'Unlabelled control: {control}'
        documents[path.name] = doc
    for name, doc in documents.items():
        for ref in doc.links:
            url = urlsplit(ref)
            if url.scheme or url.netloc:
                continue
            target = ROOT / unquote(url.path) if url.path else ROOT / name
            assert target.is_file(), f'{name}: missing {ref}'
            if url.fragment and target.name in documents:
                assert unquote(url.fragment) in documents[target.name].ids, f'{name}: broken anchor {ref}'
    papers = json.loads((ROOT / 'data/publications.json').read_text())
    posts = json.loads((ROOT / 'data/blogs.json').read_text())
    assert len(papers) == 9 and len(posts) == 11
    assert len({p['id'] for p in papers}) == len(papers)
    for item in papers + posts:
        if item['image']:
            assert (ROOT / item['image']).is_file()
    assert (ROOT / 'files/Jhon_G_Botello_Resume.pdf').read_bytes().startswith(b'%PDF-')
    # Check the explicit foreground/background pairs in the shared design system.
    for foreground, background in [('202a26','fbfcf9'), ('5e665f','fbfcf9'), ('315e4b','fbfcf9'), ('ffffff','315e4b'), ('3f5d4d','e9eee7'), ('5e665f','f0f3ed')]:
        light, dark = sorted([luminance(foreground), luminance(background)], reverse=True)
        contrast = (light + .05) / (dark + .05)
        assert contrast >= 4.5, (foreground, background, contrast)
    print('PASS: 8 pages, generated output, HTML nesting, unique IDs, labels, local routes/anchors/assets, bibliography/blog counts, PDF integrity, and text color contrast (at least 4.5:1).')


if __name__ == '__main__':
    main()
