# Editorial redesign

## Direction

The user-provided publications-page reference informed the serif headlines,
muted forest-green accents, pale backgrounds, landscape masthead, restrained
topic tags, compact thumbnails, and separate bibliography action column.
Home and About use profile 3 in an oval frame, without zoom or image cropping.
Contact and social profile links sit below the portrait caption, as requested.
The original photograph remains unchanged.

All pages share a single layout template and one stylesheet. Content is static
HTML; JavaScript enhances navigation and filtering. Local system serif/sans-serif
stacks eliminate font downloads and keep the site readable offline.

## Information architecture

- Home: introduction, portrait, research interests, selected work, selected writing.
- About: profile, education, research experience, methods, activities, awards.
- Research (`projects.html`): seven research areas from the supplied CV.
- Publications: nine contributions; topic, year, type, text-search, and sort controls.
- Teaching: the two retained teaching appointments and two invited 2026 workshops.
- Blog (`blogs.html`): all eleven existing posts, newest first, with original filters.
- Contact: legacy route retained for compatibility, omitted from navigation.
  Email and social links are now provided beneath the Home and About portraits.
- CV (`resume.html`): original PDF preview, open, and download actions.

Original page routes and external links are retained. The old About teaching
anchor remains available, with a link to the full Teaching page.

## Content provenance

The user confirmed `Botello_Jhon_Curriculum_Vitae_Es.docx` as the content source.
No separate Spanish website was needed. Biographical additions are translations
or concise summaries of that CV; research-area headings are organizational labels,
not invented named projects. New Contact information and ORCID come from the CV,
including its document hyperlinks. Technical reporting and the VMware information
retrieval activity complete omissions from the first redesign.

Existing publication summaries, papers, blog posts, authors, and outbound URLs
are preserved. The only added direct paper PDF link uses the supplied arXiv
identifier, 2606.30846. No unavailable manuscript PDFs are implied. Citations are
plain-text exports of the same bibliography, not independently verified BibTeX.
The existing downloadable resume PDF is unchanged and may be older than the CV.

The Ottoman census author list remains as supplied, including its incomplete
first “Frydenlund” entry. Editorial correction needs the author's confirmation.
Two CV-supplied Blogspot links could not be verified by the external browsing tool
in the earlier pass; both remain as provided. Preserving URLs does not guarantee
that third-party websites will be reachable at all times.

## Images

`images/Profile/profile3.jpeg` is used on Home and About. Existing article images
are retained. Publication photos and small conceptual SVGs are decorative research
context, not reproductions of figures from the papers. The landscape masthead is
generated decorative artwork, not claimed as a photograph from the author's travels
or fieldwork. See `images/editorial/README.md` for its prompt and provenance.

## Accessibility and verification

- A single h1 and main landmark on each page; labelled navigation and form controls.
- Skip link, visible keyboard focus, current-page markers, reduced-motion support.
- Native citation dialog supports Escape, focus return, text selection, and download.
- Mobile menu exposes expanded state, supports Escape, and restores button focus.
- Clipboard failure gives a manual-copy fallback rather than a false success message.
- Site content and navigation remain available without JavaScript.
- Shared text/background color pairs pass 4.5:1 contrast checks.
- HTML nesting, duplicate IDs, local paths, fragments, labels, assets, and PDF integrity
  are checked by `tools/validate_site.py`.
- Chromium checks cover eight pages at 1440, 1024, 768, 390, and 320 px, including
  overflow, image loading, navigation, combined filters, reset/empty states, search,
  sorting, citation export, resume PDF download, and JavaScript errors.

The site has no framework compilation step; `tools/build_site.py --check` verifies
that all generated pages match the editable templates and data.

## Requested content adjustments

The Unicafam teaching appointment and its associated graduate courses are omitted
at the user’s request. Teaching summaries refer to the two remaining institutions.
The header reads “AI, M&S and Digital libraries”; the homepage eyebrow reads
“AI · Modeling & simulation · Digital Libraries”.
