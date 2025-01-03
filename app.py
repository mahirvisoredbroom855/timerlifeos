from flask import Flask, render_template, request, jsonify, send_file
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# File paths
data_file = "tasks_data.json"
records_file = "records_data.json"

# Load tasks and records
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return []

def save_data(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

tasks = load_data(data_file)
records = load_data(records_file)

@app.route('/')
def home():
    print(tasks)  # Debug
    return render_template('index.html', tasks=tasks)



@app.route('/add_task', methods=['POST'])
def add_task():
    global tasks
    # Reload tasks to ensure the latest state
    tasks = load_data(data_file)

    task_name = request.json.get('task')

    # Validate input
    if not task_name or not task_name.strip():  # Empty or whitespace-only task name
        return jsonify({"error": "Task name cannot be empty."}), 400

    # Normalize task name for consistent comparison
    normalized_task_name = task_name.strip().lower()

    # Ensure tasks are normalized for comparison
    normalized_tasks = [task.strip().lower() for task in tasks]

    # Debugging logs
    print(f"Task to add (normalized): '{normalized_task_name}'")
    print(f"Existing tasks (normalized): {normalized_tasks}")

    # Check for duplicates
    if normalized_task_name in normalized_tasks:
        print("Duplicate detected!")
        return jsonify({"error": "Task already exists."}), 400

    # Add the task if no duplicates are found
    tasks.append(task_name.strip())
    save_data(data_file, tasks)
    print(f"Task '{task_name}' added successfully!")
    return jsonify({"message": "Task added successfully!", "tasks": tasks})





@app.route('/view_records', methods=['GET'])
def view_records():
    return jsonify(records)

@app.route('/alternative_records', methods=['GET'])
def alternative_view_records():
    return jsonify({"message": "This is an alternative view of records.", "records": records})

@app.route('/start_timer', methods=['POST'])
def start_timer():
    global current_task, start_time
    task_name = request.json.get('task')
    if task_name in tasks:
        current_task = task_name
        start_time = datetime.now()
        return jsonify({"message": f"Timer started for task: {current_task}"})
    return jsonify({"error": "Invalid task selected."}), 400



@app.route('/stop_timer', methods=['POST'])
def stop_timer():
    global current_task, start_time
    if not current_task or not start_time:
        return jsonify({"error": "No task is currently being timed."}), 400

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    record = {
        "task": current_task,
        "date": start_time.strftime("%Y-%m-%d"),
        "begin": start_time.strftime("%I:%M %p"),
        "end": end_time.strftime("%I:%M %p"),
        "duration": str(timedelta(seconds=duration)),
        "duration_decimal": round(duration / 3600, 2)
    }

    records.append(record)
    save_data(records_file, records)
    current_task, start_time = None, None
    return jsonify({"message": "Timer stopped and data recorded!", "records": records})

@app.route('/export_records', methods=['POST'])
def export_records():
    period = request.form.get('period')
    if period == "week":
        start_date = datetime.now() - timedelta(days=7)
    elif period == "month":
        start_date = datetime.now() - timedelta(days=30)
    else:
        start_date = datetime.min

    filtered_records = [
        record for record in records
        if datetime.strptime(record["date"], "%Y-%m-%d") >= start_date
    ]

    export_file = "exported_records.json"
    with open(export_file, "w") as f:
        json.dump(filtered_records, f, indent=4)

    return send_file(export_file, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
