// --- DASHBOARD LOGIC ---

document.addEventListener('DOMContentLoaded', function () {
    // 1. Initialize Dashboard State from LocalStorage
    loadMissionData();

    // 2. Attach Event Listeners to all Checkboxes
    const checkboxes = document.querySelectorAll('.task-item input[type="checkbox"]');
    checkboxes.forEach(box => {
        box.addEventListener('change', function () {
            // Save state
            const weekId = this.closest('.week-section').id;
            saveMissionData(weekId);
            updateProgress(weekId);

            // Visual toggle
            if (this.checked) {
                this.parentElement.classList.add('completed');
            } else {
                this.parentElement.classList.remove('completed');
            }
        });
    });

    // 3. Attach Event Listeners to Notes
    const notes = document.querySelectorAll('.field-notes');
    notes.forEach(note => {
        note.addEventListener('input', function () {
            const weekId = this.closest('.week-section').id;
            saveMissionData(weekId);
        });
    });
});

function loadMissionData() {
    // Loop through each Week Section
    const weeks = document.querySelectorAll('.week-section');
    weeks.forEach(week => {
        const weekId = week.id;
        const savedData = JSON.parse(localStorage.getItem('eda_mission_' + weekId));

        if (savedData) {
            // Restore Checkboxes
            const boxes = week.querySelectorAll('input[type="checkbox"]');
            savedData.tasks.forEach((isChecked, index) => {
                if (boxes[index]) {
                    boxes[index].checked = isChecked;
                    if (isChecked) boxes[index].parentElement.classList.add('completed');
                }
            });

            // Restore Notes
            const noteArea = week.querySelector('.field-notes');
            if (noteArea && savedData.notes) {
                noteArea.value = savedData.notes;
            }

            // Update Progress Bar
            updateProgress(weekId);
        }
    });

    // Also open the first tab by default context
    // Defaulting to Overview if nothing else selected, handled by HTML default
}

function saveMissionData(weekId) {
    const weekSection = document.getElementById(weekId);
    if (!weekSection) return;

    const boxes = weekSection.querySelectorAll('input[type="checkbox"]');
    const taskStates = Array.from(boxes).map(box => box.checked);

    const noteArea = weekSection.querySelector('.field-notes');
    const notes = noteArea ? noteArea.value : "";

    const data = {
        tasks: taskStates,
        notes: notes
    };

    localStorage.setItem('eda_mission_' + weekId, JSON.stringify(data));
}

function updateProgress(weekId) {
    const weekSection = document.getElementById(weekId);
    if (!weekSection) return;

    const boxes = weekSection.querySelectorAll('input[type="checkbox"]');
    const checked = weekSection.querySelectorAll('input[type="checkbox"]:checked');

    const total = boxes.length;
    if (total === 0) return;

    const percent = Math.round((checked.length / total) * 100);

    // Find progress bar in this section
    const bar = weekSection.querySelector('.progress-bar');
    if (bar) {
        bar.style.width = percent + "%";
        bar.textContent = percent + "% COMMS"; // Military styling

        // Color coding
        if (percent < 30) bar.style.backgroundColor = "var(--accent-red)";
        else if (percent < 70) bar.style.backgroundColor = "var(--accent-gold)";
        else bar.style.backgroundColor = "var(--accent-green)";
    }
}
