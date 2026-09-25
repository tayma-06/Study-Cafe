# Study Café

A web-based study café management platform that allows customers to browse study zones, check seat availability, make time-based bookings, manage café services, and handle payments.

## Overview

Study Café is built around a **FastAPI + React + PostgreSQL** architecture. PostgreSQL handles a significant portion of the application's business logic through functions, procedures, triggers, constraints, and views.

### Functionalities

* User registration and login
* Zone and seat browsing
* Time-based seat availability checking
* Seat booking with double-booking prevention
* Booking cancellation
* Check-in and check-out
* Booking history
* Café service management
* Automatic price calculation
* Payment management
* Booking and payment status tracking
* Role-based access control (customer, receptionist, admin)
* Desk bookings at reception for customers, new accounts, and walk-in guests
* Simulated bKash payment requests with staff approval/rejection
* Cash payment collection at reception
* Admin management of zones, seats, services, and receptionist accounts

## Tech Stack

* **Frontend:** React
* **Backend:** FastAPI
* **Database:** PostgreSQL
* **Database Driver:** Psycopg
* **Authentication:** JWT
* **Password Hashing:** bcrypt
* **API Documentation:** Swagger UI / OpenAPI

## Project Structure

```text
Study-Cafe/
│
├── backend/
│   ├── auth.py           # JWT authentication
│   ├── database.py       # Database connection pool
│   ├── models.py         # Pydantic models
│   ├── schemas.py        # Request/response schemas
│   ├── routes.py         # API routes
│   ├── main.py           # FastAPI app entry point
│   └── create_admin.py   # Admin creation script
│
├── database/
│   ├── schema.sql        # Tables, types, domains
│   ├── functions.sql     # Database functions
│   ├── triggers.sql      # Database triggers
│   ├── procedures.sql    # Stored procedures
│   ├── views.sql         # Database views
│   └── seed.sql          # Initial data
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.example
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── index.css
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── components/
│   │   ├── pages/
│   │   ├── styles/
│   │   └── utils/
│   └── tests/
│       ├── customer-flow.mjs
│       └── staff-flow.mjs
│
├── docs/
│   └── SETUP.md
│
├── .env.example          # Backend environment template
├── .env                  # Backend environment (gitignored)
├── requirements.txt      # Python dependencies
└── README.md
```

* **Backend** — FastAPI application
* **Frontend** — React application
* **Database** — PostgreSQL database scripts and database logic

---

<details>
<summary><strong>API Endpoints</strong></summary>

### Authentication & Users

| Method | Endpoint           | Description                        |
| ------ | ------------------ | ---------------------------------- |
| POST   | `/users`           | Register a new user                |
| POST   | `/login`           | Log in and receive an access token |
| GET    | `/users`           | Get all users — Admin              |
| GET    | `/users/{user_id}` | Get user information — Self/Admin  |

### Zones & Seats

| Method | Endpoint                 | Description                         |
| ------ | ------------------------ | ----------------------------------- |
| GET    | `/zones`                 | Get all study zones                 |
| GET    | `/zones/{zone_id}/seats` | Get seats in a zone                 |
| GET    | `/seats`                 | Get all seats                       |
| GET    | `/seats/{seat_id}`       | Get a specific seat                 |
| GET    | `/availability`          | Get available seats for a date/time |

### Bookings

| Method | Endpoint                           | Description                       |
| ------ | ---------------------------------- | --------------------------------- |
| POST   | `/bookings`                        | Create a booking                  |
| GET    | `/bookings/me`                     | Get current user's bookings       |
| GET    | `/users/{user_id}/bookings`        | Get user's bookings — Self/Admin  |
| GET    | `/bookings/{booking_id}`           | Get booking details — Owner/Admin |
| POST   | `/bookings/{booking_id}/cancel`    | Cancel a booking                  |
| POST   | `/bookings/{booking_id}/check-in`  | Check in                          |
| POST   | `/bookings/{booking_id}/check-out` | Check out                         |

### Services

