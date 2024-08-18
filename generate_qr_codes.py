import qrcode
import pandas as pd
import os

students_file = 'students.csv'
output_dir = 'qr_codes'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

students = pd.read_csv(students_file)

for index, student in students.iterrows():
    data = f"{student['name']} {student['surname']}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    file_name = f"{student['name']}_{student['surname']}.png"
    img.save(os.path.join(output_dir, file_name))

print("QR kodlar yaratildi.")
