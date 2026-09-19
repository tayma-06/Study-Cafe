# Study Café — Development Plan

Complete implementation checklist for the Study Café Slot Booking & Management System.

---

# 1. Project Scope

## 1.1 Objective

- [x] Build a web-based study café booking and management system
- [x] Allow customers to browse zones and seats
- [x] Allow customers to check seat availability
- [x] Allow customers to book seats for a selected time period
- [x] Allow customers to add café services to bookings
- [x] Calculate booking costs automatically
- [x] Allow customers to view and manage bookings
- [x] Allow customers to check in and check out
- [x] Record and track payments
- [ ] Allow administrators to manage café resources
- [x] Enforce booking integrity through PostgreSQL

## 1.2 User Roles

### Customer

- [x] Register
- [x] Login
- [x] View zones
- [x] View seats
- [x] Check availability
- [ ] Select a seat
- [x] Create a booking
- [x] Add services
- [x] View booking cost
- [x] Record payment
- [x] Cancel booking
- [x] Check in
- [x] Check out
- [x] View booking history

### Admin

- [ ] Login
- [ ] View dashboard
- [ ] Manage zones
- [ ] Manage seats
- [ ] Manage seat availability/status
- [ ] Manage pricing
- [ ] Manage services
- [ ] View all bookings
- [ ] Manage bookings
- [ ] Monitor payments

---

# 2. System Architecture

## 2.1 Technology Stack

- [x] React
- [x] FastAPI
- [x] PostgreSQL
- [x] Vite
- [x] Python
- [x] JavaScript/JSX

## 2.2 Architecture

```text
React Frontend
      │
      ▼
FastAPI Backend
      │
      ▼
PostgreSQL
      │
      ├── Tables
      ├── Domains
      ├── Composite Types
      ├── Range Types
      ├── Constraints
      ├── Indexes
      ├── Functions
      ├── Procedures
      ├── Triggers
      └── Views
```

## 2.3 Responsibility

- [x] React handles presentation and user interaction
- [x] React sends requests to FastAPI
- [x] FastAPI validates requests
- [ ] FastAPI handles authentication and authorization
- [x] FastAPI communicates with PostgreSQL
- [x] PostgreSQL enforces data integrity
- [x] PostgreSQL prevents overlapping bookings
- [x] PostgreSQL performs authoritative booking calculations
- [x] Frontend must not be trusted for prices or booking status

---

# 3. Database Design

## 3.1 Required Tables

The database contains exactly seven main tables.

- [x] `users`
- [x] `zones`
- [x] `seats`
- [x] `bookings`
- [x] `services`
- [x] `booking_services`
- [x] `payments`

Do not create separate tables for:

- [x] maintenance
- [x] slots
- [x] facilities
- [x] pricing
- [x] booking history

These concepts are handled using existing tables, fields, PostgreSQL types, constraints, functions, or views.

---

# 4. Table Design

## 4.1 users

Purpose: store customer and administrator accounts.

- [x] `user_id` primary key
- [x] `name`
- [x] `email`
- [x] `password_hash`
- [x] `role`
- [x] `created_at`
- [x] Unique email constraint
- [x] Valid role constraint/domain

Relationship:

```text
users 1 ──────── N bookings
```

---

## 4.2 zones

Purpose: represent different study areas.

Examples:

* Quiet Zone
* Group Study Zone
* Premium Zone

Fields:

- [x] `zone_id` primary key
- [x] `name`
- [x] `description`
- [x] `facilities`
- [x] `price`
- [x] `status` if required
- [x] Unique zone name

PostgreSQL feature:

- [x] Store facilities using `TEXT[]`

Relationship:

```text
zones 1 ──────── N seats
```

---

## 4.3 seats

Purpose: represent individual study seats.

Fields:

- [x] `seat_id` primary key
- [x] `zone_id` foreign key
- [x] `seat_number`
- [x] `status`

Rules:

- [x] Every seat belongs to one zone
- [x] Seat number is unique within a zone
- [x] Invalid zone references are rejected
- [x] Unavailable seats cannot be booked

Relationship:

```text
seats 1 ──────── N bookings
```

---

## 4.4 bookings

Purpose: store customer seat reservations.

Fields:

