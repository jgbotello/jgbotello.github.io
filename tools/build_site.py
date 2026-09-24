#!/usr/bin/env python3
"""Render the static GitHub Pages site using only the Python standard library.

Edit templates/pages, templates/layout.html, and data/*.json, then run this file.
The generated root HTML also works directly, without a server or build runtime.
"""
import argparse
import html
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
PAGES = {
    'index': ('Home', 'Jhon G. Botello — AI, M&S and Digital libraries'),
    'about': ('About', 'About Jhon G. Botello: education, research experience, and academic background.'),
    'projects': ('Research', 'Research in artificial intelligence, modeling and simulation, web science, and human mobility.'),
    'publications': ('Publications', 'Journal articles and conference papers by Jhon G. Botello, with searchable research topics and citations.'),
    'teaching': ('Teaching', 'Teaching in data science, programming, decision-making, and simulation.'),
    'blogs': ('Blog', 'Field notes and writing on AI, web archives, migration, and digital humanities.'),
    'contact': ('Contact', 'Get in touch with Jhon G. Botello and follow his research.'),
    'resume': ('CV', 'Read or download the resume of Jhon G. Botello.'),
}
TOPICS = {'ai': 'Artificial intelligence', 'simulation': 'Modeling & simulation', 'web': 'Web science', 'society': 'Society & mobility'}
TYPES = {'journal': 'Journal article', 'conference': 'Conference paper', 'non-peer-reviewed': 'Non-peer-reviewed contribution'}


def escape(value):
    return html.escape(str(value), quote=True)


def external_link_attrs(url):
    return ' target="_blank" rel="noopener noreferrer"' if url.startswith(("https://", "http://")) else ""


def read_data(name):
    return json.loads((ROOT / 'data' / f'{name}.json').read_text())


def tags(values):
    return '<div class="tags">' + ''.join(f'<span>{escape(TOPICS.get(value, value))}</span>' for value in values) + '</div>'


def citation(paper):
    year = 'In press' if paper['year'] == 'in-press' else paper['year']
    return f"{paper['authors']} ({year}). {paper['title']}. {paper['venue']}." + (f" {paper['url']}" if paper['url'] else '')


def publication(paper, compact=False):
    year = 'In press' if paper['year'] == 'in-press' else paper['year']
    title = escape(paper['title'])
    if paper['url']:
        title = f'<a href="{escape(paper["url"])}" target="_blank" rel="noopener noreferrer">{title}</a>'
    actions = ''
    if paper.get('pdf'):
        actions += f'<a href="{escape(paper["pdf"])}" target="_blank" rel="noopener noreferrer">View PDF <span aria-hidden="true">↗</span></a>'
    if paper['url']:
        label = 'View preprint' if 'arxiv.org' in paper['url'] else 'View publication'
        actions += f'<a href="{escape(paper["url"])}" target="_blank" rel="noopener noreferrer">{label} <span aria-hidden="true">↗</span></a>'
    if not compact:
        actions += f'<button type="button" class="cite-button" data-citation="{escape(citation(paper))}" aria-label="Cite: {escape(paper["title"])}" hidden>Cite this work <span aria-hidden="true">“</span></button>'
    summary = f'<p class="publication-summary">{escape(paper["summary"])}</p>' if paper['summary'] else ''
    thumbnail = f'<img class="publication-thumb" src="{escape(paper["image"])}" width="160" height="160" alt="" loading="lazy">'
    if paper.get('cover_alt'):
        thumbnail = f'<img class="publication-thumb editorial-cover" src="{escape(paper["image"])}" width="100" height="120" alt="{escape(paper["cover_alt"])}" loading="lazy">'
    elif paper.get('figure'):
        figure = paper['figure']
        thumbnail = f'<a class="publication-figure-link" href="{escape(paper["image"])}" target="_blank" rel="noopener noreferrer" aria-label="Open figure {figure["number"]} from {escape(paper["title"])} at full size"><img class="publication-thumb paper-figure" src="{escape(paper["image"])}" width="160" height="160" alt="{escape(figure["alt"])}" loading="lazy"></a>'
    return f'''<article id="{paper['id']}" class="publication-item{' publication-compact' if compact else ''}" data-year="{paper['year']}" data-type="{paper['type']}" data-topics="{' '.join(paper['topics'])}">
      {thumbnail}
      <div class="publication-content"><p class="publication-meta"><span>{year}</span><span>{TYPES[paper['type']]}</span></p>
      <h{'3' if compact else '2'}>{title}</h{'3' if compact else '2'}>
      <p class="publication-authors">{escape(paper['authors'])}</p><p class="publication-venue"><em>{escape(paper['venue'])}</em></p>
      {summary}{tags(paper['topics'])}</div><div class="publication-actions">{actions}</div>
    </article>'''


def blog(post, home=False):
    date = datetime.strptime(post['date'], '%Y-%m').strftime('%b %Y')
    source = 'WS-DL' if post['source'] == 'wsdl' else 'Storymodelers'
    image = f'<a class="blog-cover-wrapper" href="{escape(post["url"])}" tabindex="-1" aria-hidden="true" target="_blank" rel="noopener noreferrer"><img src="{post["image"]}" alt="" loading="lazy" width="600" height="360"></a>' if post['image'] else '<div class="text-cover" aria-hidden="true"><span>Field notes</span><span>Research,<br>in perspective.</span></div>'
    summary = f'<p class="blog-summary">{escape(post["summary"])}</p>' if post['summary'] else ''
    return f'''<article class="blog-card" data-year="{post['year']}" data-source="{post['source']}" data-topic="{post['topic']}" data-date="{post['date']}">{image}<div class="blog-card-body"><p class="blog-meta"><span>{source}</span><time datetime="{post['date']}">{date}</time></p><h{'3' if home else '2'}><a href="{escape(post['url'])}" target="_blank" rel="noopener noreferrer">{escape(post['title'])}</a></h{'3' if home else '2'}>{summary}{tags(post['tags'])}<a class="text-link blog-link" href="{escape(post['url'])}" target="_blank" rel="noopener noreferrer">Read the story <span aria-hidden="true">↗</span></a></div></article>'''


