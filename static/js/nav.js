// Mobile menu: at 600px and below the nav links live in a dropdown opened by the
// "Menu" button. The button carries aria-expanded / aria-controls, Escape closes the
// menu and returns focus to the button, and picking a link or tapping outside closes it.
// Without JavaScript the button stays hidden and the links stay in the header.
(function () {
    var toggle = document.getElementById("nav-toggle");
    var panel = document.getElementById("nav-links");
    if (!toggle || !panel) return;

    function setOpen(open) {
        toggle.setAttribute("aria-expanded", open ? "true" : "false");
        panel.classList.toggle("is-open", open);
    }

    toggle.addEventListener("click", function () {
        setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });

    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
            setOpen(false);
            toggle.focus();
        }
    });

    document.addEventListener("click", function (e) {
        if (toggle.getAttribute("aria-expanded") !== "true") return;
        if (!panel.contains(e.target) && !toggle.contains(e.target)) setOpen(false);
    });

    panel.addEventListener("click", function (e) {
        if (e.target.closest && e.target.closest("a")) setOpen(false);
    });

    // Leaving the phone layout (rotate, resize) resets the state.
    window.matchMedia("(min-width: 601px)").addEventListener("change", function (e) {
        if (e.matches) setOpen(false);
    });
})();
