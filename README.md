# TravelEase – Smart Travel and Tourism Booking System
## Software Construction Course – Complete Practical Implementation Capstone

[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.18-red.svg)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%20%7C%20SQLite-blue.svg)](https://www.postgresql.org/)
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0%20Swagger-brightgreen.svg)](http://localhost:8000/api/docs/)
[![Tests](https://img.shields.io/badge/Tests-19%20Passed%20(100%25)-success.svg)](docs/TESTING_REPORT.md)

---

### 1. Project Concept & Executive Summary

**TravelEase** is an enterprise-grade travel and tourism booking web application developed for the university Software Construction course. It delivers a genuinely functional, database-connected commercial platform that connects travelers with licensed tourism service providers and central administrators.

The system features real concurrency-safe capacity locks, dynamic room inventory tracking, an academic safe payment ledger, and dedicated role portals for **Customers**, **Travel Agents**, and **Platform Administrators**.

---

### 2. High-Level System Architecture Diagram

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

---

### 3. Use Case Diagram

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
        UC3["Execute 12-Step Package Booking"]
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

---

### 4. Class Diagram

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
    TravelPackage "1" --> "*" PackageDeparture : schedules
    PackageDeparture "1" --> "*" PackageBooking : books
    PackageBooking "1" --> "*" Traveler : manifests
    PackageBooking "1" --> "1" PaymentRecord : settles
    Hotel "1" --> "*" HotelRoom : supplies
    HotelRoom "1" --> "*" HotelBooking : reserves
    HotelBooking "1" --> "1" PaymentRecord : settles
```

---

### 5. Sequence Diagram: Concurrency-Safe Travel Package Booking

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

---

### 6. Activity Diagram: Travel Booking Lifecycle

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

---

### 7. Technology Stack
- **Backend Framework:** Python 3.10+, Django 5.x, Django REST Framework 3.18.
- **API Documentation:** `drf-spectacular` (OpenAPI 3.0 / Swagger UI / ReDoc).
- **Frontend Stack:** HTML5, CSS3, Bootstrap 5.3, Bootstrap Icons, Custom Visual Identity (Inter & Plus Jakarta Sans typography, deep navy `#0f2444`, turquoise `#0891b2`, warm orange `#f97316`).
- **Database:** PostgreSQL 15+ (Production / Docker) & SQLite3 (instant zero-configuration local runs).
- **Deployment:** Docker & Docker Compose (`docker-compose.yml`), Gunicorn, Nginx.
- **Testing:** Django Test Suite & `pytest` (19 automated unit & integration test cases with 100% pass rate).

---

### 8. Installation & Quick Start

```powershell
# 1. Activate virtual environment
.\venv\Scripts\activate

# 2. Run database migrations
python manage.py migrate

# 3. Seed demonstration database
python manage.py seed_data

# 4. Start local development server
python manage.py runserver 127.0.0.1:8000
```
Open **`http://localhost:8000/`** in your browser.

---

### 9. Demonstration Credentials
- **Administrator:** `admin` / `AdminPass123!`
- **Travel Agent:** `agent_sarah` / `AgentPass123!`
- **Traveler:** `traveler_john` / `TravelerPass123!`

---

### 10. Automated Test Results
Run the test suite with:
```powershell
python manage.py test
```
**Results:** `Ran 19 tests in 69s. OK (19 passed, 0 failed)`.

---

### 11. Documentation Pointers
- **[Installation Guide](INSTALLATION.md)**
- **[Database Documentation & ERD](docs/DATABASE_DOCUMENTATION.md)**
- **[API Documentation & Swagger](docs/API_DOCUMENTATION.md)**
- **[Testing & QA Report](docs/TESTING_REPORT.md)**
- **[User Guide & Demonstration Steps](docs/USER_GUIDE.md)**
- **[Deployment & Docker Guide](docs/DEPLOYMENT_GUIDE.md)**
#   T r a v e l E a s e  
 