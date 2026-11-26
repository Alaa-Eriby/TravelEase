# TravelEase – User Guide & Academic Demonstration Walkthrough

### 1. Default Demonstration Credentials
TravelEase comes pre-seeded with three verified personas for academic evaluation:

| Role | Username | Password | Purpose |
|---|---|---|---|
| **Administrator** | `admin` | `AdminPass123!` | System operations, live revenue metrics, audit trail, user CRUD |
| **Travel Agent** | `agent_sarah` | `AgentPass123!` | Alpine & European Escapes agency, create packages & departures |
| **Traveler** | `traveler_john` | `TravelerPass123!` | Sample customer with active Swiss Alps reservation and favorites |
| **Traveler #2** | `traveler_emma` | `TravelerPass123!` | Sample customer with active Paris luxury hotel booking |

---

### 2. Role Walkthroughs

#### A. Customer / Traveler Experience
1. **Explore Destinations:**
   - Navigate to `/destinations/`. Filter by Country or budget range.
   - Click **Explore Packages & Hotels** to view full attractions, reviews, and related trips.
   - Toggle the **Heart** icon to save a destination to your favorites.
2. **Booking a Travel Package (12-Step Process):**
   - Click **Book Trip** on any package (e.g. *Grand Swiss Alpine Expedition*).
   - Select an upcoming departure date.
   - Select the number of travelers (1 to 5). Notice how the passenger manifest form dynamically renders fields for each passenger.
   - Enter traveler names, passports, and ages.
   - View the calculated live price.
   - Confirm reservation. A unique booking reference (e.g. `TE-PKG-XXXXXXXX`) is generated, seats are locked, and a simulated payment record is created.
   - Print or review your official travel receipt.
3. **Reserving a Hotel Room:**
   - Navigate to `/hotels/`. Select a property (e.g. *The Alpina Grand Lodge*).
   - Enter your intended check-in and check-out dates to view real database availability.
   - Click **Reserve Room**, enter guest counts, and confirm.
4. **Self-Service Customer Dashboard:**
   - Navigate to `/bookings/dashboard/` to view upcoming trips, past trips, payment receipts, and favorite destinations.
   - Click **Cancel** on any eligible booking to automatically release seats back to the public pool.

#### B. Travel Agent Experience
1. **Accessing Agent Portal:**
   - Sign in with `agent_sarah` / `AgentPass123!`.
   - The system automatically routes you to `/agent/dashboard/`.
2. **Publishing New Travel Packages:**
   - Click **Create Travel Package** to set up itinerary description, inclusions, exclusions, price per person, and duration.
3. **Managing Departures & Capacities:**
   - On any package, click **+ Departure Date** to schedule new departures with custom traveler capacities.
4. **Customer Passenger Manifest:**
   - View customer reservations, passenger names, and update statuses to `COMPLETED` or `CANCELLED`.

#### C. Administrator Experience
1. **Accessing Executive Dashboard:**
   - Sign in with `admin` / `AdminPass123!`.
   - The platform redirects you to `/admin-panel/`.
2. **Live System Metrics:**
   - Inspect live database statistics: Total recorded booking revenue, total reservations, confirmed vs cancelled bookings, customer accounts, and agency accounts.
3. **User Management:**
   - Filter users by role (`Customer`, `Travel Agent`, `Administrator`).
4. **Contact Messages & Audit Logs:**
   - Review incoming contact inquiries and mark them as resolved.
   - Inspect the real-time security audit trail capturing every login, booking, cancellation, and registration.
