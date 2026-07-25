// App Javascript - Baby Shower de Adhara

function toggleHamburger() {
    const overlay = document.getElementById("hamburger-overlay");
    const drawer = document.getElementById("hamburger-drawer");
    if (overlay && drawer) {
        const isClosed = drawer.classList.contains("-translate-x-full");
        if (isClosed) {
            // Open drawer
            drawer.classList.remove("-translate-x-full");
            overlay.classList.remove("pointer-events-none");
            overlay.classList.remove("opacity-0");
            overlay.classList.add("opacity-100");
        } else {
            // Close drawer
            drawer.classList.add("-translate-x-full");
            overlay.classList.add("pointer-events-none");
            overlay.classList.remove("opacity-100");
            overlay.classList.add("opacity-0");
        }
    }
}

// Close drawer on escape key
document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
        const drawer = document.getElementById("hamburger-drawer");
        if (drawer && !drawer.classList.contains("-translate-x-full")) {
            toggleHamburger();
        }
    }
});

// Scroll animations via Intersection Observer
document.addEventListener("DOMContentLoaded", function () {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.05,
        rootMargin: "0px 0px -30px 0px"
    });

    document.querySelectorAll(".fade-up-element").forEach(el => {
        observer.observe(el);
    });
});

// Parallax scroll effect for background floating watercolor elements
window.addEventListener("scroll", function () {
    const scrolled = window.scrollY;
    window.requestAnimationFrame(() => {
        document.querySelectorAll(".parallax-blob").forEach((blob) => {
            const speed = parseFloat(blob.getAttribute("data-speed") || "0.5");
            // Translate downwards to lag behind the viewport scroll direction
            blob.style.transform = `translateY(${scrolled * speed}px)`;
        });
    });
});