- [x] `booking_id` primary key
- [x] `user_id` foreign key
- [x] `seat_id` foreign key
- [x] `time_slot`
- [x] `status`
- [x] `booking_cost`
- [x] `created_at`
- [x] `check_in_at`
- [x] `check_out_at`
- [x] Cancellation information if required

Use:

```text
tstzrange
```

for `time_slot`.

Example:

```text
[2026-09-10 10:00, 2026-09-10 14:00)
```

Rules:

- [x] Start must be before end
- [x] Booking duration must be valid
- [x] Canceled bookings do not block availability
- [x] Same seat cannot have overlapping active bookings

Relationship:

```text
users ──────── bookings
seats ──────── bookings
```

---

## 4.5 services

Purpose: café services that customers can add to bookings.

Examples:

* Coffee
* Snacks
* Printing

Fields:

- [x] `service_id` primary key
- [x] `name`
- [x] `description`
- [x] `price`
- [x] `status`

Rules:

- [x] Service name should be unique
- [x] Price must be non-negative
- [x] Disabled services cannot be newly selected

---

## 4.6 booking_services

Purpose: many-to-many relationship between bookings and services.

Fields:

- [x] `booking_id` foreign key
- [x] `service_id` foreign key
- [x] `quantity`
- [x] `service_price`

Rules:

- [x] Quantity must be positive
- [x] Store service price at booking time
- [x] Calculate service subtotal

Relationship:

```text
bookings N ──────── N services
```

through:

```text
booking_services
```

---

## 4.7 payments

Purpose: record payments associated with bookings.

Fields:

- [x] `payment_id` primary key
- [x] `booking_id` foreign key
- [x] `amount`
- [x] `payment_method`
- [x] `payment_status`
- [x] `transaction_reference`
- [x] `paid_at`

Rules:

- [x] Payment amount must be valid
- [x] Payment must belong to a valid booking
- [x] Customer cannot access another customer's payment
- [x] Payment status must use valid values

---

# 5. PostgreSQL Features

## 5.1 Domains

Create domains for controlled values.

- [x] `user_role`
- [x] `booking_status`
- [x] `seat_status`
- [x] `payment_status`
- [x] `payment_method`

Example:

```sql
CREATE DOMAIN user_role AS TEXT
CHECK (VALUE IN ('admin', 'customer'));
```

---

## 5.2 Composite Type

Create a composite type for booking price information.

- [x] Define `price_breakdown`
- [x] Include base booking cost
- [x] Include service cost
- [x] Include final total
- [x] Use it where appropriate in database functions

Example structure:

```text
price_breakdown
├── base_cost
├── service_cost
└── total_cost
```

---

## 5.3 Range Type

Use:

```text
tstzrange
```

for booking periods.

- [x] Use half-open ranges
- [x] Validate start < end
- [x] Use range operators for availability checking
- [x] Use range overlap operator `&&`

---

## 5.4 Arrays

Use:

```text
TEXT[]
```

for zone facilities.

Example:

```text
{"WiFi", "Power Outlet", "AC", "Lamp"}
```

- [x] Insert facility arrays
- [x] Query facilities
- [x] Update facilities

---

## 5.5 Indexes

Create useful indexes.

- [x] Unique index on `users.email`
- [x] Index on `bookings.user_id`
- [x] Index on `bookings.seat_id`
- [x] Index on `bookings.status`
- [x] Index on `payments.booking_id`
- [x] GiST index for booking ranges where appropriate

---

# 6. Booking Conflict Prevention

This is a core database requirement.

## 6.1 Exclusion Constraint

- [x] Create PostgreSQL exclusion constraint
- [x] Compare `seat_id` using equality
- [x] Compare `time_slot` using overlap
- [x] Exclude canceled bookings from the conflict rule if supported by the design

Conceptually:

```text
same seat
      +
overlapping time
      =
booking rejected
```

## 6.2 Allowed Cases

- [x] Same seat + overlapping time → reject
- [x] Same seat + non-overlapping time → allow
- [x] Different seats + overlapping time → allow
- [x] Canceled booking + same time → allow

## 6.3 Concurrency

- [x] Test two users booking the same seat simultaneously
- [x] Ensure PostgreSQL remains the final authority
- [x] Handle exclusion-constraint failure in FastAPI

---

# 7. Database Functions

Functions should be placed in:

```text
database/functions.sql
```

## 7.1 Availability

