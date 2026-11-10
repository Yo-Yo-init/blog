// Theme toggle — dark / light mode
(function () {
    const toggle = document.getElementById("theme-toggle");
    const root = document.documentElement;

    function currentTheme() {
        return root.getAttribute("data-theme") || "light";
    }

    toggle.addEventListener("click", function () {
        const next = currentTheme() === "dark" ? "light" : "dark";
        root.setAttribute("data-theme", next);
        localStorage.setItem("theme", next);
    });

    // ⌘K to focus search
    document.addEventListener("keydown", function (e) {
        if ((e.metaKey || e.ctrlKey) && e.key === "k") {
            e.preventDefault();
            var input = document.querySelector(".search-bar input");
            if (input) input.focus();
        }
    });
})();
