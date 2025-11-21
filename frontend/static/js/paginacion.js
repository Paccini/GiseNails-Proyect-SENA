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

        document.querySelectorAll('.page-link').forEach(l => {
            l.style.cursor = 'pointer';
            if (!l.hasAttribute('tabindex')) l.setAttribute('tabindex', '0');
        });
    }

    async function fetchAndReplace(href, push = true) {
        try {
            const res = await fetch(href, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
            const text = await res.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(text, 'text/html');

            // 🔥 SIEMPRE reemplazar cards
            const newCards = doc.querySelector('.cards');
            const oldCards = document.querySelector('.cards');
            if (newCards && oldCards) oldCards.replaceWith(newCards);

            // 🔥 SIEMPRE reemplazar paginación (este era el problema)
            const newPag = doc.querySelector('.pagination-wrapper, .animated-paginator, nav[aria-label="Page navigation"], .pagination');
            const oldPag = document.querySelector('.pagination-wrapper, .animated-paginator, nav[aria-label="Page navigation"], .pagination');
            if (newPag && oldPag) oldPag.replaceWith(newPag);

            if (push) history.pushState({ ajax: true }, '', href);

            initDynamicBehaviors();

        } catch (err) {
            console.error('AJAX pagination error, fallback full load', err);
            window.location.href = href;
        }
    }

    document.addEventListener('click', function (e) {
        const link = e.target.closest('.page-link');
        if (!link) return;

        const href = link.getAttribute('href');
        if (!href || href === '#') return;

        e.preventDefault();
        fetchAndReplace(href, true);
    });

    window.addEventListener('popstate', function () {
        fetchAndReplace(location.href, false);
    });

    document.addEventListener('DOMContentLoaded', function () {
        initDynamicBehaviors();
    });
})();
