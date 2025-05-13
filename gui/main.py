import tkinter as tk
import csv
import pandas as pd
from sklearn.tree import DecisionTreeRegressor

def train_model():
    data = pd.DataFrame({
        "occupancy_rate": [0.0, 0.33, 0.5, 0.66, 0.83, 1.0],
        "price": [10, 10, 10, 20, 20, 30]
    })
    X = data[["occupancy_rate"]]
    y = data["price"]
    model = DecisionTreeRegressor()
    model.fit(X, y)
    return model

def ml_price_prediction(occupied, total_slots=5):
    rate = occupied / total_slots
    return round(model.predict([[rate]])[0])

CSV_FILE = "C:/Users/milin/OneDrive/Pictures/HackAthon/ArduBotz-TechTrix/data2.csv"
TOTAL_SLOTS = 5

def load_data():
    try:
        with open(CSV_FILE, newline="") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            return [row for row in reader if len(row) >= 4]
    except FileNotFoundError:
        print("CSV file not found.")
        return []

def current_occupancy(data):
    latest = {}
    for row in data:
        slot_id = row[0]
        status = row[1]
        latest[slot_id] = status
    return sum(1 for s in latest.values() if s == '1')

def update():
    data = load_data()
    occupied = current_occupancy(data)
    price_now = ml_price_prediction(occupied, TOTAL_SLOTS)

    future_occupied = min(occupied + 1, TOTAL_SLOTS)
    price_future = ml_price_prediction(future_occupied, TOTAL_SLOTS)

    price_label.config(
        text=f"🤖 Current Price: ₹{price_now}/hr\n🔮 Future Price: ₹{price_future}/hr (if 1 more car arrives)"
    )

    for i in range(5):
        if i < len(data):
            row = data[i]
            status = row[1]
            in_time = row[2] or "---"
            out_time = row[3] or "---"
            color = "red" if status == '1' else "green"
        else:
            color = "gray"
            in_time = out_time = "---"
        canvas.itemconfig(boxes[i], fill=color)
        canvas.itemconfig(info[i], text=f"IN: {in_time}\nOUT: {out_time}")
    root.after(2000, update)


model = train_model()  

root = tk.Tk()
root.title("Smart Parking System (ML Pricing)")
canvas = tk.Canvas(root, width=800, height=400)
canvas.pack()

boxes = []
info = []

for i in range(5):
    x = 60 + (i % 3) * 240
    y = 40 if i < 3 else 200
    box = canvas.create_rectangle(x, y, x+180, y+100, fill="gray")
    label = canvas.create_text(x + 90, y - 20, text=f"Spot {i + 1}", font=("Arial", 10, "bold"))
    boxes.append(box)
    info.append(label)

price_label = tk.Label(root, text="🤖 ML Price: ₹--/hr", font=("Arial", 14))
price_label.pack(pady=10)

update()
root.mainloop()
