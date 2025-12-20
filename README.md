# 🏥 National Flu Stress Monitor (Task 1)

## 📌 Project Overview
The **National Flu Stress Monitor** is a Python-based data analytics dashboard designed for public health surveillance. It integrates live provisional mortality data from the **CDC Open Data API** with local hospital capacity records to calculate a "Healthcare Stress Index."

This tool demonstrates a professional **Service-Repository Architecture**, ensuring clean separation between external data fetching, internal business logic, and the user interface.

## 🚀 Key Features
* **Live Data Ingestion:** Fetches real-time provisional Influenza death counts from the CDC API (Dataset: `Provisional COVID-19 Death Counts by Week`).
* **Healthcare Stress Index:** Implements the UKHSA staffing model (1:15 ratio) to quantify hospital strain:
  $$\text{Stress Index} = \left( \frac{\text{Flu Deaths} \times 15}{\text{ICU Beds}} \right) \times 100$$
* **Interactive Dashboard:** Visualises temporal trends, peak stress weeks, and risk levels using Plotly.
* **Admin CRUD Interface:** A secured panel allowing administrators to manually **Update** hospital bed capacity in the database to reflect real-time operational changes.
* **Persistent Caching:** Stores processed data in a local SQLite database (`health_dashboard.db`) for offline resilience.

## 🛠️ Technical Architecture
The project avoids monolithic scripts by using a modular design:
* **`src/repo.py`**: Handles CDC API communication and error resilience.
* **`src/database.py`**: Managing SQLite transactions via a DAO (Data Access Object) pattern.
* **`src/service.py`**: The "Business Logic" layer (Merging API+CSV and calculating Risk).
* **`src/ui/`**: Streamlit components for the Dashboard and Admin Panel.

## 📂 Project Structure
```text
├── 01_Data/
│   └── us_states_capacity.csv    # Static Hospital Bed Capacity Data
├── src/
│   ├── ui/
│   │   ├── dashboard.py          # Main Visualisation View
│   │   └── admin.py              # CRUD Admin Interface
│   ├── database.py               # Database Adapter (SQLite)
│   ├── repo.py                   # API Repository
│   ├── service.py                # Core ETL & Logic Service
│   └── log_config.py             # Logging Configuration
├── tests/
│   └── test_app.py               # TDD Unit Tests
│   └── test_database.py          # TDD Unit Tests
│   └── test_enhancements.py      # TDD Unit Tests
│   └── test_service.py           # TDD Unit Tests
│   └── test_ui.py                # TDD Unit Tests
├── app.py                        # Main Dashboard Entry Point
├── main.py                       # ETL Pipeline Entry Point
├── requirements.txt              # Dependencies
└── README.md                     # Project Documentation

## Usage
* **Install dependencies:** `pip install -r requirements.txt`
* **Run the ETL pipeline:** `python3 main.py`
* **Launch the dashboard:** `streamlit run app.py`
* **Run TDD suite:** `python3 -m pytest`