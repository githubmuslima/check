from flask import Flask, request, redirect
import pandas as pd
import os
from datetime import datetime
import schedule
import time
import threading

app = Flask(__name__)

attendance_file = 'attendance.csv'
students_file = 'students.csv'
qr_code_dir = 'qr_codes'

def initialize_files():
    if not os.path.exists(attendance_file):
        df = pd.DataFrame(columns=['name', 'surname', 'date', 'time'])
        df.to_csv(attendance_file, index=False)
        
    if not os.path.exists(students_file):
        raise FileNotFoundError(f"{students_file} fayli topilmadi")

def clear_attendance():
    today = datetime.now().strftime('%Y-%m-%d')
    df = pd.read_csv(attendance_file)
    df = df[df['date'] != today]
    df.to_csv(attendance_file, index=False)

def schedule_tasks():
    schedule.every().day.at("00:00").do(clear_attendance)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/', methods=['GET', 'POST'])
def index():
    initialize_files()
    
    if request.method == 'POST':
        student_data = request.form['student_data']
        student_data_split = student_data.split()
        if len(student_data_split) != 2:
            return "Xato: Iltimos, faqat ism va familiya kiriting."
        
        student_name, student_surname = student_data_split
        
        # Ro'yxatni yangilash
        df = pd.read_csv(attendance_file)
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        time = now.strftime('%H:%M:%S')
        new_row = pd.DataFrame({
            'name': [student_name],
            'surname': [student_surname],
            'date': [today],
            'time': [time]
        })
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(attendance_file, index=False)
        
        return redirect('/')
    
    return '''
        <h1>Ro'yxatga olish</h1>
        <form method="post">
            <label for="student_data">QR Kod Ma'lumotlari:</label>
            <input type="text" id="student_data" name="student_data" placeholder="QR koddan olingan ma'lumot" required>
            <button type="submit">Ro'yxatga olish</button>
        </form>
        <br>
        <h2>O‘quvchi holatini tekshirish</h2>
        <form method="post" action="/check">
            <label for="check_name">Ism:</label>
            <input type="text" id="check_name" name="check_name" required>
            <label for="check_surname">Familiya:</label>
            <input type="text" id="check_surname" name="check_surname" required>
            <button type="submit">Tekshirish</button>
        </form>
    '''

@app.route('/scan', methods=['POST'])
def scan():
    student_data = request.form['student_data']
    student_data_split = student_data.split()
    if len(student_data_split) != 2:
        return "Xato: Iltimos, faqat ism va familiya kiriting."
        
    student_name, student_surname = student_data_split
    
    # Ro'yxatni yangilash
    df = pd.read_csv(attendance_file)
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    time = now.strftime('%H:%M:%S')
    new_row = pd.DataFrame({
        'name': [student_name],
        'surname': [student_surname],
        'date': [today],
        'time': [time]
    })
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(attendance_file, index=False)
    
    return f"O‘quvchi ro‘yxatga olingan, vaqt: {time}"

@app.route('/check', methods=['POST'])
def check():
    name = request.form['check_name']
    surname = request.form['check_surname']
    
    today = datetime.now().strftime('%Y-%m-%d')
    df = pd.read_csv(attendance_file)
    filtered = df[(df['name'] == name) & (df['surname'] == surname) & (df['date'] == today)]
    
    if not filtered.empty:
        time = filtered.iloc[0]['time']
        message = f"O‘quvchi bugun ro‘yxatga olingan, vaqt: {time}"
        color = "green"
    else:
        message = "O‘quvchi bugun ro‘yxatga olinmagan"
        color = "red"
    
    return f'<span style="color:{color}">{message}</span>'

if __name__ == '__main__':
    schedule_tasks()
    threading.Thread(target=run_scheduler, daemon=True).start()
    app.run(debug=True)