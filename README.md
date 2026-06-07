# 🚐 Jeepney Fuel Consumption Simulation

A Python-based real-time fuel consumption simulation system for a modern Philippine jeepney using vehicle dynamics, driver behavior modeling, and interactive Streamlit visualization.

---

# 📌 Overview

This project simulates the fuel consumption behavior of a modern Philippine jeepney using second-by-second physics-based calculations.

The simulation considers:

* Vehicle acceleration
* Rolling resistance
* Aerodynamic drag
* Driver behavior
* Traction force
* Fuel consumption rate
* Coasting behavior

The application provides a real-time dashboard with:

* Live telemetry
* Animated vehicle movement
* Fuel analytics
* Speed graphs
* Downloadable simulation results

---

# 🧠 Features

## Real-Time Simulation

* Live vehicle movement visualization
* Real-time telemetry updates
* Route progression playback

## Driver Behavior Profiles

* Aggressive
* Moderate
* Eco

Each profile affects:

* Acceleration
* Deceleration
* Cruise speed
* Coasting behavior
* Fuel efficiency

## Analytics Dashboard

* Speed vs Time graph
* Fuel Consumption graph
* Traction Force graph
* Fuel Economy metrics

## Data Export

* Download simulation results as CSV

---

# ⚙️ Technologies Used

* Python
* Streamlit
* Pandas
* NumPy
* Plotly

---

# 📂 Project Structure

fuel_consumption_simulation_QMMS/
│
├── main.py
├── simulation.py
├── routes.py
├── behaviors.py
├── vehicle.py
├── requirements.txt
└── README.md

---

# 🚀 Installation

## Clone Repository

git clone <repository-url>
cd fuel_consumption_simulation_QMMS

## Install Dependencies

pip install -r requirements.txt

---

# ▶️ Running the Application

py -m streamlit run main.py

The application will open in your browser at:

http://localhost:8501

---

# 🧮 Simulation Model

The system calculates fuel consumption using:

## Traction Force Equation

* Inertial force
* Rolling resistance
* Aerodynamic drag

## Fuel Consumption Equation

Fuel rate is derived from:

* Traction power
* Drivetrain efficiency
* Fuel lower heating value

---

# 📊 Example Outputs

* Total fuel consumed
* Fuel economy (km/L)
* Speed profile
* Traction force profile
* Real-time vehicle telemetry

---

# 📌 Future Improvements

* Passenger load simulation
* Traffic conditions
* Road elevation
* Weather effects
* GPS route visualization
* CO₂ emission analysis
* AI driving optimization

# Jeepney Fuel Consumption Simulator

## Folder Structure

```
jeepney_simulator/
├── api.py            ← Flask backend (NEW)
├── index.html        ← Frontend connected to API (NEW)
├── simulation.py     ← Physics engine
├── behaviors.py      ← Driving behavior profiles
├── routes.py         ← Route definitions
├── vehicle.py        ← Jeepney parameters
├── main.py           ← Original Streamlit app (optional)
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
```

## Run

### 1. Start the backend API
```bash
python api.py
```
Flask will start at http://localhost:5000

### 2. Open the frontend
Open `index.html` directly in your browser (double-click it).

The sidebar will show **API connected** in green when the backend is reachable.

## API Endpoints

| Method | Endpoint         | Description                    |
|--------|-----------------|-------------------------------|
| GET    | /api/routes     | List available routes          |
| GET    | /api/behaviors  | List driving behavior profiles |
| POST   | /api/simulate   | Run a simulation               |

### POST /api/simulate — Request body
```json
{
  "route": "route_1",
  "behavior": "Eco"
}
```

### POST /api/simulate — Response
```json
{
  "log":          [...],
  "total_fuel_L": 0.123456,
  "economy_kmL":  12.34,
  "distance_km":  6.24,
  "duration_s":   845
}
```

## Optional: Streamlit app
```bash
streamlit run main.py
```


# 📄 License

This project is intended for academic and research purposes.