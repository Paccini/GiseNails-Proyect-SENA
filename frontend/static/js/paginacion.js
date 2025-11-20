// Código de paginación AJAX (reemplaza / pega entero en ese archivo)
(function () {
    if (window.__ajaxPaginatorInit) return;
    window.__ajaxPaginatorInit = true;

    function initDynamicBehaviors() {
        try {
            const obs = new IntersectionObserver((entries, o) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const el = entry.target;
                        const delay = parseFloat(el.getAttribute('data-delay') || 0);
                        if (delay > 0) setTimeout(() => el.classList.add('visible'), Math.round(delay * 1000));
                        else el.classList.add('visible');
                        o.unobserve(el);
                    }
                });
            }, { threshold: 0.15 });
            document.querySelectorAll('.scroll-fade').forEach(el => obs.observe(el));
        } catch (e) { console.warn('Observer init failed', e); }
        document.querySelectorAll('.animated-paginator .page-link').forEach(l => {
            l.style.cursor = 'pointer';
            if (!l.hasAttribute('tabindex')) l.setAttribute('tabindex', '0');
        });
    }

    async function fetchAndReplace(href, push = true) {
        showLoader();
        try {
            const res = await fetch(href, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
            const text = await res.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(text, 'text/html');

            const newCards = doc.querySelector('.cards');
            const oldCards = document.querySelector('.cards');
            if (newCards && oldCards) oldCards.replaceWith(newCards);

            const newPag = doc.querySelector('.animated-paginator');
            const oldPag = document.querySelector('.animated-paginator');
            if (newPag && oldPag) oldPag.replaceWith(newPag);

            const newPagWrapper = doc.querySelector('.pagination-wrapper');
            const oldPagWrapper = document.querySelector('.pagination-wrapper');
            if (newPagWrapper && oldPagWrapper) oldPagWrapper.replaceWith(newPagWrapper);

            const newTitle = doc.querySelector('title');
            if (newTitle) document.title = newTitle.textContent;

            if (push) history.pushState({ ajax: true }, '', href);

            initDynamicBehaviors();
            document.dispatchEvent(new CustomEvent('content:updated', { detail: { url: href } }));
        } catch (err) {
            console.error('AJAX pagination error, fallback full load', err);
            window.location.href = href;
        } finally { hideLoader(); }
    }

    function showLoader() {
        // if paginator present, show small inline loader next to it
        const pagWrapper = document.querySelector('.pagination-wrapper') || document.querySelector('.d-flex.justify-content-center');
        if (pagWrapper) {
            // avoid duplicate
            if (!pagWrapper.querySelector('.ajax-inline-loader')) {
                const loader = document.createElement('div');
                loader.className = 'ajax-inline-loader';
                loader.innerHTML = '<div class="spinner-border text-primary" role="status" aria-hidden="true"></div>';
                loader.style.marginLeft = '12px';
                pagWrapper.appendChild(loader);
            }
            // soft page fade (CSS handles actual opacity)
            document.body.classList.add('pag-navigating');
            // Also ensure cards are slightly dimmed
            const cards = document.querySelector('.cards');
            if (cards) cards.style.filter = 'brightness(0.85) saturate(0.9)';
            return;
        }

        // fallback: full-screen overlay only if paginator not found
        if (document.getElementById('ajaxLoader')) return;
        const overlay = document.createElement('div');
        overlay.id = 'ajaxLoader';
        overlay.style.cssText = 'position:fixed;inset:0;background:rgba(255,255,255,0.65);display:flex;align-items:center;justify-content:center;z-index:9999';
        overlay.innerHTML = '<div class="spinner-border text-primary" role="status" aria-hidden="true"></div>';
        document.body.appendChild(overlay);
    }

    function hideLoader() {
        // remove inline loader if present
        const inline = document.querySelector('.ajax-inline-loader');
        if (inline && inline.parentNode) inline.parentNode.removeChild(inline);
        // remove overlay fallback if present
        const l = document.getElementById('ajaxLoader');
        if (l) l.remove();
        // remove paginating class and reset dim
        document.body.classList.remove('pag-navigating');
        const cards = document.querySelector('.cards');
        if (cards) cards.style.filter = '';
    }

    document.addEventListener('click', function (e) {
        const link = e.target.closest('.animated-paginator .page-link');
        if (!link) return;
        const href = link.getAttribute('href');
        if (!href || href === '#') return;
        if (link.dataset.noAjax === 'true') return;
        e.preventDefault();
        fetchAndReplace(href, true);
    });

    document.addEventListener('keydown', function (e) {
        if (e.key !== 'Enter' && e.key !== ' ') return;
        const el = document.activeElement;
        if (!el) return;
        if (el.matches && el.matches('.animated-paginator .page-link')) {
            const href = el.getAttribute('href');
            if (!href || href === '#') return;
            if (el.dataset.noAjax === 'true') return;
            e.preventDefault();
            fetchAndReplace(href, true);
        }
    });

    window.addEventListener('popstate', function () { fetchAndReplace(location.href, false); });

    document.addEventListener('DOMContentLoaded', function () { initDynamicBehaviors(); });
})();