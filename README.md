# 🌍 TravelEase – Smart Travel & Tourism Booking System
> **An enterprise-grade, concurrency-safe travel and tourism booking web platform built with Django 5, Django REST Framework, and PostgreSQL / SQLite.**

[![Django](https://img.shields.io/badge/Django-5.2-green.svg?logo=django)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.18-red.svg)](https://www.django-rest-framework.org/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL%20%7C%20SQLite-4169E1.svg?logo=postgresql)](https://www.postgresql.org/)
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0%20Swagger-85EA2D.svg?logo=swagger)](http://localhost:8000/api/docs/)
[![Tests](https://img.shields.io/badge/Tests-19%20Passed%20(100%25)-success.svg)](docs/TESTING_REPORT.md)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

---

## 📖 Overview | نظرة عامة

**TravelEase** is an enterprise-grade travel and tourism booking web platform developed as a Software Construction capstone. It provides a robust, commercially structured, database-driven service connecting travelers with certified tour operators and centralized system administrators.

Key engineering highlights include:
- **Concurrency-Safe Bookings**: Strict database row-level locking (`select_for_update`) to prevent overbooking on concurrent departure reservations.
- **Dynamic Hotel Availability**: Exact date-range overlap validation algorithms ensuring zero double-bookings.
- **Academic Payment Gateway**: Deterministic, audit-tracked simulated payment ledger.
- **Dual Presentation**: Fully featured server-rendered Bootstrap 5 web interface + RESTful JSON APIs with interactive Swagger/ReDoc.

---

## 📑 Table of Contents

- [Key Features](#-key-features)
- [Role-Based Portals](#-role-based-portals)
- [User Interface Showcase](#-user-interface-showcase)
- [System Architecture & UML](#-system-architecture--uml)
- [Technology Stack](#-technology-stack)
- [Quick Start & Installation](#-quick-start--installation)
- [Demonstration Accounts](#-demonstration-accounts)
- [REST API & Swagger](#-rest-api--swagger)
- [Automated Testing](#-automated-testing)
- [Project Documentation](#-project-documentation)

---

## ✨ Key Features

| Feature | Description |
|---|---|
| **Multi-Step Package Wizard** | Smooth booking flow with real-time price calculation, passenger manifest collection, and instant receipt generation. |
| **Room Inventory Management** | Real-time calculation of available hotel rooms for specific check-in / check-out ranges. |
| **Concurrency Lock Mechanism** | Guaranteed capacity checks using atomic database transactions to eliminate race conditions. |
| **Audit Trails & Security** | Comprehensive administrative audit log capturing all high-risk operations and booking updates. |
| **RESTful API** | Clean endpoints for destinations, packages, hotels, and reservations with OpenAPI 3.0 schema. |

---

## 👥 Role-Based Portals

```
┌────────────────────────────────────────────────────────────────────────┐
│                        TravelEase Architecture                         │
├────────────────────┬────────────────────┬──────────────────────────────┤
│  👤 Customer       │  🏢 Travel Agent   │  🛡️ Platform Administrator    │
├────────────────────┼────────────────────┼──────────────────────────────┤
│ • Explore places   │ • Publish packages │ • Financial KPI analytics    │
│ • Book packages    │ • Track departures │ • System-wide bookings log   │
│ • Reserve rooms    │ • View manifests   │ • User & agent verification  │
│ • Printable ticket │ • Manage bookings  │ • Security audit trail       │
└────────────────────┴────────────────────┴──────────────────────────────┘
```

---

## 🖼️ User Interface Showcase

<div align="center">

### Home Page & Destinations
| Home Page | Destinations Catalog |
|:---:|:---:|
| ![Home Page](docs/screenshots/01_home_page.png) | ![Destinations Page](docs/screenshots/02_destinations_page.png) |

### Packages & Booking Experience
| Travel Packages | Booking Confirmation |
|:---:|:---:|
| ![Packages Page](docs/screenshots/03_packages_page.png) | ![Booking Confirmation](docs/screenshots/09_booking_confirmation.png) |

### Dedicated Role Dashboards
| Customer Dashboard | Agent Dashboard | Admin Analytics |
|:---:|:---:|:---:|
| ![Customer](docs/screenshots/07_customer_dashboard.png) | ![Agent](docs/screenshots/10_agent_dashboard.png) | ![Admin](docs/screenshots/11_admin_dashboard.png) |

</div>

---

## 📐 System Architecture & UML

### High-Level System Architecture

```mermaid
flowchart TD
    subgraph ClientLayer ["Client & Presentation Layer (HTML5, Bootstrap 5, JS)"]
        A1["Public Visitor / Traveler"]
        A2["Licensed Travel Agent"]
        A3["Platform Administrator"]
        A4["Third-Party API Clients / Swagger"]
    end

    subgraph SecurityRouting ["Security & Routing Layer (Django Middleware)"]
        B1["Security Middleware & SSL"]
        B2["CSRF Protection"]
        B3["Role-Based Access Controller (RBAC)"]
        B4["Session & Authentication Engine"]
    end

    subgraph ServiceLayer ["Application & Business Logic Layer (Django 5 + DRF)"]
        C1["Core & Administration Service"]
        C2["Accounts & Identity Manager"]
        C3["Destinations & Reviews Catalog"]
        C4["Travel Packages & Departures Engine"]
        C5["Hotels & Rooms Availability Engine"]
        C6["Bookings Engine (select_for_update)"]
        C7["Simulated Academic Payment Gateway"]
        C8["OpenAPI 3.0 / Swagger Documentation"]
    end

    subgraph DataStorageLayer ["Data Persistence & Storage Layer"]
        D1[("PostgreSQL 15+ / SQLite3 Engine")]
        D2[("Media & Static Asset Storage")]
        D3[("Security Audit Trail & Notification Queue")]
    end

    ClientLayer --> SecurityRouting
    SecurityRouting --> ServiceLayer
    ServiceLayer --> DataStorageLayer
```

<details>
<summary><b>🔍 Click to view Use Case Diagram</b></summary>

```mermaid
flowchart LR
    subgraph Actors
        T["Traveler / Customer"]
        A["Travel Agent"]
        ADM["Administrator"]
    end

    subgraph SystemUseCases ["TravelEase Platform Functions"]
        UC1["Search & Filter Destinations"]
        UC2["Browse Travel Packages & Inclusions"]
        UC3["Execute Multi-Step Package Booking"]
        UC4["Reserve Hotel Room (Overlap Checked)"]
        UC5["View Booking History & Receipts"]
        UC6["Cancel Booking (Release Seats)"]
        UC7["Publish Travel Package & Departures"]
        UC8["Inspect Passenger Manifests"]
        UC9["Update Reservation Status"]
        UC10["Monitor Live Revenue & Database KPIs"]
        UC11["Manage Users & Verification"]
        UC12["Inspect System Security Audit Trail"]
    end

    T --> UC1
    T --> UC2
    T --> UC3
    T --> UC4
    T --> UC5
    T --> UC6

    A --> UC7
    A --> UC8
    A --> UC9

    ADM --> UC10
    ADM --> UC11
    ADM --> UC12
```
</details>

<details>
<summary><b>🔍 Click to view Class Diagram</b></summary>

```mermaid
classDiagram
    class User {
        +String username
        +String email
        +String role (CUSTOMER, AGENT, ADMIN)
        +String phone
        +is_customer() bool
        +is_agent() bool
        +is_administrator() bool
    }

    class Destination {
        +String name
        +String description
        +Decimal estimated_cost
        +bool is_featured
    }

    class TravelPackage {
        +String title
        +int duration_days
        +Decimal price_per_person
        +String included_services
        +String excluded_services
    }

    class PackageDeparture {
        +Date departure_date
        +Date return_date
        +int total_capacity
        +int booked_seats
        +available_seats() int
        +reserve_seats(seats)
        +release_seats(seats)
    }

    class PackageBooking {
        +String booking_reference
        +int travelers_count
        +Decimal total_price
        +String status
        +cancel(reason)
    }

    class Traveler {
        +String first_name
        +String last_name
        +String passport_number
        +int age
        +String gender
    }

    class Hotel {
        +String name
        +int star_rating
        +String amenities
        +String address
    }

    class HotelRoom {
        +String room_type
        +Decimal price_per_night
        +int total_rooms
        +get_available_rooms_count(check_in, check_out) int
    }

    class HotelBooking {
        +String booking_reference
        +Date check_in
        +Date check_out
        +Decimal total_price
        +cancel(reason)
    }

    class PaymentRecord {
        +String transaction_id
        +Decimal amount
        +String status
        +String card_last_four
        +bool is_demo_simulation
    }

    User "1" --> "1" Destination : favorites
    User "1" --> "*" PackageBooking : places
    TravelPackage "1" --> "*" PackageDeparture : offers
    PackageDeparture "1" --> "*" PackageBooking : schedules
    PackageBooking "1" --> "*" Traveler : includes
    PackageBooking "1" --> "1" PaymentRecord : settles
    Hotel "1" --> "*" HotelRoom : supplies
    HotelRoom "1" --> "*" HotelBooking : reserves
    HotelBooking "1" --> "1" PaymentRecord : settles
```
</details>

<details>
<summary><b>🔍 Click to view Sequence Diagram (Concurrency-Safe Booking)</b></summary>

```mermaid
sequenceDiagram
    autonumber
    actor Traveler
    participant UI as Browser / Frontend
    participant View as BookingWizardView
    participant Dep as PackageDeparture Model
    participant DB as PostgreSQL Database
    participant Pay as PaymentLedger

    Traveler->>UI: Select departure date, number of travelers & enter passenger info
    Traveler->>UI: Click "Confirm Reservation"
    UI->>View: POST /packages/{id}/book/ (travelers manifest, simulated card)
    View->>DB: Begin Atomic Database Transaction
    View->>Dep: PackageDeparture.reserve_seats(departure_id, count)
    Dep->>DB: SELECT FOR UPDATE (acquire exclusive row lock)
    alt Available seats >= Requested seats
        Dep->>DB: UPDATE booked_seats = booked_seats + count
        View->>DB: INSERT INTO bookings_packagebooking (CONFIRMED)
        View->>DB: INSERT INTO bookings_traveler (for each passenger)
        View->>Pay: Record simulated academic transaction (TXN-SIM-XXXXX)
        Pay->>DB: INSERT INTO payments_paymentrecord (SUCCESS)
        DB-->>View: Commit Transaction
        View-->>UI: 302 Redirect to Booking Confirmation
        UI-->>Traveler: Render Confirmation Page & Print-Ready Receipt
    else Insufficient capacity
        DB-->>Dep: Capacity constraint failed
        View->>DB: Rollback Transaction
        View-->>UI: Return error alert: "Only X seats remain on this departure"
    end
```
</details>

<details>
<summary><b>🔍 Click to view Activity Diagram (Booking Lifecycle)</b></summary>

```mermaid
flowchart TD
    Start([Traveler Begins]) --> SearchDest[Browse Destinations or Search Keyword]
    SearchDest --> SelectPackage[Select Desired Travel Package]
    SelectPackage --> CheckDeparture[Choose Future Guaranteed Departure Date]
    CheckDeparture --> EnterTravelers[Enter Number & Manifest of Passengers]
    EnterTravelers --> CalcPrice[Real-Time Price Calculation Displayed]
    CalcPrice --> SubmitBooking[Submit Reservation Request]
    SubmitBooking --> AtomicLock{Atomic Lock Capacity Available?}
    
    AtomicLock -- No --> RejectBooking[Show Capacity Exceeded Error]
    RejectBooking --> CheckDeparture
    
    AtomicLock -- Yes --> ReserveSeats[Deduct Seats Atomically with select_for_update]
    ReserveSeats --> GenPayment[Simulate Safe Academic Payment Record]
    GenPayment --> GenRef[Generate Unique Booking Reference]
    GenRef --> ConfirmBooking[Mark Status: CONFIRMED]
    ConfirmBooking --> DisplayReceipt[Render Printable Confirmation & Pass Manifest]
    
    DisplayReceipt --> NeedCancel{Does Customer Request Cancellation?}
    NeedCancel -- No --> EndTrip([Traveler Completes Journey])
    NeedCancel -- Yes --> CheckPolicy{Is Departure Date in the Future?}
    CheckPolicy -- No --> RejectCancel[Cancellation Denied: Trip Started/Passed]
    CheckPolicy -- Yes --> RestoreSeats[Atomically Release Seats to Inventory]
    RestoreSeats --> MarkCancelled[Update Status: CANCELLED]
    MarkCancelled --> EndTrip
```
</details>

---

## 🛠️ Technology Stack

- **Backend:** Python 3.10+, Django 5.x, Django REST Framework 3.18
- **Database:** PostgreSQL 15+ (Production / Docker) & SQLite3 (Development)
- **API Documentation:** `drf-spectacular` (OpenAPI 3.0 / Swagger UI / ReDoc)
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5.3, Bootstrap Icons
- **Typography & Brand:** Inter & Plus Jakarta Sans, Deep Navy (`#0f2444`), Turquoise (`#0891b2`), Warm Orange (`#f97316`)
- **DevOps & Containers:** Docker, Docker Compose, Gunicorn, Nginx
- **Testing:** Django Test Suite, `pytest` (19 automated tests, 100% pass)

---

## 🚀 Quick Start & Installation

### Option A: One-Click Script (Windows)
Simply run the included helper batch file:
```cmd
setup_and_run.bat
```
This automatically verifies Python, creates the virtual environment, installs dependencies, runs migrations, and opens the application in your browser.

### Option B: Manual Setup
```bash
# 1. Clone the repository
git clone https://github.com/Alaa-Eriby/TravelEase.git
cd TravelEase

# 2. Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run database migrations
python manage.py migrate

# 5. Populate sample demonstration data
python manage.py seed_data

# 6. Start development server
python manage.py runserver 127.0.0.1:8000
```
Visit **`http://127.0.0.1:8000/`** in your browser.

### Option C: Docker Deployment
```bash
docker-compose up --build
```

---

## 🔑 Demonstration Accounts

The platform includes pre-configured demo accounts loaded via `python manage.py seed_data`:

| Role | Username | Password | Access Scope |
|---|---|---|---|
| 🛡️ **Administrator** | `admin` | `AdminPass123!` | Full control, financial KPIs, user roles & audit logs |
| 🏢 **Travel Agent** | `agent_sarah` | `AgentPass123!` | Package management, manifests & reservation updates |
| 👤 **Traveler / Customer** | `traveler_john` | `TravelerPass123!` | Destination browsing, booking wizard & receipts |

---

## 📡 REST API & Swagger

TravelEase exposes full REST APIs with interactive documentation:

- **Swagger UI:** [`http://127.0.0.1:8000/api/docs/`](http://127.0.0.1:8000/api/docs/)
- **ReDoc:** [`http://127.0.0.1:8000/api/redoc/`](http://127.0.0.1:8000/api/redoc/)
- **OpenAPI Schema:** Generated via `schema.yml`

---

## 🧪 Automated Testing

Run the full automated test suite covering authentication, concurrency locks, booking wizards, and API endpoints:
```bash
python manage.py test
```
```
Found 19 test(s).
System check identified no issues (0 silenced).
...................
----------------------------------------------------------------------
Ran 19 tests in 69.412s

OK (19 passed, 0 failed)
```

---

## 📚 Project Documentation

Detailed technical documentation is available in the [`docs/`](docs/) directory:

- 📘 **[Installation Guide](INSTALLATION.md)** — Comprehensive setup instructions
- 🗄️ **[Database Documentation & ERD](docs/DATABASE_DOCUMENTATION.md)** — Relational schemas and data dictionary
- 🔌 **[API Documentation](docs/API_DOCUMENTATION.md)** — Endpoint definitions and payload samples
- 🧪 **[Testing & QA Report](docs/TESTING_REPORT.md)** — Test cases and verification evidence
- 📖 **[User Guide](docs/USER_GUIDE.md)** — Step-by-step role walkthroughs
- 🐳 **[Deployment & Docker Guide](docs/DEPLOYMENT_GUIDE.md)** — Production deployment workflows

---

<div align="center">
  <sub>TravelEase • Software Construction Course Capstone • Developed with ❤️ by Alaa Eriby </sub>
</div>
