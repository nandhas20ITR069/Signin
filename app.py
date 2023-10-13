import os
import time
import qrcode
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from flask import Flask, request, render_template, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)

# Google Sheets API setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("F:/signinnnnnnnnnnnn/credentials/sigin-401516-0289e9251633.json", scope)
client = gspread.authorize(credentials)
spreadsheet_id = "1zS8bcrvWvxUq4CX8QVCaRGyZvthBvej4sajtq9tVsf8"
sheet = client.open_by_key(spreadsheet_id).sheet1  # Replace with your actual Google Sheet name

# Ensure the static/qr_codes directory exists
QR_CODE_DIR = 'static/qr_codes'
os.makedirs(QR_CODE_DIR, exist_ok=True)

email_ids = []

def generate_qr_code(data, filename):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)

def send_mail(sender_email, sender_password, recipient_email, subject, body, qr_code_path):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with open(qr_code_path, 'rb') as file:
        qr_code = MIMEImage(file.read(), name=os.path.basename(qr_code_path))
        qr_code.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(qr_code_path)}"')
        msg.attach(qr_code)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/give_attendance', methods=['POST'])
def give_attendance():
    global email_ids
    email_ids = sheet.col_values(3)[1:]  # Assuming email IDs are in the second column (adjust index as per your sheet)
    
    for email_id in email_ids:
        qr_code_data = f'{email_id}'  # Include email ID in the QR code data
        qr_code_filename = f'{QR_CODE_DIR}/{email_id}_qr_code.png'
        generate_qr_code(qr_code_data, qr_code_filename)

        sender_email = 'nandhas.20it@kongu.edu'  # Sender's email address
        sender_password = 'vxfdwytmfxdtvjnb'  # Sender's email password
        subject = 'Attendance QR Code'
        body = 'Please find your attendance QR code attached below.'

        # Record mail sent time
        mail_sent_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        send_mail(sender_email, sender_password, email_id, subject, body, qr_code_filename)
        sheet.update_cell(email_ids.index(email_id) + 2, 8, mail_sent_time)  # Update the timestamp in column 7
        time.sleep(1)  # Add a delay to avoid rate-limiting issues with the email server

    return jsonify({'message': 'QR codes sent successfully to all students.'})

@app.route('/scan_qr_code', methods=['POST'])
def scan_qr_code():
    email_id = request.form['email']  # Get the email ID from the scanned QR code
    # Assuming 'yes' is the value to be updated in the Google Sheet upon successful scanning
    # Check if the scanned email ID exists in the Google Sheet
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if email_id in email_ids:
        # Find the index of the email ID in the list and update the corresponding cell in the Google Sheet
        sheet.update_cell(email_ids.index(email_id) + 2, 7, 'yes')  # Update the corresponding cell in the Google Sheet
        sheet.update_cell(email_ids.index(email_id) + 2, 9, timestamp)
        return jsonify({'message': 'Attendance recorded successfully.'})
    else:
        return jsonify({'message': 'Invalid email ID. Attendance not recorded.'}), 400  # Return a 400 Bad Request status code for invalid email IDs

if __name__ == '__main__':
    app.run(debug=True)
