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
    });
});