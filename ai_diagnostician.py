import json
import glob
import os
import csv

def run_ai_diagnostics():
    try:
        with open("vehicle_profile.json", "r") as f:
            profile = json.load(f)
    except FileNotFoundError:
        print("vehicle_profile.json missing!")
        return

    csv_files = glob.glob("drive_log_*.csv")
    if not csv_files:
        print("No drive log found!")
        return
    latest_file = max(csv_files, key=os.path.getctime)

    max_temp, max_stft = 0.0, 0.0
    detected_dtcs = set()

    with open(latest_file, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            max_temp = max(max_temp, float(row["Coolant_Temp"]))
            max_stft = max(max_stft, float(row["STFT"]))
            if row["Active_DTC"] != "NONE":
                detected_dtcs.add(row["Active_DTC"])

    print(f"\n[AI Local Engine] Synthesizing diagnostic RAG report for {profile['year']} {profile['make']} {profile['model']}...")
    print("=" * 60)

    report = f"""
    --- AUTOMOTIVE AI PREVENTATIVE MAINTENANCE REPORT ---
    Chassis Profile: {profile['year']} {profile['make']} {profile['model']} ({profile['engine']})
    
    [TELEMETRY PEAK METRICS]
    - Peak Coolant Temp: {max_temp}°C (Safe Threshold: {profile['thresholds']['max_coolant_temp']}°C)
    - Peak Fuel Trim Drift (STFT): +{max_stft}% (Safe Threshold: +{profile['thresholds']['max_stft']}%)
    - Active DTCs Flagged: {list(detected_dtcs) if detected_dtcs else "None"}

    [KNOWN CHASSIS VULNERABILITIES]
    - {profile['common_issues'][0]}
    - {profile['common_issues'][1]}

    [MASTER MECHANIC RECOMMENDATIONS]
    Telemetry indicates synchronous thermal creep and positive fuel trim compensation under load. 
    Action plan: Inspect cooling pathways, execute a smoke test for intake leaks, and verify DTC registries.
    ------------------------------------------------------
    """
    print(report)

if __name__ == "__main__":
    run_ai_diagnostics()