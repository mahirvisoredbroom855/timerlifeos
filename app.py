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

#global vars
current_task = None
start_time = None


# Helper function to get the user-specific task file path
def get_user_task_file():
    username = session.get('user')
    if username:
        return f"tasks_{username}.json"
    return None

# Utility function to get user-specific file
def get_user_records_file():
    user = session.get("user")
    if not user:
        return None
    return f"records_{user}.json"


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


# Load tasks for the user
def load_user_tasks():
    username = session.get('user')
    if username:
        task_file = f'tasks_{username}.json'
        if os.path.exists(task_file):
            with open(task_file, 'r') as file:
                return json.load(file)
        else:
            return []
    return []


# Save tasks for the user
def save_user_tasks(tasks):
    user_file = get_user_records_file()
    if not user_file:
        return
    user_data = load_data(user_file)
    user_data["tasks"] = tasks
    save_data(user_file, user_data)


# Load records for the user
def load_user_records():
    user_file = get_user_records_file()
    if not user_file or not os.path.exists(user_file):
        return []  # Return an empty list if no records exist
    user_data = load_data(user_file)
    return user_data.get("records", [])



# Save records for the user
def save_user_records(records):
    user_file = get_user_records_file()  # Get the user-specific records file
    if not user_file:
        return
    user_data = load_data(user_file)
    if "records" not in user_data:
        user_data["records"] = []  # Initialize if the records key is missing
    user_data["records"] = records  # Update the records with the new data
    save_data(user_file, user_data)  # Save the updated data to the file



@app.route('/load_tasks', methods=['GET'])
def load_tasks_json():
    tasks = load_user_tasks()  # This loads the tasks from the user-specific task file
    return jsonify({"tasks": tasks})


@app.route('/')
def home():
    username = session.get('user')
    if username:
        print(f"Logged in as {username}")  # Debug line
        tasks = load_user_tasks()
        return render_template('index.html', username=username, tasks=tasks)
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if credentials are valid
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            session['user'] = username  # Save username in session

            # Create user-specific task and records files if they don't exist
            task_file = f"tasks_{username}.json"
            if not os.path.exists(task_file):
                save_data(task_file, [])  # Initialize with an empty task list

            # Create the records file if it doesn't exist
            records_file = f"records_{username}.json"
            if not os.path.exists(records_file):
                save_data(records_file, {"records": []})  # Initialize with an empty records list

            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid username or password.")
    return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():
    # Remove the user from session
    session.pop('user', None)
    return jsonify({"message": "Logged out successfully."}), 200


@app.route('/add_task', methods=['POST'])
def add_task():
    # Ensure the user is logged in
    if 'user' not in session:
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
    if 'user' not in session:
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


# Route: View records for the user
@app.route('/view_records', methods=['GET'])
def view_records():
    records = load_user_records()
    return jsonify(records)

# Route: Alternative view of records
@app.route('/alternative_records', methods=['GET'])
def alternative_view_records():
    records = load_user_records()
    return jsonify({"message": "This is an alternative view of records.", "records": records})





# Route: Start the timer for a task
@app.route('/start_timer', methods=['POST'])
def start_timer():
    global current_task, start_time  # Keep these as global variables
    task_name = request.json.get('task')

    # Load tasks for the logged-in user
    tasks = load_user_tasks()

    if task_name in tasks:
        current_task = task_name
        start_time = datetime.now()
        return jsonify({"message": f"Timer started for task: {current_task}"})
    return jsonify({"error": "Invalid task selected."}), 400


import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)



@app.route('/stop_timer', methods=['POST'])
def stop_timer():
    global current_task, start_time

    # Ensure current_task and start_time are valid before proceeding
    if current_task is None or start_time is None:
        return jsonify({"error": "No task is currently being timed."}), 400

    # Calculate the time elapsed
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Convert times to UNIX timestamps
    unix_begin = int(start_time.timestamp())
    unix_end = int(end_time.timestamp())

    # Format duration to a readable string
    duration_str = str(timedelta(seconds=round(duration)))

    # Prepare the record data
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

    # Load existing records, append the new record, and save
    records = load_user_records()  # Load the current records
    records.append(record)  # Append the new record
    save_user_records(records)  # Save the updated list of records

    # Clear the current task and start time
    current_task, start_time = None, None

    return jsonify({"message": "Timer stopped and data recorded!", "records": records})















# Route: Export user records
@app.route('/export_records', methods=['POST'])
def export_records():
    period = request.json.get('period')
    if period == "week":
        start_date = datetime.now() - timedelta(days=7)
    elif period == "month":
        start_date = datetime.now() - timedelta(days=30)
    else:
        start_date = datetime.min

    records = load_user_records()
    filtered_records = [
        record for record in records
        if datetime.strptime(record["date"], "%Y-%m-%d") >= start_date
    ]

    export_file = f"exported_records_{session['user']}.json"
    with open(export_file, "w") as f:
        json.dump(filtered_records, f, indent=4)

    return send_file(export_file, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)