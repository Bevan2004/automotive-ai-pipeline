import csv
import glob
import os
import json
import sqlite3

def init_local_database():
    """Initializes a local air-gapped SQLite database with multi-brand DTC registries."""
    conn = sqlite3.connect("local_automotive_database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dtc_registry (
            make TEXT,
            code TEXT,
            description TEXT,
            corrective_action TEXT,
            PRIMARY KEY (make, code)
        )
    """)
    
    # Pre-populate multi-brand database samples (Mazda, Audi, Mercedes, Range Rover)
    sample_codes = [
        ("Mazda", "P0171", "System Too Lean (Bank 1)", "Inspect intake manifold runner control gasket and PCV hoses."),
        ("Mazda", "P0126", "Insufficient Coolant Temp for Thermostat Operation", "Replace engine thermostat and flush coolant fluid."),
        ("Audi", "P0299", "Turbocharger Underboost", "Check N75 valve performance and wastegate linkage play."),
        ("Mercedes-Benz", "P029900", "Charge Pressure Too Low (AMG)", "Inspect auxiliary intercooler pump and turbo compressor outlet."),
        ("Land Rover", "P0117", "Engine Coolant Temp Circuit Low Input", "Check thermostat housing ground and wiring harness.")
    ]
    cursor.executemany("INSERT OR IGNORE INTO dtc_registry VALUES (?, ?, ?, ?)", sample_codes)
    conn.commit()
    conn.close()

def lookup_dtc_offline(make, code):
    """Queries the local SQLite database offline with zero internet dependency."""
    conn = sqlite3.connect("local_automotive_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT description, corrective_action FROM dtc_registry WHERE make = ? AND code = ?", (make, code))
    result = cursor.fetchone()
    conn.close()
    return result if result else ("Unmapped Powertrain Fault", "Perform manual diagnostic scan.")

def analyze_logs():
    init_local_database()

    try:
        with open("vehicle_profile.json", "r") as f:
            profile = json.load(f)
            thresholds = profile.get("thresholds", {"max_coolant_temp": 95.0, "max_stft": 5.0})
    except FileNotFoundError:
        print("Profile not found. Using default limits.")
        profile = {"make": "Mazda"}
        thresholds = {"max_coolant_temp": 95.0, "max_stft": 5.0}

    csv_files = glob.glob("drive_log_*.csv")
    if not csv_files:
        print("No drive log found! Run mock_obd.py first.")
        return
    
    latest_file = max(csv_files, key=os.path.getctime)
    print(f"Analyzing log: {latest_file} for {profile.get('make')} chassis\n" + "-"*50)

    anomalies_detected = 0

    with open(latest_file, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            timestamp = row["Timestamp"]
            coolant = float(row["Coolant_Temp"])
            stft = float(row["STFT"])
            dtc = row["Active_DTC"]

            if coolant > thresholds["max_coolant_temp"]:
                print(f"[{timestamp}] [WARNING] Thermal Creep: {coolant}°C (Limit: {thresholds['max_coolant_temp']}°C)")
                anomalies_detected += 1

            if stft > thresholds["max_stft"]:
                print(f"[{timestamp}] [ALERT] Fuel Trim Drift: +{stft}% (Limit: +{thresholds['max_stft']}%)")
                anomalies_detected += 1

            if dtc != "NONE":
                desc, fix = lookup_dtc_offline(profile.get("make"), dtc)
                print(f"[{timestamp}] [DTC FOUND] Code {dtc}: {desc} | Recommended Fix: {fix}")
                anomalies_detected += 1

    print("-" * 50)
    print(f"Analysis complete. Total anomalies flagged: {anomalies_detected}")

if __name__ == "__main__":
    analyze_logs()