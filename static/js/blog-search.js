// Free-text search for the post lists (/blog/, tag and category pages).
// Filters the cards already on the page by title, summary and tags, keeps the
// query in the URL as ?q=<text> and reads it back on load. A ?q= value that is
// exactly a tag slug is redirected to its tag page by src/worker.js before this
// script ever runs; any other text is handled here.
(function () {
    var form = document.getElementById("blog-search");
    var input = document.getElementById("blog-search-input");
    var status = document.getElementById("blog-search-status");
    if (!form || !input) return;

    var cards = Array.prototype.slice.call(document.querySelectorAll(".post-card[data-search]"));
    var groups = Array.prototype.slice.call(document.querySelectorAll(".year-group"));
    var empty = document.getElementById("blog-search-empty");

    function apply(query, updateUrl) {
        var terms = query.toLowerCase().split(/\s+/).filter(Boolean);
        var shown = 0;
        cards.forEach(function (card) {
            var hay = card.getAttribute("data-search");
            var match = terms.every(function (t) { return hay.indexOf(t) !== -1; });
            card.hidden = !match;
            if (match) shown++;
        });
        groups.forEach(function (g) {
            g.hidden = !g.querySelector(".post-card:not([hidden])");
        });
        if (empty) empty.hidden = shown !== 0;
        if (status) {
            status.textContent = terms.length
                ? shown + (shown === 1 ? " post matches" : " posts match") + " \u201c" + query.trim() + "\u201d"
                : "";
        }
        if (updateUrl) {
            var url = new URL(window.location.href);
            if (terms.length) url.searchParams.set("q", query.trim());
            else url.searchParams.delete("q");
            history.replaceState(null, "", url.pathname + url.search + url.hash);
        }
    }

    input.addEventListener("input", function () { apply(input.value, true); });
    form.addEventListener("submit", function (e) {
        e.preventDefault();
        apply(input.value, true);
    });
    form.addEventListener("reset", function () {
        // Let the browser clear the field first, then refresh the list.
        setTimeout(function () { apply("", true); input.focus(); }, 0);
    });

    var initial = new URLSearchParams(window.location.search).get("q");
    if (initial) {
        input.value = initial;
        apply(initial, false);
    }
})();
