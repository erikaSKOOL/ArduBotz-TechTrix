import serial
import csv
from datetime import datetime
import os
import time

SERIAL_PORT = 'COM13'  
BAUD_RATE = 9600
CSV_FILE = 'data2.csv'

def initialize_csv(file_path):
    headers = ['slot', 'status', 'in_time', 'out_time']
    if not os.path.isfile(file_path):
        with open(file_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for i in range(1, 6):  
                writer.writerow({'slot': str(i), 'status': '0', 'in_time': '', 'out_time': ''})

def load_parking_data(file_path):
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        return {row['slot']: row for row in reader}

def write_parking_data(file_path, data):
    with open(file_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['slot', 'status', 'in_time', 'out_time'])
        writer.writeheader()
        for slot in sorted(data.keys(), key=int):
            writer.writerow(data[slot])

RFID_TO_SLOT = {
    '23b8caf8': '1',  
    '73d6ba15': '2',
    'f7ee6a62': '3',
    '838bb915': '4',
    'c390d2f8': '5'
}

def log_occupancy(parking_data):
    occupied_slots = sum(1 for slot in parking_data.values() if slot['status'] == '1')
    print(f"📊 Current Occupancy: {occupied_slots}/{len(parking_data)} slots occupied.")

def main():
    initialize_csv(CSV_FILE)
    parking_data = load_parking_data(CSV_FILE)

    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2) 

    print("Listening for RFID tags...")

    try:
        while True:
            if arduino.in_waiting > 0:
                tag = arduino.readline().decode('utf-8').strip().lower()
                print(f"Received tag: {tag}")

                slot = RFID_TO_SLOT.get(tag)
                if slot:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M")
                    current_status = parking_data[slot]['status']

                    if current_status == '0':  
                        parking_data[slot]['status'] = '1'
                        parking_data[slot]['in_time'] = now
                        parking_data[slot]['out_time'] = '' 
                        print(f"Slot {slot}: Car entered at {now}")
                    else:  
                        parking_data[slot]['status'] = '0'
                        parking_data[slot]['out_time'] = now
                        print(f"Slot {slot}: Car exited at {now}")

                    write_parking_data(CSV_FILE, parking_data)

                    log_occupancy(parking_data)
                else:
                    print(f"Unknown RFID tag: {tag}")

    except KeyboardInterrupt:
        print("Stopping.")
    finally:
        arduino.close()

if __name__ == "__main__":
    main()