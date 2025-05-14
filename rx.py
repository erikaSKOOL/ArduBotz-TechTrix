import serial
import csv
from datetime import datetime
import os

SERIAL_PORT = 'COM13'  
BAUD_RATE = 9600
CSV_FILE = 'data2.csv'

RFID_TO_SLOT = {
    '23b8caf8': '1',
    '73d6ba15': '2',
    'c390d2f8': '3',
    '838bb915': '4',
    'f7ee6a62': '5'
}

def initialize_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['slot', 'status', 'in_time', 'out_time'])
            for i in range(1, 6):  
                writer.writerow([str(i), '0', '', ''])

def read_csv():
    with open(CSV_FILE, 'r', newline='') as f:
        return list(csv.DictReader(f))

def write_csv(rows):
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['slot', 'status', 'in_time', 'out_time'])
        writer.writeheader()
        writer.writerows(rows)

def update_slot_with_rfid(tag):
    slot = RFID_TO_SLOT.get(tag)
    if not slot:
        print(f"⚠️ Unknown RFID tag: {tag}")
        return

    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    rows = read_csv()

    for row in rows:
        if row['slot'] == slot:
            if row['status'] == '0':  
                row['status'] = '1'
                row['in_time'] = now
                row['out_time'] = ''
                print(f"[IN ] Slot {slot} at {now}")
            else:  
                row['status'] = '0'
                row['out_time'] = now
                print(f"[OUT] Slot {slot} at {now}")
            break

    write_csv(rows)

def update_sensor_status(sensor_data):
    sensor_values = sensor_data.split(',')
    if len(sensor_values) != 5:
        print(f"⚠️ Invalid sensor data: {sensor_data}")
        return

    rows = read_csv()
    for i in range(5): 
        rows[i]['status'] = sensor_values[i].strip()
    write_csv(rows)
    print(f"📊 Sensor data updated: {sensor_values}")

initialize_csv()

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print("📡 Listening for RFID tags and sensor data...")

    expecting_rfid = False

    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip().lower()

        if not line:
            continue

        if line == 'car enter':
            expecting_rfid = True
            print("🚗 Entry detected. Waiting for RFID scan...")

        elif expecting_rfid:
            print(f"🔖 RFID received: {line}")
            update_slot_with_rfid(line)
            
            ser.write(b'T')
            print("✅ Sent 'T' to ESP32 indicating car entry.")

            expecting_rfid = False

        elif ',' in line:  # Sensor data received
            print(f"📥 Sensor string received: {line}")
            update_sensor_status(line)

        else:
            print(f"❓ Unknown input: {line}")

except serial.SerialException as e:
    print(f"❌ Serial error: {e}")
except Exception as ex:
    print(f"❌ Unexpected error: {ex}")
