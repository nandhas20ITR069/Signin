# import cv2
# import requests
# from pyzbar.pyzbar import decode
# import json

# def scan_qr_code():
#     cap = cv2.VideoCapture(0)  # Use the default camera (index 0)

#     while True:
#         ret, frame = cap.read()

#         # Decode QR codes in the frame
#         decoded_objects = decode(frame)
        
#         for obj in decoded_objects:
#             qr_data = obj.data.decode('utf-8')
#             print(f'Scanned QR Data: {qr_data}')
            
#             # Send scanned data to Flask server for marking attendance
#             payload = {'data': qr_data}
#             response = requests.post('http://localhost:5000/mark_attendance', json=payload)
#             print(response.text)

#         cv2.imshow('QR Code Scanner', frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()

# if __name__ == '__main__':
#     scan_qr_code()




import cv2
import requests
from pyzbar.pyzbar import decode
import json

def scan_qr_code():
    cap = cv2.VideoCapture(0)  # Use the default camera (index 0)

    while True:
        ret, frame = cap.read()

        # Decode QR codes in the frame
        decoded_objects = decode(frame)
        
        for obj in decoded_objects:
            qr_data = obj.data.decode('utf-8')
            print(f'Scanned QR Data: {qr_data}')
            
            # Send scanned data to Flask server for marking attendance
            payload = {'email': qr_data}  # Assuming QR code contains email data
            response = requests.post('http://localhost:5000/scan_qr_code', data=payload)
            print(response.text)

        cv2.imshow('QR Code Scanner', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    scan_qr_code()
