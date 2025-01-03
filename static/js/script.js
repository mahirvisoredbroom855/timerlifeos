document.addEventListener('DOMContentLoaded', () => {
    const taskInput = document.getElementById('task-input');
    const addTaskBtn = document.getElementById('add-task-btn');
    const taskList = document.getElementById('task-list');
    const startTimerBtn = document.getElementById('start-timer-btn');
    const stopTimerBtn = document.getElementById('stop-timer-btn');
    const viewRecordsBtn = document.getElementById('view-records-btn');
    const exportRecordsBtn = document.getElementById('export-records-btn');
    const recordsList = document.getElementById('records-list');
    const exportPeriod = document.getElementById('export-period');
    const removeTaskBtn = document.getElementById('remove-task-btn');

    // Fetch tasks and populate the task list
    // Fetch tasks and populate the task list
    function loadTasks() {
        fetch('/')
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const tasksFromServer = Array.from(doc.querySelectorAll('#task-list li'))
                    .map(li => li.textContent);

                // Clear existing tasks and populate the list
                taskList.innerHTML = '';
                tasksFromServer.forEach(task => {
                    const li = document.createElement('li');
                    li.textContent = task;

                    // Add selection behavior
                    li.addEventListener('click', () => {
                        document.querySelectorAll('#task-list li').forEach(el => el.classList.remove('selected'));
                        li.classList.add('selected');
                    });

                    taskList.appendChild(li);
                });
            })
            .catch(error => console.error('Error loading tasks:', error));
    }


    

    function addTask(taskName) {
        fetch('/add_task', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task: taskName })
        })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    loadTasks();
                    document.getElementById('task-input').value = '';
                } else {
                    alert(data.error);
                }
            });
    }
    
    function viewRecords() {
        fetch('/view_records')
            .then(response => response.json())
            .then(data => {
                const recordsList = document.getElementById('records-list');
                recordsList.innerHTML = ''; // Clear records list
                data.forEach(record => {
                    const li = document.createElement('li');
                    li.textContent = `${record.task} - ${record.date} (${record.begin} to ${record.end})`;
                    recordsList.appendChild(li);
                });
            });
    }


    document.getElementById('add-task-btn').addEventListener('click', () => {
        const taskInput = document.getElementById('task-input').value;
        if (taskInput) addTask(taskInput);
    });
    
    document.getElementById('view-records-btn').addEventListener('click', viewRecords);

    // Add a new task
    // Add task event
    addTaskBtn.addEventListener('click', () => {
        const taskName = taskInput.value.trim(); // Normalize input
        if (!taskName) {
            alert('Task name cannot be empty!');
            return;
        }

        fetch('/add_task', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task: taskName })
        })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    loadTasks(); // Reload tasks
                    taskInput.value = ''; // Clear input field
                } else {
                    alert(data.error);
                }
            })
            .catch(error => console.error('Error adding task:', error));

            console.log('Add Task button clicked');
    });



    // Remove task event
    removeTaskBtn.addEventListener('click', () => {
        const selectedTask = document.querySelector('#task-list li.selected');
        if (!selectedTask) {
            alert('No task selected to remove!');
            return;
        }
    
        const taskName = selectedTask.textContent;
    
        fetch('/remove_task', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task: taskName })
        })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    loadTasks(); // Reload tasks
                    removeTaskBtn.disabled = true; // Disable remove button
                } else {
                    alert(data.error);
                }
            })
            .catch(error => console.error('Error removing task:', error));
    });


    // Start timer
    startTimerBtn.addEventListener('click', () => {
        const selectedTask = document.querySelector('#task-list li.selected');
        if (!selectedTask) {
            alert('Please select a task to start the timer.');
            return;
        }

        const taskName = selectedTask.textContent;

        fetch('/start_timer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task: taskName })
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
            });
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
            });
    });

    // Export records
    exportRecordsBtn.addEventListener('click', () => {
        const period = exportPeriod.value;

        fetch('/export_records', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ period })
        })
            .then(response => {
                if (response.ok) {
                    return response.blob();
                } else {
                    return response.json().then(data => { throw new Error(data.error); });
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

    // Task selection
    taskList.addEventListener('click', event => {
        const items = document.querySelectorAll('#task-list li');
        items.forEach(item => item.classList.remove('selected'));
        event.target.classList.add('selected');
    });

    // Initialize tasks
    loadTasks();
});