- [x] Accept seat and requested time range
- [x] Check existing bookings
- [x] Ignore canceled bookings
- [x] Return availability

## 7.2 Booking Cost

- [x] Accept seat/zone and duration
- [x] Retrieve applicable price
- [x] Calculate base booking cost
- [x] Return cost

## 7.3 Service Cost

- [x] Accept service and quantity
- [x] Retrieve service price
- [x] Calculate subtotal
- [x] Return subtotal

## 7.4 Booking Total

- [x] Calculate base booking cost
- [x] Calculate service total
- [x] Calculate final total
- [x] Return price breakdown

## 7.5 Booking Queries

- [x] Return customer's bookings
- [x] Return booking details
- [x] Return available seats
- [x] Return booking history
- [x] Return payment information

---

# 8. Database Procedures

Procedures should be placed in:

```text
database/procedures.sql
```

## 8.1 Create Booking

- [x] Validate customer
- [x] Validate seat
- [x] Validate time range
- [x] Validate selected services
- [x] Check availability
- [x] Calculate base cost
- [x] Create booking
- [x] Add booking services
- [x] Calculate final cost
- [x] Create payment record where required
- [x] Handle exceptions
- [x] Complete as one transaction

## 8.2 Cancel Booking

- [x] Validate booking
- [x] Validate ownership
- [x] Validate current status
- [x] Change status to `canceled`
- [x] Handle payment state where required

## 8.3 Check In

- [x] Validate booking ownership
- [x] Validate booking status
- [x] Verify check-in eligibility
- [x] Change status to `checked_in`
- [x] Record check-in timestamp

## 8.4 Check Out

- [x] Validate booking ownership
- [x] Require `checked_in` status
- [x] Change status to `checked_out`
- [x] Record check-out timestamp

---

# 9. Database Triggers

Triggers should be placed in:

```text
database/triggers.sql
```

Use triggers only where automatic database-side behavior is appropriate.

## 9.1 Timestamp Handling

- [x] Automatically maintain relevant timestamps
- [x] Test timestamp behavior

## 9.2 Booking Validation

- [x] Validate booking state transitions where appropriate
- [x] Prevent invalid lifecycle transitions

## 9.3 Payment Consistency

- [x] Prevent invalid payment state changes where required
- [x] Keep payment information consistent with booking state

## 9.4 Derived Data

- [x] Maintain derived values only where necessary
- [x] Avoid duplicating procedure/function logic

## 9.5 Trigger Testing

- [x] Test successful trigger execution
- [x] Test rejected operations
- [x] Test edge cases

---

# 10. Database Views

Create useful views for repeated queries.

## 10.1 Available Seats View

- [x] Show seats
- [x] Show zone
- [x] Show seat status
- [x] Show pricing information

## 10.2 Customer Booking View

- [ ] Show customer
- [ ] Show seat
- [ ] Show zone
- [ ] Show time slot
- [ ] Show booking status
- [ ] Show cost

## 10.3 Admin Booking View

- [ ] Show booking
- [ ] Customer information
- [ ] Seat
- [ ] Zone
- [ ] Time
- [ ] Status
- [ ] Payment status

## 10.4 Payment Summary View

- [ ] Show booking
- [ ] Amount
- [ ] Method
- [ ] Status
- [ ] Payment date

## 10.5 Service Usage View

- [ ] Show services
- [ ] Quantity used
- [ ] Revenue/subtotal where appropriate

---

# 11. Advanced PostgreSQL Requirements

## 11.1 Recursive CTE

Use a meaningful recursive CTE rather than adding one artificially.

Possible use:

- [ ] Generate/represent hierarchical zone information if applicable
- [ ] Generate a time sequence for availability/reporting if applicable
- [ ] Document why the recursive CTE is useful

## 11.2 Cursor

Use a cursor for an appropriate administrative/reporting operation.

Possible use:

- [ ] Iterate through booking records
- [ ] Generate an administrative report
- [ ] Demonstrate cursor-based processing

## 11.3 Transactions

- [ ] Use transactions for booking creation
- [ ] Roll back failed booking operations
- [ ] Roll back service insertion when booking creation fails
- [ ] Roll back payment creation when the transaction fails

## 11.4 Exception Handling

