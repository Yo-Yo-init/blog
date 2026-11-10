// Client-side blog filtering for the static site.
// Handles /blog?q=<search or tag> and /blog?category=<slug>, which the
// FastAPI version did on the server.
(function () {
    var list = document.querySelector("[data-blog-list]");
    if (!list) return;

    var params = new URLSearchParams(window.location.search);
    var q = (params.get("q") || "").trim().toLowerCase();
    var category = (params.get("category") || "").trim().toLowerCase();

    var names = {};
    try {
        JSON.parse(document.getElementById("category-names").textContent).forEach(function (c) {
            names[c.slug] = c.name;
        });
    } catch (e) { /* no category names available */ }

    var cards = list.querySelectorAll("[data-post]");
    var shown = 0;
    cards.forEach(function (card) {
        var matchCat = !category || card.dataset.category === category;
        var matchQ = !q || (card.dataset.search || "").indexOf(q) !== -1;
        var visible = matchCat && matchQ;
        card.hidden = !visible;
        if (visible) shown++;
    });

    // Heading: category name when filtering by category.
    var heading = list.querySelector("[data-list-heading]");
    if (heading) {
        heading.textContent = category ? (names[category] || category) : heading.dataset.defaultHeading;
    }

    // Highlight the matching filter pill.
    list.querySelectorAll("[data-filter-q]").forEach(function (pill) {
        var active = category ? false : pill.dataset.filterQ.toLowerCase() === q;
        pill.classList.toggle("active", active);
    });

    // Empty states.
    if (shown === 0 && cards.length > 0) {
        if (category && !q) {
            var box = list.querySelector('[data-empty="category"]');
            box.querySelector("[data-empty-name]").textContent = names[category] || category;
            box.hidden = false;
        } else {
            list.querySelector('[data-empty="no-results"]').hidden = false;
        }
    }

})();