def render():
    layout = (ROOT / 'templates/layout.html').read_text()
    papers = read_data('publications')
    # In-press entries lead the bibliography; dated entries follow newest first.
    papers.sort(key=lambda p: 9999 if p['year'] == 'in-press' else int(p['year']), reverse=True)
    posts = sorted(read_data('blogs'), key=lambda p: p['date'], reverse=True)
    # Most recent publicly readable papers; preserve bibliography order for tied years.
    selected = [p for p in papers if p['year'] != 'in-press' and p.get('public_pdf')][:3]
    # Home shows a compact selection with real article images.
    home_posts = [next(p for p in posts if p['image'] and p['topic'] == topic) for topic in ['web-archives', 'migration']]
    profile_icons = {
        'Email': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 6 9 7 9-7"/>',
        'Google Scholar': '<path d="m2 9 10-6 10 6-10 6Z"/><path d="M6 12v6q6 5 12 0v-6M22 9v8"/>',
        'ORCID': '<circle cx="12" cy="12" r="10"/><path d="M7 10v7M11 7h3a5 5 0 0 1 0 10h-3Z"/><circle cx="7" cy="7" r=".6" fill="currentColor"/>',
        'LinkedIn': '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 10v7M11 17v-7m0 3a3 3 0 0 1 6 0v4"/><circle cx="7" cy="7" r=".6" fill="currentColor"/>',
        'GitHub': '<path d="M9 21v-3c-4 1-4-2-6-2m12 5v-4c0-1-.3-1.5-1-2 3-.4 6-1.5 6-6a5 5 0 0 0-1.5-3.5c.2-1 .2-2-.3-3.5-1.5 0-3 1-4 1.5a12 12 0 0 0-4.4 0C8.8 3 7.3 2 5.8 2c-.5 1.5-.5 2.5-.3 3.5A5 5 0 0 0 4 9c0 4.5 3 5.6 6 6-.7.5-1 1-1 2"/>',
        'X': '<path d="M4 3h4l12 18h-4ZM20 3l-7 8M4 21l7-8"/>',
    }
    profile_links = '<nav class="profile-social-links" aria-label="Contact and social profiles">' + ''.join(
        f'<a href="{escape(url)}"{external_link_attrs(url)}><svg class="profile-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{profile_icons[label]}</svg><span>{label}</span></a>' for label, url in [
            ('Email', 'mailto:jhongbm.12.jgbm@gmail.com'),
            ('Google Scholar', 'https://scholar.google.com/citations?user=x6VeC7sAAAAJ&hl=en'),
            ('ORCID', 'https://orcid.org/0009-0009-9344-4404'),
            ('LinkedIn', 'https://www.linkedin.com/in/jgbotello/'),
            ('GitHub', 'https://github.com/jgbotello'),
            ('X', 'https://x.com/Jhon_gbm12'),
        ]) + '</nav>'
    blocks = {
        '{{profile_links}}': profile_links,
        '{{publications}}': '\n'.join(publication(p) for p in papers),
        '{{selected_publications}}': '<div class="selected-publications">' + '\n'.join(publication(p, True) for p in selected) + '</div>',
        '{{blogs}}': '\n'.join(blog(p) for p in posts),
        '{{home_writing}}': '<div class="home-writing-grid">' + '\n'.join(blog(p, True) for p in home_posts) + '</div>',
    }
    results = {}
    for key, (label, description) in PAGES.items():
        body = (ROOT / f'templates/pages/{key}.html').read_text()
        for marker, content in blocks.items():
            body = body.replace(marker, content)
        navigation = '\n'.join(f'<li><a href="{name}.html"' + (' aria-current="page"' if name == key else '') + f'>{text}</a></li>' for name, (text, _) in PAGES.items() if name != 'contact')
        values = {'title': 'Jhon G. Botello | AI & Social Systems' if key == 'index' else f'{label} | Jhon G. Botello', 'description': description, 'body': body, 'page': key, 'navigation': navigation}
        output = layout
        for icon_label in ('Google Scholar', 'GitHub', 'LinkedIn'):
            icon = f'<svg class="profile-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{profile_icons[icon_label]}</svg>'
            output = output.replace('{{icon_' + icon_label.lower().replace(' ', '_') + '}}', icon)
        for marker, value in values.items():
            output = output.replace('{{' + marker + '}}', value if marker in {'body', 'navigation'} else escape(value))
        if '{{' in output:
            raise ValueError(f'Unresolved template marker in {key}')
        results[ROOT / f'{key}.html'] = output
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if generated pages are out of date, without writing.')
    args = parser.parse_args()
    stale = []
    for path, content in render().items():
        if args.check:
            if not path.exists() or path.read_text() != content:
                stale.append(path.name)
        else:
            path.write_text(content)
    if stale:
        raise SystemExit('Run python3 tools/build_site.py to update: ' + ', '.join(stale))
    print('Verified 8 generated pages.' if args.check else 'Built 8 static pages.')


if __name__ == '__main__':
    main()
