// Theme toggle: dark / light mode.
// aria-pressed is "true" while dark mode is on, so assistive tech announces
// "Toggle dark mode, toggle button, pressed" and the label never has to change.
(function () {
    const toggle = document.getElementById("theme-toggle");
    const root = document.documentElement;

    function currentTheme() {
        return root.getAttribute("data-theme") || "light";
    }

    function sync() {
        toggle.setAttribute("aria-pressed", currentTheme() === "dark" ? "true" : "false");
    }

    toggle.addEventListener("click", function () {
        const next = currentTheme() === "dark" ? "light" : "dark";
        root.setAttribute("data-theme", next);
        localStorage.setItem("theme", next);
        sync();
    });

    sync();
})();
