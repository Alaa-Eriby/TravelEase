# TravelEase – REST API Specification & OpenAPI Documentation

### 1. Interactive Documentation Surfaces
TravelEase comes equipped with automated Swagger / OpenAPI 3.0 interfaces generated via `drf-spectacular`:
- **Swagger UI Interactive Console:** `http://localhost:8000/api/docs/`
- **ReDoc Technical Interface:** `http://localhost:8000/api/redoc/`
- **Raw OpenAPI Schema (JSON/YAML):** `http://localhost:8000/api/schema/`

---

### 2. Authentication & Authorization
All endpoints requiring user context accept standard HTTP Session authentication or Basic authentication.
Role-based permission classes enforce access levels:
- **Public:** Destination listings, packages, hotels, reviews, country/city directories.
- **Authenticated (Customer):** Personal dashboard, bookings creation, reviews submission, favorites toggle.
- **Agent:** Managing owned packages, departure schedules, reviewing passengers.
- **Admin:** System analytics, full CRUD operations, audit log review.

---

### 3. Core REST Endpoints Summary

#### A. User Accounts & Profiles
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/accounts/api/register/` | Register new customer or travel agent | No |
| `GET` | `/accounts/api/profile/` | Fetch current logged-in profile | Yes |
| `PUT/PATCH` | `/accounts/api/profile/` | Update personal profile information | Yes |

#### B. Destinations & Reviews
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/destinations/api/countries/` | List all available countries | No |
| `GET` | `/destinations/api/cities/` | List all available cities | No |
| `GET` | `/destinations/api/destinations/` | List destinations with filtering (`q`, `country`, `min_price`) | No |
| `GET` | `/destinations/api/destinations/{id}/` | Retrieve destination details and galleries | No |
| `GET` | `/destinations/api/reviews/` | List approved user reviews | No |
| `POST` | `/destinations/api/reviews/` | Submit a review for a destination, package, or hotel | Yes |
| `GET` | `/destinations/api/favorites/` | List current user's favorite destinations | Yes |
| `POST` | `/destinations/api/favorites/` | Add destination to user's favorites | Yes |

#### C. Travel Packages & Departures
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/packages/api/packages/` | List packages with filters (`destination`, `duration`, `price`) | No |
| `GET` | `/packages/api/packages/{id}/` | Get full package details, inclusions, exclusions | No |
| `POST` | `/packages/api/packages/` | Create a new package (Agent/Admin only) | Yes (Agent) |
| `GET` | `/packages/api/departures/` | List upcoming scheduled departures and capacities | No |
| `POST` | `/packages/api/departures/` | Add departure date and capacity | Yes (Agent) |

#### D. Hotels & Rooms
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/hotels/api/hotels/` | List verified hotels with destination filtering | No |
| `GET` | `/hotels/api/hotels/{id}/` | Get hotel details, amenities, and room categories | No |
| `GET` | `/hotels/api/rooms/` | List room categories and nightly pricing | No |

#### E. Bookings Engine & Simulated Transactions
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/bookings/api/package-bookings/` | List user's package bookings (or all for admin) | Yes |
| `POST` | `/bookings/api/package-bookings/` | Book package with traveler manifest & seat lock | Yes |
| `POST` | `/bookings/api/package-bookings/{id}/cancel/` | Atomic cancellation and seat release | Yes |
| `GET` | `/bookings/api/hotel-bookings/` | List user's hotel reservations | Yes |
| `POST` | `/bookings/api/hotel-bookings/` | Reserve hotel room with date overlap check | Yes |
| `POST` | `/bookings/api/hotel-bookings/{id}/cancel/` | Cancel hotel reservation | Yes |
| `GET` | `/payments/api/records/` | List academic simulated payment receipts | Yes |

#### F. Core, Audits & Notifications
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/contact/` | Submit contact inquiry | No |
| `GET` | `/api/audit-logs/` | Retrieve system security audit log | Yes (Admin) |
| `GET` | `/api/notifications/` | Retrieve user notification alerts | Yes |
