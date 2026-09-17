# Automotive AI Telemetry & Local RAG Diagnostic Pipeline

An offline-first, modular Python architecture designed to ingest real-time OBD-II vehicle telemetry, detect threshold anomalies across multi-brand chassis profiles, translate Diagnostic Trouble Codes (DTCs) via an embedded SQLite database, and synthesize preventative maintenance reports locally with zero internet dependency.

---

##  Architectural Overview

Modern vehicle diagnostics often rely on cloud infrastructure, making them vulnerable in air-gapped or low-connectivity environments. This pipeline demonstrates edge computing principles by processing telemetry entirely locally using a decoupled, modular design:

1. **`mock_obd.py`**: Simulates live ECU polling streams (RPM, coolant temperature, throttle position, and Short Term Fuel Trim), outputting structured CSV drive logs. (Easily swappable with physical ELM327 `python-obd` hardware interfaces).
2. **`vehicle_profile.json`**: A brand-specific configuration framework that dynamically adjusts operational safety thresholds (e.g., thermal limits, fuel trim drift) and tracks common model-specific chassis vulnerabilities.
3. **`detect_anomalies.py`**: Automatically initializes an embedded, offline **SQLite database** seeded with cross-brand DTC registries. It processes drive logs, flags thermal and fuel anomalies in real-time, and performs air-gapped fault code translation.
4. **`ai_diagnostician.py`**: Acts as a local RAG (Retrieval-Augmented Generation) report synthesizer, combining peak telemetry metrics with manufacturer knowledge bases to generate comprehensive preventative maintenance summaries.

---

##  Project Structure

```text
automotive_ai_pipeline/
│
├── mock_obd.py            # Live ECU telemetry simulator & CSV logger
├── vehicle_profile.json   # Manufacturer thresholds and known vulnerabilities
├── detect_anomalies.py    # SQLite engine & real-time threshold rule-checker
└── ai_diagnostician.py    # Local RAG report synthesizer & mechanics advisory
