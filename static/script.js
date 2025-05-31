const calendar = document.getElementById("calendar");
const moodPopup = document.getElementById("moodPopup");
const moodSelect = document.getElementById("moodSelect");
const monthYear = document.getElementById("monthYear");
let selectedDay;
let currentDate = new Date();

const moodCount = {
    "😊 Happy": 0,
    "😢 Sad": 0,
    "😴 Tired": 0,
    "🤩 Excited": 0,
    "😟 Stressed": 0,
    "😡 Angry": 0,
    "🙄 Annoyed": 0
};

let moodChart;

function generateCalendar() {
    calendar.innerHTML = "";
    const month = currentDate.getMonth();
    const year = currentDate.getFullYear();
    monthYear.textContent = new Date(year, month).toLocaleString('default', { month: 'long', year: 'numeric' });

    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    
    const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    weekdays.forEach(day => {
        let weekdayDiv = document.createElement("div");
        weekdayDiv.className = "weekday";
        weekdayDiv.textContent = day;
        calendar.appendChild(weekdayDiv);
    });

    for (let i = 0; i < firstDay; i++) {
        let emptyDiv = document.createElement("div");
        emptyDiv.className = "day";
        calendar.appendChild(emptyDiv);
    }
    
    for (let i = 1; i <= daysInMonth; i++) {
        let dayDiv = document.createElement("div");
        dayDiv.className = "day";
        dayDiv.textContent = i;
        dayDiv.onclick = () => openMoodPopup(i);
        calendar.appendChild(dayDiv);
    }

    fetchMoods();
}

function openMoodPopup(day) {
    selectedDay = day;
    moodPopup.style.display = "block";
}

function saveMood() {
    const mood = moodSelect.value;
    const dateKey = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}-${String(selectedDay).padStart(2, '0')}`;

    fetch('/save_mood', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ date: dateKey, mood: mood })
    }).then(() => {
        moodPopup.style.display = "none";
        generateCalendar();
    });
}

function fetchMoods() {
    fetch('/get_moods')
        .then(response => response.json())
        .then(data => {
            Object.keys(moodCount).forEach(mood => moodCount[mood] = 0); // Reset

            Object.entries(data).forEach(([date, mood]) => {
                const moodDate = new Date(date);
                if (moodDate.getMonth() === currentDate.getMonth()) {
                    const day = moodDate.getDate();
                    const moodText = `${day} ${mood}`;
                    const index = day + new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay() - 1;
                    const dayElement = document.querySelectorAll(".day")[index];
                    if (dayElement) dayElement.textContent = moodText;

                    if (mood in moodCount) moodCount[mood]++;
                }
            });

            updateMoodChart();
        });
}

function updateMoodChart() {
    const labels = Object.keys(moodCount);
    const data = Object.values(moodCount);

    if (moodChart) moodChart.destroy(); // Reset if already created

    const ctx = document.getElementById('moodChart').getContext('2d');
    moodChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Mood Frequency',
                data: data,
                backgroundColor: ['#f9d923', '#ff6b6b', '#a29bfe', '#55efc4', '#cd87ff', '#f6a7f5', '#a9e39c']
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    precision: 0
                }
            }
        }
    });
}

generateCalendar();
