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



//tracker

// tracker_script.js
const runItems = document.getElementById('run-items').querySelectorAll('li');
let selectedWeeks = [];

runItems.forEach(item => {
    item.addEventListener('click', () => {
        const week = item.dataset.week;
        if (selectedWeeks.includes(week)) {
            selectedWeeks = selectedWeeks.filter(w => w !== week);
            item.classList.remove('selected');
        } else {
            selectedWeeks.push(week);
            item.classList.add('selected');
        }
        sendSelectedRuns(selectedWeeks); // Send data to Flask
    });
});

function sendSelectedRuns(selectedWeeks) {
    fetch('/save_selected_runs', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ selectedWeeks: selectedWeeks }),
    })
    .then(response => response.json())
    .then(data => console.log(data));
}

window.addEventListener('load', function() {
    // Get the user's runs from the HTML and mark them as selected.
    let userRunsIds = JSON.parse(document.getElementById('user_runs_ids').textContent);
    runItems.forEach(item => {
        if(userRunsIds.includes(parseInt(item.dataset.runId))){
            item.classList.add('selected');
            selectedWeeks.push(item.dataset.week);
        }
    });
});