- [ ] Handle invalid booking requests
- [ ] Handle unavailable seats
- [ ] Handle duplicate/conflicting bookings
- [ ] Handle invalid service selection
- [ ] Handle database exceptions safely

---

# 12. Backend — FastAPI

All backend implementation remains in:

```text
backend/main.py
```

## 12.1 Application Setup

- [x] Initialize FastAPI
- [x] Add health endpoint
- [x] Configure PostgreSQL connection
- [x] Configure environment variables
- [x] Configure CORS
- [ ] Add exception handling

---

# 13. Authentication API

## Register

Registration is handled through the existing `Login.jsx` authentication page rather than a separate frontend page.

- [ ] `POST /auth/register`
- [ ] Validate name
- [ ] Validate email
- [ ] Validate password
- [ ] Check duplicate email
- [ ] Hash password
- [ ] Create user
- [ ] Return appropriate response

## Login

- [x] `POST /auth/login`
- [x] Validate credentials
- [x] Verify password
- [ ] Create authentication session/token
- [x] Return user information

## Current User

- [ ] `GET /users/me`
- [ ] Require authentication
- [ ] Return current user
- [ ] Return role

---

# 14. Zone & Seat API

## Zones

- [ ] `GET /zones`
- [ ] `GET /zones/{id}`
- [ ] `POST /zones` — admin
- [ ] `PUT /zones/{id}` — admin
- [ ] `DELETE /zones/{id}` — admin

## Seats

- [ ] `GET /seats`
- [ ] `GET /seats/{id}`
- [ ] `GET /zones/{id}/seats`
- [ ] `POST /seats` — admin
- [ ] `PUT /seats/{id}` — admin
- [ ] `DELETE /seats/{id}` — admin

---

# 15. Availability API

- [ ] Accept requested date
- [ ] Accept start time
- [ ] Accept end time
- [ ] Accept optional zone filter
- [ ] Query available seats
- [ ] Return seat information
- [ ] Return zone information
- [ ] Return applicable pricing
- [ ] Recheck availability during booking

Important:

```text
Availability shown in frontend
        ↓
FastAPI validation
        ↓
PostgreSQL final conflict check
```

---

# 16. Booking API

## Create Booking

- [x] `POST /bookings`
- [ ] Require authentication
- [x] Validate customer
- [x] Validate seat
- [x] Validate time range
- [x] Validate services
- [x] Recheck availability
- [x] Calculate authoritative cost
- [x] Create booking
- [x] Return booking information

## Retrieve

- [x] `GET /bookings/{id}`
- [ ] `GET /bookings/me`
- [x] Return seat
- [x] Return zone
- [x] Return time slot
- [x] Return services
- [x] Return total
- [x] Return payment status

## Booking Actions

- [x] `POST /bookings/{id}/cancel`
- [x] `POST /bookings/{id}/check-in`
- [x] `POST /bookings/{id}/check-out`

---

# 17. Booking Lifecycle

```text
PENDING
   │
   ▼
CONFIRMED
   │
   ▼
CHECKED_IN
   │
   ▼
CHECKED_OUT
```

Cancellation:

```text
PENDING ───────► CANCELED

CONFIRMED ─────► CANCELED
```

Prevent:

- [x] `CHECKED_OUT → CHECKED_IN`
- [ ] `CHECKED_OUT → CONFIRMED`
- [x] `CANCELED → CONFIRMED`
- [x] Duplicate check-in
- [x] Duplicate check-out
- [ ] Unauthorized cancellation
- [ ] Access to another customer's booking

---

# 18. Service API

- [x] `GET /services`
- [ ] `GET /services/{id}`
- [ ] `POST /services` — admin
- [ ] `PUT /services/{id}` — admin
- [ ] `DELETE /services/{id}` — admin
- [x] Add service to booking
- [ ] Remove service from booking
- [ ] Update service quantity
- [ ] Recalculate booking total

---

# 19. Payment API

- [x] `POST /payments`
- [x] `GET /payments/{id}`
- [] `GET /payments/me`
- [x] Validate booking
- [x] Validate amount
- [x] Record payment
- [x] Update payment status
- [ ] Return payment information
- [ ] Protect payment ownership

For this project, payment is a **recording/tracking system**, not a real payment gateway.

---

# 20. Admin API

## Dashboard

- [ ] Booking statistics
- [ ] Seat availability summary
- [ ] Payment summary
- [ ] Service usage summary
- [ ] Recent bookings