| Method | Endpoint                          | Description                 |
| ------ | --------------------------------- | --------------------------- |
| GET    | `/services`                       | Get available café services |
| POST   | `/bookings/{booking_id}/services` | Add services to a booking   |

### Payments

| Method | Endpoint                 | Description                                                           |
| ------ | ------------------------ | --------------------------------------------------------------------- |
| POST   | `/payments`              | Deprecated — returns 410; use payment requests or staff cash collection |
| GET    | `/payments/{booking_id}` | Get payment information                                               |
| POST   | `/payment-requests`      | Submit a simulated bKash transaction for staff approval               |
| GET    | `/payment-requests`      | Get transaction history (own, or all for staff)                       |

### Pricing

| Method | Endpoint                       | Description                 |
| ------ | ------------------------------ | --------------------------- |
| GET    | `/bookings/{booking_id}/price` | Get booking price breakdown |

### Staff & Admin

| Method | Endpoint                                          | Description                                         |
| ------ | ------------------------------------------------- | --------------------------------------------------- |
| POST   | `/admin/receptionists`                            | Create a receptionist account — Admin               |
| POST   | `/admin/users/{user_id}/role`                     | Grant or remove receptionist access — Admin         |
| POST   | `/admin/zones`                                    | Create or update a zone — Admin                     |
| POST   | `/admin/seats`                                    | Create or update a seat — Admin                     |
| POST   | `/admin/services`                                 | Create or update a service — Admin                  |
| GET    | `/staff/customers`                                | Search customer accounts — Staff                    |
| POST   | `/staff/bookings`                                 | Create a booking (customer, new account, or guest)  |
| GET    | `/staff/bookings`                                 | Staff booking and transaction dashboard             |
| GET    | `/staff/summary`                                  | Staff dashboard totals (today's bookings/revenue)   |
| POST   | `/staff/payment-requests/{transaction_id}/review` | Approve or reject a payment request — Staff         |
| POST   | `/staff/payments/cash`                            | Record cash received — Staff                        |

</details>

---

<details>
<summary><strong>Database Schema</strong></summary>

### Tables

#### `users`

Stores customer, receptionist, and administrator accounts.

* `user_id` — BIGINT, Primary Key (generated: YYYYMMDD + sequence)
* `name` — TEXT, NOT NULL
* `email` — TEXT, UNIQUE, NOT NULL
* `password` — TEXT, NOT NULL (bcrypt hashed)
* `role` — `user_role`
* `work_email` — TEXT, staff login email for receptionists
* `created_at` — TIMESTAMP

#### `zones`

Stores study café zones.

* `zone_id` — SERIAL, Primary Key
* `name` — TEXT
* `description` — TEXT
* `price_per_hour` — NUMERIC
* `facilities` — TEXT[]

#### `seats`

Stores individual study seats.

* `seat_id` — SERIAL, Primary Key
* `zone_id` — INT, Foreign Key → `zones`
* `seat_number` — TEXT
* `status` — `seat_status`

Constraint:
```text
UNIQUE(zone_id, seat_number)
```

#### `bookings`

Stores time-based seat reservations.

* `booking_id` — NUMERIC(12,4), Primary Key (generated: YYYYMMDD.####)
* `user_id` — BIGINT, Foreign Key → `users` (nullable for guest bookings)
* `seat_id` — INT, Foreign Key → `seats`
* `time_slot` — TSTZRANGE
* `status` — `booking_status`
* `checked_in_at` — TIMESTAMPTZ
* `checked_out_at` — TIMESTAMPTZ
* `guest_name` — TEXT
* `guest_phone` — TEXT
* `guest_email` — TEXT
* `created_by` — BIGINT, Foreign Key → `users` (staff who made the booking)
* `hourly_rate` — NUMERIC, the price per hour locked at booking time
* `created_at` — TIMESTAMPTZ

#### `services`

Stores additional café services.

* `service_id` — SERIAL, Primary Key
* `name` — TEXT
* `description` — TEXT
* `price` — NUMERIC

#### `booking_services`

Connects bookings with services.

* `booking_id` — NUMERIC(12,4), Foreign Key → `bookings`
* `service_id` — INT, Foreign Key → `services`
* `quantity` — INT
* `unit_price` — NUMERIC

Primary Key:
```text
(booking_id, service_id)
```

#### `payments`

Stores booking payment information.

* `payment_id` — BIGINT, Primary Key
* `booking_id` — NUMERIC(12,4), Foreign Key → `bookings`, UNIQUE
* `amount` — NUMERIC
* `method` — `payment_method`
* `status` — `payment_status`
* `received_by` — BIGINT, Foreign Key → `users` (staff who approved/recorded the payment)
* `paid_at` — TIMESTAMPTZ
* `created_at` — TIMESTAMPTZ

#### `payment_requests`

Stores simulated bKash transactions awaiting staff approval.

* `transaction_id` — TEXT, Primary Key
* `booking_id` — NUMERIC(12,4), NOT NULL, Foreign Key → `bookings`
* `amount` — NUMERIC(10,2), NOT NULL
* `method` — `payment_method`
* `provider` — TEXT
* `phone` — TEXT, NOT NULL
* `status` — TEXT (`pending`, `approved`, `rejected`)
* `submitted_by` — BIGINT, NOT NULL, Foreign Key → `users`
* `reviewed_by` — BIGINT, Foreign Key → `users`
* `review_note` — TEXT
* `reviewed_at` — TIMESTAMPTZ
* `created_at` — TIMESTAMPTZ

Constraint: only one `pending`/`approved` request per booking.

### Relationships

```text
users
  │
  └──< bookings >── seats ──> zones
          │
          ├──< booking_services >── services
          │
          ├── payments
          │
          └──< payment_requests (pending approval) ──> users (reviewer)
```

</details>

---

<details>
<summary><strong>Custom Types & Domains</strong></summary>

### `user_role`
```text
admin
customer
receptionist
```

### `booking_status`
```text
pending
confirmed
checked_in
checked_out
canceled
```

### `seat_status`
```text
available
unavailable
```

### `payment_status`
```text
pending
completed
failed
```

### `payment_method`
```text
credit_card
mobile_banking
cash
```

### `price_breakdown`

Composite type containing:
```text
base_price
service_cost
total_price
```

</details>

---

<details>
<summary><strong>Database Functions</strong></summary>

| Function                    | Purpose                                                             |
| --------------------------- | ------------------------------------------------------------------- |
| `generate_user_id()`        | Generates a date-based user ID (YYYYMMDD + sequence)                |
| `generate_booking_id()`     | Generates a date-based booking ID (YYYYMMDD.####)                   |
| `generate_payment_id()`     | Handles payment ID initialization (auto-generated)                  |
| `calculate_booking_price()` | Calculates the base booking cost using locked hourly rate           |
| `calculate_service_cost()`  | Calculates the total service cost for a booking                     |
| `calculate_total_price()`   | Returns complete price breakdown (composite type `price_breakdown`) |
| `update_booking_status()`   | Updates seat availability based on booking status changes           |
| `update_payment_status()`   | Updates booking status based on payment status changes              |
| `check_seat_availability()` | Checks whether a seat is available for a time slot                  |
| `get_available_seats()`     | Returns available seats for a requested time slot and optional zone |
| `check_login_email()`       | Prevents duplicate login emails across customer and staff accounts  |
| `protect_booking_payment()` | Locks the booked hourly rate and guards cancellations during payment review |
| `protect_booking_services()` | Blocks service changes once a payment has been submitted            |

</details>

---

<details>
<summary><strong>Stored Procedures</strong></summary>

| Procedure                   | Purpose                                                     |
| --------------------------- | ----------------------------------------------------------- |
| `create_booking()`          | Creates a booking with seat availability check and adds services |
| `cancel_booking()`          | Cancels a booking                                           |
| `check_in_booking()`        | Checks in a confirmed booking                               |
| `check_out_booking()`       | Checks out a checked-in booking                             |
| `add_services_to_booking()` | Adds services to an existing booking                        |
| `create_payment()`          | Creates a payment and updates booking status when completed |

</details>

---

<details>
<summary><strong>Database Views</strong></summary>

| View              | Purpose                                                           |
| ----------------- | ----------------------------------------------------------------- |
| `user_bookings`   | Customer booking history with seat, zone, and payment information |
| `available_seats` | Currently available seats with zone and pricing information       |
| `admin_bookings`  | Detailed booking information for administrative use               |
| `payment_summary` | Payment information with booking and customer details             |
| `service_usage`   | Service usage, quantities, unit prices, and service totals        |

</details>

---

<details>
<summary><strong>Database Triggers</strong></summary>

| Trigger                     | Event                       | Function                  |
| --------------------------- | --------------------------- | ------------------------- |
| `trg_generate_user_id`      | BEFORE INSERT on `users`    | `generate_user_id()`      |
| `trg_generate_booking_id`   | BEFORE INSERT on `bookings` | `generate_booking_id()`   |
| `trg_booking_status_update` | AFTER UPDATE on `bookings`  | `update_booking_status()` |
| `trg_payment_status_update` | AFTER UPDATE on `payments`  | `update_payment_status()` |
| `trg_check_login_email`     | BEFORE INSERT/UPDATE on `users` | `check_login_email()`   |
| `trg_protect_booking_payment` | BEFORE INSERT/UPDATE on `bookings` | `protect_booking_payment()` |
| `trg_protect_booking_services` | BEFORE INSERT/UPDATE/DELETE on `booking_services` | `protect_booking_services()` |

</details>

---

<details>
<summary><strong>Business Rules & Data Integrity</strong></summary>

### Authentication
* Email addresses must be unique, including across customer login emails and receptionist work emails.
* Receptionists log in with their café `work_email`; login emails are cross-checked by a trigger.
* Passwords are stored using bcrypt hashing.
* JWT authentication is used for protected API operations.
* Users can access their own protected resources.
* Admin users have additional management access; receptionists have staff access.

### Booking
* A booking belongs to a specific user and seat, or to a walk-in guest (guest details required).
* Bookings use PostgreSQL `TSTZRANGE` for time slots.
* A seat cannot have overlapping non-canceled bookings (enforced by exclusion constraint).
* The `hourly_rate` is locked at booking time so later zone price changes do not alter the price.
* Only valid booking status transitions are allowed.
* Confirmed bookings can be checked in.
* Checked-in bookings can be checked out.
* Bookings can be canceled.

### Services
* Services can be attached to bookings.
* Each booking-service combination is unique.
* Service quantities and prices are stored with the booking service.

### Payments
* A booking can have at most one payment.
* Payment methods are restricted to the defined `payment_method` domain.
* Payment statuses are restricted to the defined `payment_status` domain.
* A completed payment can confirm a pending booking.
* Mobile payments are simulated as `payment_requests` that staff must approve or reject.
* Services cannot change once a payment request is pending or the booking is paid.
* Paid bookings require a refund process instead of cancellation.

</details>

---

<details>
<summary><strong>API Documentation</strong></summary>

When the FastAPI backend is running, interactive API documentation is available through:
```
http://127.0.0.1:8000/docs
```

OpenAPI specification:
```
http://127.0.0.1:8000/openapi.json
```

</details>

---

## Quick Start

See **[SETUP.md](docs/SETUP.md)** for complete setup instructions including:
- Local development setup (backend + frontend)
- Database initialization
- Render deployment guide
- Environment variable reference
- Troubleshooting

## Architecture

```text
┌─────────────────────┐
│      React UI       │
└──────────┬──────────┘
           │ HTTP / JSON
           ▼
┌─────────────────────┐
│      FastAPI        │
│                     │
│ Routes / Auth       │
│ Schemas / Models    │
└──────────┬──────────┘
           │ Psycopg
           ▼
┌────────────────────────────┐
│        PostgreSQL          │
│                            │
│ Tables                     │
│ Functions                  │
│ Procedures                 │
│ Triggers                   │
│ Views                      │
│ Constraints                │
└────────────────────────────┘
```