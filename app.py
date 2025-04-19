from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import json
import os
import threading
import time
import requests
from communicator import Communicator

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weights.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# SERIAL COMMUNICATION WRAPPER
communicator = Communicator('/dev/serial0', 9600)

# Food status memory
food_status = {"low": False}
last_beep_time = 0

class CatWeight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    weight = db.Column(db.Float)
    bmi = db.Column(db.Float)

def load_settings():
    try:
        with open("schedule.json", "r") as f:
            return json.load(f)
    except:
        return {"portion_grams": 10, "schedule": []}

def save_settings(data):
    with open("schedule.json", "w") as f:
        json.dump(data, f)

def load_cat():
    try:
        with open("cat.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_cat(data):
    with open("cat.json", "w") as f:
        json.dump(data, f)

def calculate_age_months(birthdate_str):
    birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d").date()
    today = date.today()
    return (today.year - birthdate.year) * 12 + today.month - birthdate.month

def get_latest_weight():
    weight = CatWeight.query.order_by(CatWeight.timestamp.desc()).first()
    return weight.weight if weight else None

def get_latest_bmi():
    weight = CatWeight.query.order_by(CatWeight.timestamp.desc()).first()
    return weight.bmi if weight else None

@app.route("/", methods=["GET", "POST"])
def index():
    settings = load_settings()
    cat = load_cat()

    if request.method == "POST":
        if "feed_now" in request.form:
            portions = int(request.form.get("portions", 1))
            print(f"Feeding {portions} portion(s)")
            communicator.send(f"FEED:{portions}")
        elif "add_schedule" in request.form:
            time_str = request.form["feed_time"]
            portions = int(request.form["feed_portions"])
            settings["schedule"].append({"time": time_str, "portions": portions})
            save_settings(settings)
        elif "delete_time" in request.form:
            delete_time = request.form["delete_time"]
            settings["schedule"] = [s for s in settings["schedule"] if s["time"] != delete_time]
            save_settings(settings)

    age_years = None
    weight_kg = None
    bmi = None

    if cat.get("birthdate"):
        age_months = calculate_age_months(cat["birthdate"])
        age_years = round(age_months / 12, 1)

    weight = get_latest_weight()
    if weight:
        weight_kg = round(weight / 1000, 2)

    latest_bmi = get_latest_bmi()
    if cat.get("length"):
        try:
            length = float(cat["length"])
            if length > 0:
                bmi = latest_bmi
        except (ValueError, TypeError):
            bmi = None

    return render_template("index.html",
        settings=settings,
        cat=cat,
        age_years=age_years,
        weight_kg=weight_kg,
        bmi=bmi,
        food_low=food_status["low"]
    )

@app.route("/cat", methods=["GET", "POST"])
def cat():
    cat = load_cat()
    age_years = None

    if request.method == "POST":
        cat["name"] = request.form["name"]
        cat["birthdate"] = request.form["birthdate"]
        cat["gender"] = request.form["gender"]
        cat["length"] = float(request.form["length"])
        save_cat(cat)
        return redirect("/cat")

    if cat.get("birthdate"):
        age_months = calculate_age_months(cat["birthdate"])
        age_years = round(age_months / 12, 1)

    return render_template("cat.html", cat=cat, age_years=age_years)

@app.route("/settings", methods=["GET", "POST"])
def settings():
    settings = load_settings()
    if request.method == "POST":
        settings["portion_grams"] = int(request.form["portion_grams"])
        save_settings(settings)
        return redirect("/settings")
    return render_template("settings.html", portion_grams=settings["portion_grams"])

@app.route("/weights")
def weights():
    return render_template("weights.html")

@app.route("/weights_data")
def weights_data():
    data = CatWeight.query.order_by(CatWeight.timestamp.asc()).all()
    return jsonify([{"timestamp": w.timestamp.isoformat(), "weight": w.weight, "bmi": w.bmi} for w in data])

@app.route("/log_weight", methods=["POST"])
def log_weight():
    value = request.get_json()
    weight = float(value.get("weight", 0))
    cat = load_cat()
    bmi = None

    weight_kg = weight / 1000
    cat_length = cat.get("length")

    try:
        cat_length = float(cat_length)
        if cat_length > 0:
            bmi = round(weight_kg / (cat_length ** 2), 2)
    except (ValueError, TypeError):
        bmi = None

    entry = CatWeight(weight=weight, bmi=bmi)
    db.session.add(entry)
    db.session.commit()
    return jsonify({"status": "ok"})

@app.route("/delete_weights", methods=["POST"])
def delete_weights():
    CatWeight.query.delete()
    db.session.commit()
    return redirect("/weights")

@app.route("/set_oled_mode", methods=["POST"])
def set_oled_mode():
    mode = request.form.get("mode")
    if mode in ["weight", "bongo"]:
        print(f"OLED mode set to: {mode}")
        communicator.send(f"MODE:{mode}")
    return redirect("/")

def listen_to_arduino():
    while True:
        try:
            line = communicator.read_line()
            if line:
                if line.startswith("WEIGHT:"):
                    weight_str = line.split(":")[1]
                    if weight_str.replace('.', '', 1).isdigit():
                        print(f"Received weight: {weight_str} g")
                        requests.post("http://localhost:5000/log_weight", json={"weight": float(weight_str)})
                elif line.startswith("FOOD:"):
                    status = line.split(":")[1]
                    if status == "LOW":
                        food_status["low"] = True
                        print("Food is LOW")
                    elif status == "OK":
                        food_status["low"] = False
                        print("Food is OK")
        except Exception as e:
            print(f"Error reading serial: {e}")
        time.sleep(0.2)

def buzzer_loop():
    global last_beep_time
    while True:
        now = datetime.now()
        hour = now.hour

        if food_status["low"] and 8 <= hour < 18:
            if now.timestamp() - last_beep_time > 3600:
                print("Sending BUZZ to Arduino")
                communicator.send("BUZZ")
                last_beep_time = now.timestamp()
        time.sleep(60)

if __name__ == "__main__":
    if not os.path.exists("weights.db"):
        with app.app_context():
            db.create_all()
    threading.Thread(target=listen_to_arduino, daemon=True).start()
    threading.Thread(target=buzzer_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)

