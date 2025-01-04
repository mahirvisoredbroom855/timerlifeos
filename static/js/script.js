document.addEventListener('DOMContentLoaded', () => {
    const taskInput = document.getElementById('task-input');
    const addTaskBtn = document.getElementById('add-task-btn');
    const removeTaskBtn = document.getElementById('remove-task-btn');
    const taskList = document.getElementById('task-list');
    const startTimerBtn = document.getElementById('start-timer-btn');
    const stopTimerBtn = document.getElementById('stop-timer-btn');
    const viewRecordsBtn = document.getElementById('view-records-btn');
    const exportRecordsBtn = document.getElementById('export-records-btn');
    const exportPeriod = document.getElementById('export-period');
    const recordsList = document.getElementById('records-list');

    let selectedTask = null;

    // Load tasks from server
    function loadTasks() {
        fetch('/')
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const tasksFromServer = Array.from(doc.querySelectorAll('#task-list li')).map(li => li.textContent);

                taskList.innerHTML = '';
                tasksFromServer.forEach(task => {
                    const li = document.createElement('li');
                    li.textContent = task;
                    li.addEventListener('click', () => selectTask(li));
                    taskList.appendChild(li);
                });
            })
            .catch(error => console.error('Error loading tasks:', error));
    }

    // Select a task
    function selectTask(taskElement) {
        if (selectedTask) selectedTask.classList.remove('selected');
        selectedTask = taskElement;
        selectedTask.classList.add('selected');
        removeTaskBtn.disabled = false;
    }

    // Add a new task
    addTaskBtn.addEventListener('click', () => {
        const taskName = taskInput.value.trim();
        if (!taskName) {
            alert('Task name cannot be empty!');
            return;
        }

        fetch('/add_task', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task: taskName }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    loadTasks();
                    taskInput.value = '';
                } else {
                    alert(data.error);
                }
            })
            .catch(error => console.error('Error adding task:', error));
    });

    // Remove a task
    removeTaskBtn.addEventListener('click', () => {
        if (!selectedTask) {
            alert('No task selected to remove!');
            return;
        }

        const taskName = selectedTask.textContent;

        fetch('/remove_task', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task: taskName }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    loadTasks();
                    removeTaskBtn.disabled = true;
                } else {
                    alert(data.error);
                }
            })
            .catch(error => console.error('Error removing task:', error));
    });

    // Start timer
    startTimerBtn.addEventListener('click', () => {
        if (!selectedTask) {
            alert('Please select a task to start the timer.');
            return;
        }

        const taskName = selectedTask.textContent;

        fetch('/start_timer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task: taskName }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    alert(data.message);
                } else {
                    alert(data.error);
                }
            })
            .catch(error => console.error('Error starting timer:', error));
    });

    // Stop timer
    stopTimerBtn.addEventListener('click', () => {
        fetch('/stop_timer', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                alert(data.message || data.error);
            })
            .catch(error => console.error('Error stopping timer:', error));
    });

    // View records
    viewRecordsBtn.addEventListener('click', () => {
        fetch('/view_records')
            .then(response => response.json())
            .then(data => {
                recordsList.innerHTML = '';
                data.forEach(record => {
                    const li = document.createElement('li');
                    li.textContent = `${record.task} - ${record.date} (${record.begin} to ${record.end})`;
                    recordsList.appendChild(li);
                });
            })
            .catch(error => console.error('Error viewing records:', error));
    });

    // Export records
    exportRecordsBtn.addEventListener('click', () => {
        const period = exportPeriod.value;

        fetch('/export_records', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ period }),
        })
            .then(response => {
                if (response.ok) {
                    return response.blob();
                } else {
                    return response.json().then(data => {
                        throw new Error(data.error);
                    });
                }
            })
            .then(blob => {
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'exported_records.json';
                document.body.appendChild(a);
                a.click();
                a.remove();
            })
            .catch(error => alert(error.message));
    });

    // Initialize
    loadTasks();
});
