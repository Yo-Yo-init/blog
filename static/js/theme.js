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
})();
