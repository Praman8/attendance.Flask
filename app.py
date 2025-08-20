from flask import Flask, request, render_template, redirect, url_for, flash, send_file, after_this_request
import csv
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

ATTENDANCE_FILE = "office_attendance.csv"

def initialize_file():
    """Creates the CSV file with headers if it doesn't exist."""
    if not os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Employee ID", "Employee Name", "Department", "Action", "Timestamp"])

def get_last_action(emp_id):
    """Returns the most recent action for a given employee ID."""
    last_action = None
    if os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Employee ID"] == emp_id:
                    last_action = row["Action"]
    return last_action

def get_today_records():
    """Returns all records for today."""
    today = datetime.now().strftime("%Y-%m-%d")
    today_records = []

    if os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Timestamp"].startswith(today):
                    today_records.append(row)

    return today_records

@app.route('/', methods=['GET', 'POST'])
def attendance():
    if request.method == 'POST':
        emp_id = request.form.get('emp_id', '').strip()
        emp_name = request.form.get('emp_name', '').strip()
        department = request.form.get('department', '').strip()
        action = request.form.get('action', '').strip().lower()

        # Validation
        if not emp_id or not emp_name or not department or not action:
            flash("❌ All fields are required.", "error")
            return redirect(url_for('attendance'))

        last_action = get_last_action(emp_id)

        # Prevent invalid actions
        if action == 'out' and last_action != 'Check-in':
            flash("⛔ Cannot check out without checking in first.", "error")
            return redirect(url_for('attendance'))
        elif action == 'in' and last_action == 'Check-in':
            flash("⛔ You are already checked in.", "error")
            return redirect(url_for('attendance'))

        # Log the action
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(ATTENDANCE_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([emp_id, emp_name, department, "Check-in" if action == 'in' else "Check-out", timestamp])

        flash(f"✅ {emp_name} ({emp_id}) {'checked in' if action == 'in' else 'checked out'} at {timestamp}", "success")
        return redirect(url_for('attendance'))

    # GET request
    records = get_today_records()
    check_in_count = sum(1 for r in records if r["Action"] == "Check-in")
    check_out_count = sum(1 for r in records if r["Action"] == "Check-out")

    return render_template("attendance.html",
                           records=records,
                           check_in_count=check_in_count,
                           check_out_count=check_out_count)

@app.route('/export')
def export_today():
    """Download today's attendance as a CSV file."""
    today = datetime.now().strftime("%Y-%m-%d")
    export_filename = f"attendance_{today}.csv"
    records = get_today_records()

    with open(export_filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["Employee ID", "Employee Name", "Department", "Action", "Timestamp"])
        writer.writeheader()
        for row in records:
            writer.writerow(row)

    @after_this_request
    def remove_file(response):
        try:
            os.remove(export_filename)
        except Exception:
            pass
        return response

    return send_file(export_filename, as_attachment=True)

if __name__ == '__main__':
    initialize_file()
    app.run(debug=True)