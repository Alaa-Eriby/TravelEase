# TravelEase – Step-by-Step Installation & Setup Guide

### 1. Prerequisites
- **Python 3.10+**
- **pip** package manager
- **Git**
- *(Optional)* **Docker & Docker Compose**
- *(Optional)* **PostgreSQL 14+** (SQLite is included out of the box for immediate zero-config testing)

---

### 2. Quick Local Setup (Under 2 Minutes)

#### Step 1: Open Terminal in Project Directory
```powershell
cd D:\pro
```

#### Step 2: Activate Python Virtual Environment
```powershell
.\venv\Scripts\activate
```
*(If you need to create a fresh environment, run: `python -m venv venv`)*

#### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

#### Step 4: Apply Database Migrations
```powershell
python manage.py migrate
```

#### Step 5: Seed Demonstration Data
```powershell
python manage.py seed_data
```
This loads realistic countries, tourist destinations, travel packages, hotels, rooms, customer bookings, audit logs, and test accounts.

#### Step 6: Launch Development Server
```powershell
python manage.py runserver 127.0.0.1:8000
```
Open your browser and navigate to:
**`http://localhost:8000/`**

---

### 3. Demo Credentials
- **Administrator:** `admin` / `AdminPass123!`
- **Travel Agent:** `agent_sarah` / `AgentPass123!`
- **Customer:** `traveler_john` / `TravelerPass123!`

---

### 4. Running the Automated Test Suite
To execute all 19 unit & integration test cases:
```powershell
python manage.py test
```
To run tests using `pytest`:
```powershell
pytest
```

---

### 5. Accessing Interactive API Documentation
- **Swagger UI:** `http://localhost:8000/api/docs/`
- **ReDoc:** `http://localhost:8000/api/redoc/`
- **Django Admin Panel:** `http://localhost:8000/admin/`
