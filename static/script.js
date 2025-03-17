document.addEventListener("DOMContentLoaded", function () {
    const links = document.querySelectorAll("a");

    links.forEach(link => {
        link.addEventListener("click", function (event) {
            // Ignore external links
            if (!this.href.startsWith(window.location.origin)) return;

            event.preventDefault(); // Stop default navigation
            const targetUrl = this.href;

            // Prevent multiple animations on the same click
            if (!document.body.classList.contains("fade-out")) {
                document.body.classList.add("fade-out");

                setTimeout(() => {
                    window.location.href = targetUrl;
                }, 500); // Match the CSS animation duration
            }
        }, { once: true }); // <-- Fix: Prevent multiple event bindings
    });
});

// Add fade-out keyframe only once
if (!document.head.querySelector("#fade-out-style")) {
    const style = document.createElement("style");
    style.id = "fade-out-style";
    style.innerHTML = `
        @keyframes fadeOut {
            from { opacity: 1; }
            to { opacity: 0; }
        }
        .fade-out {
            animation: fadeOut 0.5s ease-in-out;
        }
    `;
    document.head.appendChild(style);
}

window.addEventListener('load', function() {
    document.body.classList.remove('fade-out');
});
