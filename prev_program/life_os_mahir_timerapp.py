import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import json

class TaskTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Timer")

        self.data_file = "tasks_data.json"
        self.records_file = "records_data.json"

        self.tasks = self.load_tasks()
        self.current_task = None
        self.start_time = None
        self.records = self.load_records()

        # UI Components
        self.task_label = tk.Label(root, text="Mahir LifeOS Task Timer")
        self.task_label.pack()

        self.task_entry = tk.Entry(root)
        self.task_entry.pack()

        self.add_task_button = tk.Button(root, text="Add Task", command=self.add_task)
        self.add_task_button.pack()

        self.task_listbox = tk.Listbox(root)
        self.task_listbox.pack()
        self.populate_task_listbox()

        self.start_button = tk.Button(root, text="Start Timer", command=self.start_timer)
        self.start_button.pack()

        self.stop_button = tk.Button(root, text="Stop Timer", command=self.stop_timer)
        self.stop_button.pack()

        self.view_records_button = tk.Button(root, text="View Records", command=self.view_records)
        self.view_records_button.pack()

        self.export_button = tk.Button(root, text="Export JSON", command=self.export_json)
        self.export_button.pack()

    def save_tasks(self):
        with open(self.data_file, "w") as f:
            json.dump(self.tasks, f)

    def load_tasks(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                return json.load(f)
        return []

    def save_records(self):
        with open(self.records_file, "w") as f:
            json.dump(self.records, f)

    def load_records(self):
        if os.path.exists(self.records_file):
            with open(self.records_file, "r") as f:
                return json.load(f)
        return []

    def add_task(self):
        task_name = self.task_entry.get()
        if task_name:
            self.tasks.append(task_name)
            self.save_tasks()
            self.task_listbox.insert(tk.END, task_name)
            self.task_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Error", "Task name cannot be empty.")

    def populate_task_listbox(self):
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            self.task_listbox.insert(tk.END, task)

    def start_timer(self):
        selected_task_index = self.task_listbox.curselection()
        if not selected_task_index:
            messagebox.showwarning("Selection Error", "Please select a task to start the timer.")
            return

        self.current_task = self.tasks[selected_task_index[0]]
        self.start_time = time.time()
        messagebox.showinfo("Timer Started", f"Timer started for task: {self.current_task}")

    def stop_timer(self):
        if not self.current_task or not self.start_time:
            messagebox.showwarning("Timer Error", "No task is currently being timed.")
            return

        end_time = time.time()
        duration = end_time - self.start_time
        start_datetime = datetime.fromtimestamp(self.start_time)
        end_datetime = datetime.fromtimestamp(end_time)

        self.records.append({
            "unix_begin": int(self.start_time),
            "unix_end": int(end_time),
            "date": start_datetime.strftime("%Y-%m-%d"),
            "begin": start_datetime.strftime("%I:%M %p"),
            "end": end_datetime.strftime("%I:%M %p"),
            "folder": "Default",
            "task": self.current_task,
            "duration": str(timedelta(seconds=duration)),
            "duration_decimal": round(duration / 3600, 2),
            "rounding_to": 0,
            "rounding_method": "nearest",
            "original_end": end_datetime.strftime("%I:%M %p"),
            "notes": "",
            "rate": 0,
            "sum": 0
        })

        self.save_records()
        self.current_task = None
        self.start_time = None
        messagebox.showinfo("Timer Stopped", "Timer stopped and data recorded.")

    def view_records(self):
        records_window = tk.Toplevel(self.root)
        records_window.title("View Records")

        records_listbox = tk.Listbox(records_window, width=100)
        records_listbox.pack()

        for index, record in enumerate(self.records):
            records_listbox.insert(tk.END, f"{index + 1}: {record['task']} - {record['date']} - {record['begin']} to {record['end']}")

        def delete_record():
            selected = records_listbox.curselection()
            if not selected:
                messagebox.showwarning("Selection Error", "Please select a record to delete.")
                return

            record_index = selected[0]
            del self.records[record_index]
            self.save_records()
            records_listbox.delete(record_index)
            messagebox.showinfo("Record Deleted", "Record deleted successfully.")

        delete_button = tk.Button(records_window, text="Delete Record", command=delete_record)
        delete_button.pack()

    def export_json(self):
        if not self.records:
            messagebox.showwarning("Export Error", "No data to export.")
            return

        def filter_records(period):
            if period == "week":
                start_date = datetime.now() - timedelta(days=7)
            elif period == "month":
                start_date = datetime.now() - timedelta(days=30)
            else:
                start_date = datetime.min

            return [
                record for record in self.records
                if datetime.strptime(record["date"], "%Y-%m-%d") >= start_date
            ]

        def export(period):
            filtered_records = filter_records(period)

            if not filtered_records:
                messagebox.showwarning("Export Error", f"No records found for the selected period: {period}.")
                return

            file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])

            if file_path:
                with open(file_path, "w") as f:
                    json.dump(filtered_records, f, indent=4)
                messagebox.showinfo("Export Successful", f"Data exported to {file_path}")

        export_window = tk.Toplevel(self.root)
        export_window.title("Export Options")

        tk.Label(export_window, text="Select export period:").pack()

        tk.Button(export_window, text="Export Last 7 Days", command=lambda: export("week")).pack()
        tk.Button(export_window, text="Export Last 30 Days", command=lambda: export("month")).pack()
        tk.Button(export_window, text="Export All Records", command=lambda: export("all")).pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskTimerApp(root)
    root.mainloop()