## Management

- [ ] Zone management
- [ ] Seat management
- [ ] Seat availability/status management
- [ ] Pricing management
- [ ] Service management
- [ ] Booking management
- [ ] Payment monitoring

There is no separate slot table.

"Slot management" means managing **booking availability through seat status, booking ranges, and availability queries**.

---

# 21. Frontend Design System

Detailed visual rules are maintained in:

```text
docs/FRONTEND_GUIDE.md
```

## Typography

- [x] Use Georgia as primary font
- [x] Use Georgia for headings
- [x] Use Georgia for body text
- [ ] Define heading sizes
- [ ] Define body size
- [ ] Define line heights

## UI

- [ ] Primary button
- [ ] Secondary button
- [ ] Danger button
- [ ] Input style
- [ ] Select style
- [ ] Card style
- [ ] Status badge
- [ ] Table style
- [ ] Modal style
- [ ] Error message style

## Consistency

- [ ] Consistent navbar
- [ ] Consistent spacing
- [ ] Consistent buttons
- [ ] Consistent cards
- [ ] Consistent forms
- [ ] Consistent status indicators
- [ ] Avoid unnecessary decorative elements
- [ ] Avoid duplicated information
- [ ] Keep pages visually consistent with `FRONTEND_GUIDE.md`

---

# 22. Frontend Pages

Only these pages should exist:

```text
Home.jsx
Login.jsx
Booking.jsx
MyBookings.jsx
Admin.jsx
```

## 22.1 Home.jsx

- [ ] Café introduction
- [ ] Main booking CTA
- [ ] Zone overview
- [ ] Facilities overview
- [ ] Pricing overview
- [ ] Login/register CTA

## 22.2 Login.jsx

Handle both authentication states if desired.

- [ ] Login form
- [ ] Registration form/section
- [ ] Email validation
- [ ] Password validation
- [ ] Loading state
- [ ] Authentication error
- [ ] Successful login
- [ ] Successful registration
- [ ] Switch between login/register

## 22.3 Booking.jsx

This is the main booking/discovery page.

- [ ] Date selection
- [ ] Start time
- [ ] End time
- [ ] Zone selection/filter
- [ ] Available seats
- [ ] Seat selection
- [ ] Seat price
- [ ] Selected seat summary
- [ ] Service selection
- [ ] Service quantities
- [ ] Booking total
- [ ] Confirm booking

## 22.4 MyBookings.jsx

- [ ] Upcoming bookings
- [ ] Active booking
- [ ] Past bookings
- [ ] Canceled bookings
- [ ] Booking status
- [ ] Booking details
- [ ] Services
- [ ] Total cost
- [ ] Payment status
- [ ] Cancel action
- [ ] Check-in action
- [ ] Check-out action

## 22.5 Admin.jsx

Single admin page containing management sections.

### Dashboard

- [ ] Statistics
- [ ] Seat availability
- [ ] Recent bookings
- [ ] Payment summary

### Zones

- [ ] View zones
- [ ] Add zone
- [ ] Edit zone
- [ ] Remove/deactivate zone
- [ ] Manage facilities
- [ ] Manage pricing

### Seats

- [ ] View seats
- [ ] Filter by zone
- [ ] Add seat
- [ ] Edit seat
- [ ] Block seat
- [ ] Unblock seat
- [ ] Remove seat

### Services

- [ ] View services
- [ ] Add service
- [ ] Edit service
- [ ] Update price
- [ ] Enable/disable service
- [ ] Remove service

### Bookings

- [ ] View all bookings
- [ ] Search
- [ ] Filter by status
- [ ] Filter by date
- [ ] Filter by zone
- [ ] View details

### Payments

- [ ] View payments
- [ ] Search
- [ ] Filter by status
- [ ] Filter by method
- [ ] View payment details

---

# 23. Existing Frontend Components

Only these reusable components are currently defined.

## Navbar.jsx

- [ ] Navigation
- [ ] Login/logout state
- [ ] Customer navigation
- [ ] Admin navigation
- [ ] Responsive behavior

## SeatCard.jsx

- [ ] Seat number
- [ ] Zone
- [ ] Price
- [ ] Availability
- [ ] Selection state
- [ ] Booking action

## BookingCard.jsx

