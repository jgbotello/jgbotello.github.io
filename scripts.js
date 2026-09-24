/* Progressive enhancement: the content and links work without JavaScript. */
(() => {
  'use strict';

  document.documentElement.classList.add('js');
  const menuButton = document.querySelector('.menu-toggle');
  const navigation = document.getElementById('mainNav');
  const compactNavigation = window.matchMedia('(max-width: 850px)');

  function closeMenu(restoreFocus = false) {
    if (!menuButton || !navigation) return;
    navigation.classList.remove('is-open');
    menuButton.setAttribute('aria-expanded', 'false');
    if (restoreFocus && compactNavigation.matches) menuButton.focus();
  }

  if (menuButton && navigation) {
    menuButton.hidden = false;
    menuButton.addEventListener('click', () => {
      const open = menuButton.getAttribute('aria-expanded') !== 'true';
      menuButton.setAttribute('aria-expanded', String(open));
      navigation.classList.toggle('is-open', open);
    });
    navigation.addEventListener('click', (event) => {
      if (event.target.closest('a')) closeMenu();
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && menuButton.getAttribute('aria-expanded') === 'true') closeMenu(true);
    });
    document.addEventListener('click', (event) => {
      if (!event.target.closest('.nav-shell')) closeMenu();
    });
    compactNavigation.addEventListener('change', () => closeMenu());
  }

  // Copy failures retain a clear manual fallback instead of reporting success.
  async function copyText(text, status, fallback) {
    try {
      if (!navigator.clipboard) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(text);
      status.textContent = 'Copied to clipboard.';
    } catch {
      if (fallback) {
        fallback.focus();
        fallback.select();
      }
      status.textContent = 'Please select and copy the text manually.';
    }
  }

  const publicationForm = document.getElementById('publicationFilters');
  if (publicationForm) {
    const grid = document.getElementById('publicationsGrid');
    const papers = Array.from(grid.querySelectorAll('.publication-item'));
    const search = document.getElementById('publicationSearch');
    const year = document.getElementById('yearFilter');
    const type = document.getElementById('typeFilter');
    const sort = document.getElementById('publicationSort');
    const result = document.getElementById('resultsCount');
    const empty = document.getElementById('noResultsMessage');
    const topicButtons = document.querySelectorAll('[data-topic-filter]');
    const normalize = (value) => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
    const searchable = new Map(papers.map((paper) => [paper, normalize(paper.querySelector('.publication-content').textContent)]));
    let selectedTopic = 'all';

    function filterPublications() {
      const terms = normalize(search.value.trim()).split(/\s+/).filter(Boolean);
      let count = 0;
      const yearValue = (paper) => paper.dataset.year === 'in-press' ? 9999 : Number(paper.dataset.year);
      const direction = sort.value === 'oldest' ? 1 : -1;
      [...papers].sort((a, b) => direction * (yearValue(a) - yearValue(b))).forEach((paper) => grid.appendChild(paper));
      papers.forEach((paper) => {
        const matches = (year.value === 'all' || paper.dataset.year === year.value)
          && (type.value === 'all' || paper.dataset.type === type.value)
          && (selectedTopic === 'all' || paper.dataset.topics.split(' ').includes(selectedTopic))
          && terms.every((term) => searchable.get(paper).includes(term));
        paper.hidden = !matches;
        if (matches) count += 1;
      });
      empty.hidden = count !== 0;
      result.textContent = `Showing ${count} of ${papers.length} publications`;
    }

    function resetPublications() {
      selectedTopic = 'all';
      topicButtons.forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.topicFilter === 'all')));
      // The reset event is dispatched before native form values are restored.
      setTimeout(filterPublications, 0);
    }

    topicButtons.forEach((button) => button.addEventListener('click', () => {
      selectedTopic = button.dataset.topicFilter;
      topicButtons.forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
      filterPublications();
    }));
    publicationForm.addEventListener('submit', (event) => event.preventDefault());
    publicationForm.addEventListener('input', filterPublications);
    publicationForm.addEventListener('change', filterPublications);
    publicationForm.addEventListener('reset', resetPublications);
    document.querySelector('[data-reset-publications]').addEventListener('click', () => {
      publicationForm.reset();
      search.focus();
    });
    filterPublications();
  }

  const blogForm = document.getElementById('blogFilters');
  if (blogForm) {
    const posts = Array.from(document.querySelectorAll('#blogsGrid .blog-card'));
    const controls = [['sourceFilter', 'source'], ['yearFilter', 'year'], ['topicFilter', 'topic']];
    function filterBlogs() {
      let count = 0;
      posts.forEach((post) => {
        const matches = controls.every(([id, key]) => {
          const value = document.getElementById(id).value;
          return value === 'all' || post.dataset[key] === value;
        });
        post.hidden = !matches;
        if (matches) count += 1;
      });
      document.getElementById('blogResultsCount').textContent = `Showing ${count} of ${posts.length} blog posts`;
      document.getElementById('noBlogResults').hidden = count !== 0;
    }
    blogForm.addEventListener('submit', (event) => event.preventDefault());
    blogForm.addEventListener('change', filterBlogs);
    blogForm.addEventListener('reset', () => setTimeout(filterBlogs, 0));
    document.querySelector('[data-reset-blogs]').addEventListener('click', () => {
      blogForm.reset();
      document.getElementById('sourceFilter').focus();
    });
    filterBlogs();
  }

  const citationDialog = document.getElementById('citationDialog');
  if (citationDialog && typeof citationDialog.showModal === 'function') {
    const text = document.getElementById('citationText');
    const status = document.getElementById('citationStatus');
    let opener = null;
    document.querySelectorAll('[data-citation]').forEach((button) => {
      button.hidden = false;
      button.addEventListener('click', () => {
        opener = button;
        text.value = button.dataset.citation;
        status.textContent = '';
        citationDialog.showModal();
      });
    });
    citationDialog.querySelector('.dialog-close').addEventListener('click', () => citationDialog.close());
    citationDialog.addEventListener('close', () => opener?.focus());
    citationDialog.addEventListener('click', (event) => {
      const bounds = citationDialog.getBoundingClientRect();
      if (event.target === citationDialog && (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom)) citationDialog.close();
    });
    document.getElementById('copyCitation').addEventListener('click', () => copyText(text.value, status, text));
    document.getElementById('downloadCitation').addEventListener('click', () => {
      const url = URL.createObjectURL(new Blob([text.value + '\n'], { type: 'text/plain;charset=utf-8' }));
      const link = document.createElement('a');
      link.href = url;
      link.download = 'botello-citation.txt';
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    });
  }

  const emailButton = document.getElementById('copyEmail');
  if (emailButton) emailButton.addEventListener('click', () => copyText('jhongbm.12.jgbm@gmail.com', document.getElementById('emailStatus')));
})();
