from flask import Flask, request, render_template, redirect, url_for, flash
import csv
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

ATTENDANCE_FILE = "office_attendance.csv"

def initialize_file():
    """Create the attendance CSV file if it doesn't exist."""
    if not os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Employee ID", "Employee Name", "Action", "Timestamp"])

def get_last_action(emp_id):
    """Retrieve the last attendance action for the given employee ID."""
    last_action = None
    if os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["Employee ID"] == emp_id:
                    last_action = row["Action"]
    return last_action

def get_today_records():
    """Fetch attendance records for today."""
    records = []
    today_str = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["Timestamp"].startswith(today_str):
                    records.append(row)
    return records

@app.route('/', methods=['GET', 'POST'])
def attendance():
    if request.method == 'POST':
        emp_id = request.form['emp_id'].strip()
        emp_name = request.form['emp_name'].strip()
        action = request.form['action'].strip().lower()

        if not emp_id or not emp_name:
            flash(("error", "❌ Please provide both Employee ID and Full Name."))
            return redirect(url_for('attendance'))

        last_action = get_last_action(emp_id)

        if action == 'out' and last_action != 'Check-in':
            flash(( "❌ Cannot check out without checking in first."))
        elif action == 'in' and last_action == 'Check-in':
            flash(("❌ You are already checked in."))
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(ATTENDANCE_FILE, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([emp_id, emp_name, "Check-in" if action == 'in' else "Check-out", timestamp])
            flash(("success", f"✅ {emp_name} ({emp_id}) {'checked in' if action == 'in' else 'checked out'} at {timestamp}"))

        return redirect(url_for('attendance'))

    records = get_today_records()
    return render_template('attendance.html', records=records)

if __name__ == '__main__':
    initialize_file()
    app.run(debug=True)
