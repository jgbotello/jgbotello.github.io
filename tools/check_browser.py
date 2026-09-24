"""Integration checks for the static website. Requires Python Playwright."""
from pathlib import Path
from urllib.parse import urlsplit,unquote
from playwright.sync_api import sync_playwright, expect
import os, tempfile
root=Path(__file__).resolve().parents[1]
ARTIFACTS=Path(tempfile.gettempdir())/'botello-site-checks'
ARTIFACTS.mkdir(exist_ok=True)
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(root)))
Thread(target=server.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{server.server_port}/'

with sync_playwright() as p:
    chrome=os.environ.get('CHROME_BIN')
    if not chrome and Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome').exists():
        chrome='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    browser=p.chromium.launch(executable_path=chrome,headless=True)
    context=browser.new_context(accept_downloads=True)
    page=context.new_page();errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    pages=['index','about','projects','publications','teaching','blogs','contact','resume']
    for width in [1440,1024,768,390,320]:
        page.set_viewport_size({'width':width,'height':1000})
        for name in pages:
            page.goto(BASE+name+'.html')
            assert page.evaluate('document.compatMode') == 'CSS1Compat', name
            expect(page.locator('h1')).to_have_count(1),name
            expect(page.locator('nav[aria-label="Main navigation"] a[aria-current="page"]')).to_have_count(0 if name == 'contact' else 1),name
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),(width,name,'overflow')
            for ref in page.locator('[href],img[src],iframe[src],script[src]').evaluate_all('(els)=>els.map(e=>e.getAttribute("href")||e.getAttribute("src"))'):
                u=urlsplit(ref)
                if not u.scheme and u.path: assert (root/unquote(u.path)).is_file(),(name,ref)
            page.locator('img').evaluate_all('(imgs)=>imgs.forEach(i=>i.loading="eager")')
            page.wait_for_function('Array.from(document.images).every(i=>i.complete && i.naturalWidth>0)')
            if width in [1440,390]:
                page.screenshot(path=str(ARTIFACTS/f'{name}-{width}.png'),full_page=True)
                page.screenshot(path=str(ARTIFACTS/f'{name}-{width}-viewport.png'))
            if width==390:
                expect(page.locator('#mainNav')).not_to_be_visible()
                page.click('.menu-toggle');expect(page.locator('#mainNav')).to_be_visible()
                page.keyboard.press('Escape');expect(page.locator('#mainNav')).not_to_be_visible()
                expect(page.locator('.menu-toggle')).to_be_focused()
    page.set_viewport_size({'width':1440,'height':1000})
    page.goto(BASE+'publications.html')
    expect(page.locator('.publication-item:visible')).to_have_count(9)
    page.select_option('#yearFilter','2024');page.select_option('#typeFilter','journal')
    expect(page.locator('.publication-item:visible')).to_have_count(1)
    page.select_option('#yearFilter','2023');expect(page.locator('#noResultsMessage')).to_be_visible()
    page.click('[data-reset-publications]');expect(page.locator('.publication-item:visible')).to_have_count(9)
    page.select_option('#yearFilter','in-press');expect(page.locator('.publication-item:visible')).to_have_count(2)
    page.click('button[type=reset]');page.fill('#publicationSearch','NetLogo');expect(page.locator('.publication-item:visible')).to_have_count(1)
    page.fill('#publicationSearch','nonexistent-query');expect(page.locator('#noResultsMessage')).to_be_visible()
    page.click('[data-reset-publications]');page.click('[data-topic-filter="web"]');expect(page.locator('.publication-item:visible')).to_have_count(1)
    page.click('button[type=reset]');page.select_option('#publicationSort','oldest');assert page.locator('.publication-item').first.get_attribute('data-year')=='2023'
    page.select_option('#publicationSort','newest');assert page.locator('.publication-item').first.get_attribute('data-year')=='in-press'
    page.locator('[data-citation]').first.click();expect(page.locator('#citationDialog')).to_be_visible()
    assert 'Ottoman' in page.locator('#citationText').input_value()
    with page.expect_download() as download_info:page.click('#downloadCitation')
    download=download_info.value;assert download.suggested_filename=='botello-citation.txt'
    assert 'Ottoman' in Path(download.path()).read_text()
    page.click('#copyCitation');expect(page.locator('#citationStatus')).not_to_be_empty()
    page.keyboard.press('Escape');expect(page.locator('#citationDialog')).not_to_be_visible()
    page.goto(BASE+'blogs.html');expect(page.locator('.blog-card:visible')).to_have_count(11)
    assert page.locator('.blog-card').first.get_attribute('data-date')=='2026-09'
    page.select_option('#yearFilter','2026');expect(page.locator('.blog-card:visible')).to_have_count(2)
    page.select_option('#sourceFilter','storymodelers');expect(page.locator('#noBlogResults')).to_be_visible()
    page.click('#resetFilters');expect(page.locator('.blog-card:visible')).to_have_count(11)
    page.goto(BASE+'resume.html')
    with page.expect_download() as download_info:page.locator('a[download]').click()
    assert Path(download_info.value.path()).read_bytes()[:5]==b'%PDF-'
    page.goto(BASE+'contact.html');page.click('#copyEmail');expect(page.locator('#emailStatus')).not_to_be_empty()
    # Content and navigation stay available when JavaScript is disabled.
    nojs=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
    nj=nojs.new_page();nj.goto(BASE+'publications.html')
    assert nj.locator('.publication-item:visible').count()==9
    expect(nj.locator('#mainNav')).to_be_visible()
    assert not errors,errors
    browser.close()
    server.shutdown()
    print('PASS: 8 pages × 5 widths, HTML standards mode, no overflow, local assets/links, image loading, active navigation, menu/Escape/focus, all filters/search/sorting/resets, citations/dialog/download, real PDF download, email copy fallback, no-JS content/navigation, and no JavaScript errors.')