- [ ] Booking information
- [ ] Seat
- [ ] Zone
- [ ] Date/time
- [ ] Status
- [ ] Cost
- [ ] Services
- [ ] Actions

Do not add unnecessary component files unless implementation actually requires them.

---

# 24. Frontend State

- [ ] Authentication state
- [ ] Current user
- [ ] Selected zone
- [ ] Selected seat
- [ ] Selected date
- [ ] Selected start time
- [ ] Selected end time
- [ ] Selected services
- [ ] Booking summary
- [ ] Loading state
- [ ] Error state

---

# 25. Error Handling

## Frontend

- [ ] Form validation errors
- [ ] Authentication errors
- [ ] API errors
- [ ] Seat unavailable error
- [ ] Booking conflict error
- [ ] Authorization error
- [ ] Loading states
- [ ] Empty states

## Backend

- [ ] Invalid input → `400`
- [ ] Unauthenticated → `401`
- [ ] Unauthorized → `403`
- [ ] Not found → `404`
- [ ] Booking conflict → `409`
- [ ] Database errors handled safely
- [ ] Never expose database internals

---

# 26. Security

- [ ] Hash passwords
- [ ] Never store plaintext passwords
- [ ] Protect authenticated endpoints
- [ ] Protect admin endpoints
- [ ] Validate user ownership
- [ ] Validate booking ownership
- [ ] Validate payment ownership
- [ ] Never trust frontend prices
- [ ] Never trust frontend booking status
- [ ] Validate all API input
- [ ] Keep database credentials in `.env`
- [ ] Keep secrets out of Git

---

# 27. Booking Transaction

Booking creation must behave as one logical transaction.

```text
BEGIN
  │
  ├── Validate customer
  ├── Validate seat
  ├── Validate time
  ├── Validate services
  ├── Check availability
  ├── Create booking
  ├── Add services
  ├── Calculate total
  ├── Create payment record
  │
COMMIT
```

If anything fails:

```text
ROLLBACK
```

- [ ] No partial booking
- [ ] No orphan booking services
- [ ] No incorrect payment record
- [ ] Return meaningful error

---

# 28. Testing

## Database

- [ ] Test domains
- [ ] Test composite type
- [ ] Test range type
- [ ] Test arrays
- [ ] Test primary keys
- [ ] Test foreign keys
- [ ] Test unique constraints
- [ ] Test check constraints
- [ ] Test indexes
- [ ] Test exclusion constraint
- [ ] Test functions
- [ ] Test procedures
- [ ] Test triggers
- [ ] Test views
- [ ] Test transactions
- [ ] Test exception handling

## Booking

- [ ] Overlapping same-seat booking
- [ ] Non-overlapping same-seat booking
- [ ] Different seats at same time
- [ ] Canceled booking
- [ ] Invalid time range
- [ ] Unavailable seat
- [ ] Concurrent booking attempts

## Backend

- [ ] Registration
- [ ] Login
- [ ] Authentication
- [ ] Authorization
- [ ] Zone API
- [ ] Seat API
- [ ] Availability API
- [ ] Booking API
- [ ] Cancellation
- [ ] Check-in
- [ ] Check-out
- [ ] Service API
- [ ] Payment API
- [ ] Admin API

## Frontend

- [ ] Login
- [ ] Registration
- [ ] Browse seats
- [ ] Select seat
- [ ] Create booking
- [ ] Add services
- [ ] View booking
- [ ] Cancel booking
- [ ] Check-in
- [ ] Check-out
- [ ] Admin operations
- [ ] Loading states
- [ ] Error states
- [ ] Responsive layout

---

# 29. Critical Scenarios

- [ ] Two customers attempt to book the same seat at the same time
- [ ] Two customers book different seats at the same time
- [ ] Same seat is booked for sequential periods
- [ ] Customer attempts to book unavailable seat
- [ ] Customer cancels another customer's booking
- [ ] Customer checks in to another customer's booking
- [ ] Customer checks out without checking in
- [ ] Customer checks in twice
- [ ] Customer checks out twice
- [ ] Customer modifies a canceled booking
- [ ] Admin blocks a seat with future bookings
- [ ] Service becomes unavailable after selection
- [ ] Service price changes after selection
- [ ] Zone price changes after an existing booking
- [ ] Payment fails
- [ ] Booking fails halfway through transaction
- [ ] Database rejects overlapping booking

