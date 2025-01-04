from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
import json
import os
from datetime import datetime, timedelta



app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session handling

# Hardcoded user credentials
USER_CREDENTIALS = {
    "admin": "password123",
    "mahir": "2006",
}

# File paths

records_file = "records_data.json"



# Helper function to get the user-specific task file path
def get_user_task_file():
    username = session.get('username')
    if username:
        return f"tasks_{username}.json"
    return None

# Load data from a file
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return []

# Save data to a file
def save_data(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)




@app.route('/')
def home():
    # Redirect to login if the user is not logged in
    if 'username' not in session:
        return redirect(url_for('login'))

    # Load user-specific tasks
    task_file = get_user_task_file()
    tasks = load_data(task_file)
    return render_template('index.html', tasks=tasks, username=session['username'])




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if credentials are valid
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            session['username'] = username  # Save username in session

            # Create user-specific task file if it doesn't exist
            task_file = get_user_task_file()
            if not os.path.exists(task_file):
                save_data(task_file, [])  # Initialize with an empty task list

            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid username or password.")
    return render_template('login.html')



@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove username from session
    return redirect(url_for('login'))






@app.route('/add_task', methods=['POST'])
def add_task():
    # Ensure the user is logged in
    if 'username' not in session:
        return jsonify({"error": "Unauthorized access!"}), 403

    # Load user-specific tasks
    task_file = get_user_task_file()
    tasks = load_data(task_file)

    task_name = request.json.get('task')

    # Validate input
    if not task_name or not task_name.strip():  # Empty or whitespace-only task name
        return jsonify({"error": "Task name cannot be empty."}), 400

    # Normalize task name for consistent comparison
    normalized_task_name = task_name.strip().lower()

    # Check for duplicates
    if normalized_task_name in [task.strip().lower() for task in tasks]:
        return jsonify({"error": "Task already exists."}), 400

    # Add the task if no duplicates are found
    tasks.append(task_name.strip())
    save_data(task_file, tasks)
    return jsonify({"message": "Task added successfully!", "tasks": tasks})


@app.route('/remove_task', methods=['POST'])
def remove_task():
    # Ensure the user is logged in
    if 'username' not in session:
        return jsonify({"error": "Unauthorized access!"}), 403

    # Load user-specific tasks
    task_file = get_user_task_file()
    tasks = load_data(task_file)

    task_name = request.json.get('task')

    # Validate input
    if not task_name:
        return jsonify({"error": "Task name is required!"}), 400

    if task_name not in tasks:
        return jsonify({"error": "Task not found!"}), 400

    # Remove the task
    tasks = [task for task in tasks if task != task_name]
    save_data(task_file, tasks)

    return jsonify({"message": f"Task '{task_name}' removed successfully!"})













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

    unix_begin = int(start_time.timestamp())
    unix_end = int(end_time.timestamp())

    duration_str = str(timedelta(seconds=round(duration)))

    record = {
        "unix_begin": unix_begin,
        "unix_end": unix_end,
        "date": start_time.strftime("%Y-%m-%d"),
        "begin": start_time.strftime("%I:%M %p"),
        "end": end_time.strftime("%I:%M %p"),
        "folder": "",
        "task": current_task,
        "duration": duration_str,
        "duration_decimal": round(duration / 3600, 2),
        "rounding_to": 0,
        "rounding_method": "nearest",
        "original_end": end_time.strftime("%I:%M %p"),
        "notes": "",
        "rate": 0,
        "sum": 0
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
