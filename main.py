import pandas as pd
from datetime import datetime

FILE = 'data.csv'
TOTAL_SLOTS = 6

def current_occupancy():
    df = pd.read_csv(FILE)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Keep only the latest status per slot
    latest = df.sort_values('timestamp').groupby('slot_id').last().reset_index()

    # Count how many are currently occupied (status = 1)
    occupied = latest[latest['status'] == 1].shape[0]
    return occupied

def calculate_price(occupied):
    rate = occupied / TOTAL_SLOTS
    if rate <= 0.5:
        return 10
    elif rate <= 0.8:
        return 20
    else:
        return 30

if __name__ == "__main__":
    occ = current_occupancy()
    price = calculate_price(occ)
    print(f"🅿 {occ}/{TOTAL_SLOTS} slots occupied")
    print(f"💰 Current price: ₹{price}/hr")
    