---

# 30. Documentation

## README.md

- [ ] Project overview
- [ ] Features
- [ ] Customer features
- [ ] Admin features
- [ ] Tech stack
- [ ] Project structure
- [ ] PostgreSQL features
- [ ] Screenshots
- [ ] Setup reference
- [ ] Development status

## SETUP.md

- [ ] Prerequisites
- [ ] PostgreSQL installation
- [ ] Database creation
- [ ] Environment variables
- [ ] Database schema setup
- [ ] Functions setup
- [ ] Procedures setup
- [ ] Triggers setup
- [ ] Seed data
- [ ] Backend setup
- [ ] Frontend setup
- [ ] Running the application
- [ ] Troubleshooting

## FRONTEND_GUIDE.md

- [ ] Overall visual direction
- [ ] Georgia typography
- [ ] Colors
- [ ] Spacing
- [ ] Buttons
- [ ] Forms
- [ ] Cards
- [ ] Tables
- [ ] Status indicators
- [ ] Page-by-page layout
- [ ] Responsive behavior
- [ ] UI consistency rules

## PLAN.md

- [x] Maintain implementation checklist
- [ ] Mark completed features
- [ ] Keep architecture synchronized with implementation
- [ ] Add requirements only when actually discovered

---

# 31. Development Order

## Phase 1 — Database Foundation

- [x] Define domains
- [x] Define required types
- [x] Define seven tables
- [x] Define relationships
- [x] Define constraints
- [x] Add indexes
- [x] Add GiST support
- [x] Add exclusion constraint
- [ ] Add seed data

## Phase 2 — Database Logic

- [x] Functions
- [ ] Procedures
- [ ] Triggers
- [ ] Views
- [ ] Recursive CTE
- [ ] Cursor
- [ ] Transactions
- [ ] Exception handling
- [ ] Database testing

## Phase 3 — Backend

- [x] FastAPI setup
- [x] PostgreSQL connection
- [x] Environment configuration
- [x] CORS
- [ ] Authentication
- [x] Zone API
- [x] Seat API
- [x] Availability API
- [x] Booking API
- [x] Service API
- [x] Payment API
- [ ] Admin API
- [ ] Error handling

## Phase 4 — Frontend Foundation

- [x] React/Vite setup
- [x] `App.jsx`
- [x] `main.jsx`
- [x] Global CSS
- [x] Georgia typography
- [ ] Routing
- [ ] API communication
- [ ] Authentication state
- [ ] Reusable existing components

## Phase 5 — Customer Frontend

- [ ] Home
- [ ] Login/Register
- [ ] Browse availability
- [ ] Seat selection
- [ ] Booking
- [ ] Service selection
- [ ] Booking confirmation
- [ ] My Bookings
- [ ] Cancellation
- [ ] Check-in
- [ ] Check-out
- [ ] Payment status

## Phase 6 — Admin Frontend

- [ ] Admin dashboard
- [ ] Zone management
- [ ] Seat management
- [ ] Availability/status management
- [ ] Pricing management
- [ ] Service management
- [ ] Booking management
- [ ] Payment monitoring

## Phase 7 — Integration

- [ ] Connect frontend to FastAPI
- [ ] Connect FastAPI to PostgreSQL
- [ ] Verify authentication
- [ ] Verify availability
- [ ] Verify booking
- [ ] Verify service handling
- [ ] Verify payment recording
- [ ] Verify admin operations
- [ ] Verify database updates
- [ ] Verify error handling

## Phase 8 — Testing & Polish

- [ ] Database testing
- [ ] Backend testing
- [ ] Frontend testing
- [ ] End-to-end testing
- [ ] Concurrent booking testing
- [ ] Responsive testing
- [ ] Security review
- [ ] UI consistency review
- [ ] Remove unused code
- [ ] Fix bugs

## Phase 9 — Finalization

- [ ] Final README
- [ ] Final SETUP.md
- [ ] Final FRONTEND_GUIDE.md
- [x] Final PLAN.md
- [ ] Verify `.gitignore`
- [ ] Verify `.env.example` if used
- [ ] Test clean database setup
- [ ] Test clean backend setup
- [ ] Test clean frontend setup
- [ ] Final project demo
- [ ] Final Git cleanup