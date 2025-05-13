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
            for i in range(1, 7):
                writer.writerow([str(i), '0', '', ''])

def read_csv():
    with open(CSV_FILE, 'r', newline='') as f:
        return list(csv.DictReader(f))

def write_csv(rows):
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['slot', 'status', 'in_time', 'out_time'])
        writer.writeheader()
        writer.writerows(rows)

def update_slot(tag):
    slot = RFID_TO_SLOT.get(tag)
    if not slot:
        print(f"⚠️ Unknown RFID tag: {tag}")
        return

    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    rows = read_csv()

    for row in rows:
        if row['slot'] == slot:
            if row['status'] == '0':  # Car entering
                row['status'] = '1'
                row['in_time'] = now
                row['out_time'] = ''
                print(f"[IN ] Slot {slot} at {now}")
            else:  # Car exiting
                row['status'] = '0'
                row['out_time'] = now
                print(f"[OUT] Slot {slot} at {now}")
            break

    write_csv(rows)

# --- MAIN EXECUTION ---
initialize_csv()

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print("📡 Listening for RFID tags...")

    while True:
        tag = ser.readline().decode('utf-8', errors='ignore').strip().lower()
        if tag:
            print(f"🔖 Tag detected: {tag}")
            update_slot(tag)

except serial.SerialException as e:
    print(f"❌ Serial error: {e}")
except Exception as ex:
    print(f"❌ Unexpected error: {ex}")
