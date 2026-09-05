# Study Café --- Frontend Planning Guide

> **Purpose:** This document is the single source of truth for designing
> and implementing the Study Café frontend.\
> The provided UI references define the visual direction, while the
> project plan below defines the actual functionality. The final
> frontend must combine both into **one consistent application**.

------------------------------------------------------------------------

# 1. Project Overview

## Study Café

A web-based **study café management platform** that enables customers to
browse, book, and manage study seats while providing administrators with
control over operations, pricing, availability, and café services.

### Tech Stack

  Layer      Technology
  ---------- --------------
  Backend    FastAPI
  Frontend   React + Vite
  Database   PostgreSQL

Architecture:

``` text
React Frontend
      ↓
FastAPI Backend
      ↓
PostgreSQL Database
```

The React frontend must **never connect directly to PostgreSQL**.

------------------------------------------------------------------------

# 2. Frontend Goal

The reference screens show a warm, illustrated, cozy Study Café
aesthetic.

The final frontend should preserve that visual identity while removing
the inconsistencies present in the references.

The goal is **not** to copy five screenshots independently.

The goal is:

``` text
                 STUDY CAFÉ
                     │
        ┌────────────┴────────────┐
        │                         │
     CUSTOMER                    ADMIN
        │                         │
     Home                        Dashboard
     Login                       Seats & Zones
     Booking                     Slots
     My Bookings                 Pricing
     Services                    Services
     Pricing                     Bookings
                                 Payments
                                 Customers
                                 Reports
```

Every screen must look like it belongs to the same product.

------------------------------------------------------------------------

# 3. What to Keep From the Reference Images

The references establish the following visual direction:

-   warm cream backgrounds
-   dark coffee-brown primary color
-   beige/golden borders
-   serif typography
-   cozy café illustrations
-   books, plants, coffee cups, desks and lamps
-   soft shadows
-   clean cards
-   rounded but not excessively rounded containers
-   spacious layouts
-   clear visual hierarchy
-   calm academic atmosphere

The frontend should feel:

``` text
Cozy
Academic
Warm
Calm
Welcoming
Organized
Premium but approachable
```

------------------------------------------------------------------------

# 4. What Must Be Corrected From the References

The reference screens contain visual and data inconsistencies.

Do **not** reproduce them literally.

Avoid:

-   different navigation structures on different customer pages
-   different years on different pages
-   contradictory prices
-   inconsistent booking totals
-   inconsistent customer names
-   fake statistics
-   duplicated features
-   random decorative elements
-   buttons that do nothing
-   features that are not part of the project
-   inconsistent terminology
-   different typography between screens

The references are **design references**, not the application's data
specification.

------------------------------------------------------------------------

# 5. Design System

Create the design system before building individual pages.

All pages must use the same:

-   colors
-   typography
-   spacing
-   buttons
-   cards
-   borders
-   shadows
-   status badges
-   icons
-   navigation
-   form controls

Do not independently style each page.

------------------------------------------------------------------------

# 6. Typography --- Georgia

The entire frontend should use **Georgia** as the primary font.

Use:

``` css
font-family: Georgia, "Times New Roman", serif;
```

This applies to:

-   headings
-   body text
-   navigation
-   buttons
-   forms
-   cards
-   tables
-   admin dashboard
-   status labels

Do **not** introduce Playfair Display, Inter, Lora, or other additional
fonts.

The visual identity should consistently feel like the references, but
with **Georgia as the required font**.

Recommended hierarchy:

``` text
Page Title       40–52px
Section Heading  28–36px
Card Heading     18–24px
Body             15–17px
Small Text       13–14px
```

Adjust sizes responsively.

------------------------------------------------------------------------

# 7. Color Palette

Use one shared palette.

## Primary Coffee

``` css
--color-primary: #633817;
--color-primary-dark: #4d2a12;
```

Used for:

-   primary buttons
-   active navigation
-   selected seats
-   important headings
-   admin sidebar
-   important icons

## Background

``` css
--color-background: #fbf4e5;
--color-surface: #fffaf0;
```

## Beige

``` css
--color-beige: #ead7b7;
--color-beige-light: #f4e8d0;
```

## Accent

``` css
--color-accent: #b98745;
```

## Text

``` css
--color-text: #3f2818;
--color-text-secondary: #705b47;
--color-text-muted: #9a8a76;
```

## Status

``` css
--color-success: #68784b;
--color-warning: #b8863b;
--color-danger: #9a4d3f;
--color-info: #62758a;
```

Use muted status colors. Avoid neon green, red, blue, or purple.

------------------------------------------------------------------------

# 8. Global CSS Tokens

Recommended starting point:

``` css
:root {
  --font-family: Georgia, "Times New Roman", serif;

  --color-primary: #633817;
  --color-primary-dark: #4d2a12;

  --color-background: #fbf4e5;
  --color-surface: #fffaf0;

  --color-beige: #ead7b7;
  --color-beige-light: #f4e8d0;
  --color-accent: #b98745;

  --color-text: #3f2818;
  --color-text-secondary: #705b47;
  --color-text-muted: #9a8a76;

  --color-success: #68784b;
  --color-warning: #b8863b;
  --color-danger: #9a4d3f;
  --color-info: #62758a;

  --radius-sm: 8px;
  --radius-md: 14px;
  --radius-lg: 20px;

  --shadow-sm: 0 2px 8px rgba(80, 45, 20, 0.05);
  --shadow-md: 0 4px 16px rgba(80, 45, 20, 0.07);

  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
}
```

These values can be tuned visually, but the same token system must be
maintained.

------------------------------------------------------------------------

# 9. Layout

Customer desktop pages:

``` text
┌───────────────────────────────────────────────────────┐
│ Navbar                                                │
├───────────────────────────────────────────────────────┤
│                                                       │
│                  Main Content                         │
│                                                       │
├───────────────────────────────────────────────────────┤
│ Footer                                                │
└───────────────────────────────────────────────────────┘
```

Use:

``` css
max-width: 1280px;
margin: 0 auto;
padding: 0 32px;
```

Do not allow the main content to become excessively wide on large
monitors.

------------------------------------------------------------------------

# 10. Cards

Standard card:

``` text
cream surface
+
beige border
+
small/medium radius
+
very soft shadow
+
comfortable padding
```

Suggested:

``` css
border: 1px solid var(--color-beige);
border-radius: var(--radius-md);
box-shadow: var(--shadow-sm);
```

Avoid:

-   heavy black borders
-   huge shadows
-   glassmorphism
-   excessive gradients
-   excessive pill-shaped cards

------------------------------------------------------------------------

# 11. Button System

Use four basic variants.

## Primary

Dark coffee background.

Examples:

``` text
Book a Seat
Log In
Continue
Confirm Booking
Pay Now
```

## Secondary

Cream/white with brown border.

Examples:

``` text
Explore Café
Back
View Details
```

## Destructive

Muted red.

Examples:

``` text
Cancel Booking
Delete
Block Seat
```

## Icon Button

For:

-   notification
-   search
-   menu
-   close
-   password visibility
-   dropdowns

Do not create a new visual button style for every page.

------------------------------------------------------------------------

# 12. Customer Navigation

Use one consistent navbar.

## Logged Out

``` text
[Coffee Icon] Study Café

Home
Study Zones
Services
Pricing
About Us
Contact

                         [Log In] [Register]
```

## Logged In

``` text
[Coffee Icon] Study Café

Home
Study Zones
Services
Pricing
My Bookings

                    [Notification] [User] [Name] [▼]
```

The customer navbar should not change its visual structure from page to
page.

------------------------------------------------------------------------

# 13. Logo

Always use:

``` text
☕  Study Café
```

with the same:

-   icon
-   text
-   typography
-   color
-   sizing
-   spacing

Do not create different logos for Home, Login, Booking, and My Bookings.

------------------------------------------------------------------------

# 14. Customer Feature Scope

The frontend must support the actual customer requirements.

## Account

-   Register
-   Log in

## Browse & Discover

-   View available study slots by date/time
-   Explore seats
-   Explore zones
-   View facilities
-   View pricing

## Booking

-   Book a seat
-   Select date/time
-   Select zone
-   Select seat
-   Prevent double-booking
-   Cancel booking
-   Check in
-   Check out

## Payments & Cost

-   Automatic booking cost calculation
-   View current bookings
-   View past bookings
-   Make payments
-   Track payment status

## Café Services

-   View café services
-   Add services to booking
-   Calculate service cost

------------------------------------------------------------------------

# 15. Admin Feature Scope

The admin UI must support:

## Seat & Slot Management

-   Add seats
-   Update seats
-   Remove seats
-   Add zones
-   Update zones
-   Remove zones
-   Create study slots
-   Manage study slots
-   Block seats for maintenance

## Pricing & Availability

-   Set prices
-   Update prices
-   Manage availability

## Service Management

-   Add café services
-   Update services
-   Remove services

Examples:

``` text
Coffee
Snacks
Printing
Other
```

## Booking & Payment Oversight

-   View all bookings
-   Manage bookings
-   Monitor payments
-   Manage payment status

------------------------------------------------------------------------

# 16. Home Page

File:

``` text
frontend/src/pages/Home.jsx
```

Structure:

``` text
Navbar
↓
Hero
↓
Study Zones
↓
Features
↓
CTA
↓
Footer
```

------------------------------------------------------------------------

# 17. Home --- Hero

Use a two-column layout.

``` text
┌────────────────────────────────────────────────────────┐
│                                                        │
│  Welcome to                    [Café Illustration]     │
│  Study Café                                             │
│                                                        │
│  Your cozy space to focus,                             │
│  learn and grow.                                       │
│                                                        │
│  Book a seat, grab a coffee,                           │
│  and make the most of your time.                       │
│                                                        │
│  [ Book a Seat ] [ Explore Café ]                     │
│                                                        │
└────────────────────────────────────────────────────────┘
```

Left:

-   heading
-   short description
-   CTA buttons

Right:

-   one consistent café illustration

Do not overcrowd the hero.

------------------------------------------------------------------------

# 18. Home --- Study Zones

Use the actual project zones:

``` text
Quiet Zone
Standard Zone
Group Zone
```

Each card:

``` text
[Illustration]

Quiet Zone

Perfect for deep focus
and concentration.

From ৳60/hour
```

Prices should come from backend/database data.

The same zone name and price must appear consistently across the
application.

------------------------------------------------------------------------

# 19. Home --- Features

Use four concise features.

### Easy Booking

Book your seat by date and time.

### Café Services

Add coffee, snacks, printing and more.

### Secure & Reliable

Double-booking prevention helps ensure your seat is reserved.

### Transparent Pricing

See the cost of your booking and services clearly.

------------------------------------------------------------------------

# 20. Home --- CTA

End with:

``` text
Ready to focus?

Find your perfect study spot today.

[ Book a Seat ]
```

------------------------------------------------------------------------

# 21. Home --- Footer

One shared customer footer:

``` text
Study Café
Focus. Learn. Grow.

Quick Links
Home
Study Zones
Services
Pricing

Account
Log In
Register
My Bookings

Contact
Email
Phone
Location

© 2026 Study Café
```

Keep it compact.

------------------------------------------------------------------------

# 22. Login Page

File:

``` text
frontend/src/pages/Login.jsx
```

Use a split-screen layout inspired by the second reference.

``` text
┌──────────────────────┬────────────────────────────────┐
│                      │                                │
│ Café illustration    │       Welcome Back             │
│                      │                                │
│ Study Café           │ Email                          │
│ Focus. Learn. Grow.  │ [________________________]     │
│                      │                                │
│                      │ Password                       │
│                      │ [________________________]     │
│                      │                                │
│                      │ □ Remember me                  │
│                      │                  Forgot password│
│                      │                                │
│                      │ [          Log In           ]  │
│                      │                                │
│                      │              or                │
│                      │                                │
│                      │ [     Create an Account     ]  │
│                      │                                │
└──────────────────────┴────────────────────────────────┘
```

Fields:

-   Email
-   Password
-   Remember me
-   Forgot password
-   Log In
-   Create Account

Password:

-   lock icon
-   show/hide control

------------------------------------------------------------------------

# 23. Registration

Registration must exist because it is part of the project requirements.

If a separate page is used, add:

``` text
frontend/src/pages/Register.jsx
```

Suggested fields:

``` text
Full Name
Email
Password
Confirm Password

[ Create Account ]
```

Keep registration visually consistent with Login.

------------------------------------------------------------------------

# 24. Booking Page

File:

``` text
frontend/src/pages/Booking.jsx
```

This is the main transactional page.

Desktop structure:

``` text
┌─────────────────────────────────────────────────────────────┐
│ Navbar                                                      │
├─────────────────────────────────────────────────────────────┤
│ Book Your Seat                                              │
│ Choose your preferred date, time and seat.                  │
├───────────────┬─────────────────────────────────┬───────────┤
│ Booking Steps │ Main Booking Area               │ Summary   │
│               │                                 │           │
│ Filters       │ Date & Time                     │ Booking   │
│               │ Zone                            │ Summary   │
│               │ Seat                            │           │
│               │                                 │ Price     │
└───────────────┴─────────────────────────────────┴───────────┘
```

------------------------------------------------------------------------

# 25. Booking Steps

Use:

``` text
1. Select Zone & Seat
2. Choose Add-ons
3. Review & Pay
4. Confirmation
```

The current step is highlighted.

------------------------------------------------------------------------

# 26. Booking --- Date & Time

Section:

``` text
1. Choose Date & Time
```

Date:

``` text
[ 📅 Select Date ▼ ]
```

Time:

``` text
[ 08:00–11:00 ]
[ 11:00–14:00 ]
[ 14:00–17:00 ]
[ 17:00–20:00 ]
```

Actual slots should come from the backend.

The frontend must not assume fixed slots if the admin can create/manage
slots.

------------------------------------------------------------------------

# 27. Booking --- Zone Selection

Cards:

``` text
Quiet Zone
Standard Zone
Group Zone
```

Each contains:

-   illustration
-   zone name
-   description
-   pricing
-   selected state

Selected:

-   brown border
-   subtle background
-   check indicator

------------------------------------------------------------------------

# 28. Booking --- Seat Selection

Display:

``` text
Standard Zone

Legend:

[ Available ] [ Selected ] [ Booked ] [ Maintenance ]

S01 S02 S03 S04
S05 S06 S07 S08
S09 S10 S11 S12
S13 S14 S15 S16
```

The exact number of seats is dynamic.

Do not hardcode the seat count.

------------------------------------------------------------------------

# 29. Seat States

Exactly four primary UI states:

### Available

Clickable.

### Selected

Dark coffee background.

### Booked

Disabled.

### Maintenance

Disabled and visually distinct.

The database/backend remains the source of truth for availability.

------------------------------------------------------------------------

# 30. SeatCard.jsx

Current component:

``` text
frontend/src/components/SeatCard.jsx
```

Responsibilities:

-   display seat number
-   display seat status
-   allow selection when available
-   show supported facilities/features

Possible information:

``` text
S11

Near Window
Power Outlet
Quiet Area
```

Do not put API calls or booking calculations inside `SeatCard`.

------------------------------------------------------------------------

# 31. Booking Filters

Keep filters limited to useful supported data.

### Zone

``` text
All Zones
Quiet Zone
Standard Zone
Group Zone
```

### Capacity

``` text
Any
1
2
3+
```

### Features

``` text
□ Near Power Outlet
□ Near Window
□ Quiet Area
```

Only expose filters supported by the backend/database.

------------------------------------------------------------------------

# 32. Booking Summary

Keep the summary visible on desktop.

``` text
Booking Summary

Zone
Standard Zone

Seat
S11

Date
May 18, 2026

Time
11:00 AM – 02:00 PM
(3 hours)

Price
৳45 × 3 hours     ৳135

Service Charge     ৳10

Total              ৳145

[ Continue ]
```

The values must be dynamically calculated.

------------------------------------------------------------------------

# 33. Booking Cost Calculation

The frontend should display the backend-calculated booking cost.

Conceptually:

``` text
Zone/Seat Rate
       ×
Duration
       +
Add-on Costs
       +
Applicable Charges
       =
Total
```

Do not hardcode:

``` js
const price = 45;
```

inside a component.

Prices come from backend data.

------------------------------------------------------------------------

# 34. Add-ons

After selecting the seat:

``` text
Choose Add-ons
```

Services may include:

``` text
Coffee
Snacks
Printing
Other
```

Example:

``` text
Coffee
৳80

[-] 1 [+]
```

The total updates as quantities change.

------------------------------------------------------------------------

# 35. Review & Pay

Show:

``` text
Booking Details

Zone
Seat
Date
Time

Selected Services

Price Breakdown

Seat/Zone Cost
Service Cost
Other Charges

Total

Payment Method

[ Confirm & Pay ]
```

The page should make the final amount obvious.

------------------------------------------------------------------------

# 36. Payments

The customer must be able to:

-   make a payment
-   see payment status
-   associate payment with a booking

Possible UI states:

``` text
Pending
Paid
Failed
```

The exact payment methods should match the backend/database.

Do not create payment methods that the backend does not support.

------------------------------------------------------------------------

# 37. Booking Confirmation

Successful booking:

``` text
✓

Booking Confirmed!

Your study seat has been reserved.

Booking ID: #SC-XXXX

Standard Zone
Seat S11

May 18, 2026
11:00 AM – 02:00 PM

Total: ৳145

[ View My Bookings ]
[ Back to Home ]
```

------------------------------------------------------------------------

# 38. Check-In

Customers must be able to check in when they arrive.

The booking details should expose:

``` text
[ Check In ]
```

only when the booking is eligible.

After check-in:

``` text
Checked In
```

The frontend should display the backend result rather than inventing
eligibility rules.

------------------------------------------------------------------------

# 39. Check-Out

Customers must be able to check out when leaving.

For an eligible checked-in booking:

``` text
[ Check Out ]
```

After successful checkout:

``` text
Checked Out
```

The UI should clearly show the booking's current status.

------------------------------------------------------------------------

# 40. My Bookings

File:

``` text
frontend/src/pages/MyBookings.jsx
```

Page:

``` text
My Bookings

View and manage all your study café bookings.
```

Tabs:

``` text
Upcoming
Past
Cancelled
```

Do not add unnecessary tabs.

------------------------------------------------------------------------

# 41. BookingCard.jsx

Current component:

``` text
frontend/src/components/BookingCard.jsx
```

Reuse it for booking lists.

Example:

``` text
┌─────────────────────────────────────────────────────────┐
│ [image]  Standard Zone — Seat S11      [Upcoming]       │
│                                                         │
│          May 18, 2026                                   │
│          11:00 AM – 02:00 PM                            │
│                                                         │
│          Near Window  Power Outlet  Quiet Area          │
│                                                         │
│                           Total: ৳145                   │
│                           [View Details]                │
│                           [Cancel Booking]              │
└─────────────────────────────────────────────────────────┘
```

Actions depend on booking state.

------------------------------------------------------------------------

# 42. Booking Statuses

The database booking statuses should be represented consistently.

Use:

``` text
Pending
Confirmed
Checked In
Checked Out
Cancelled
```

Internal values may be:

``` text
pending
confirmed
checked_in
checked_out
canceled
```

The frontend display label should be human-readable.

------------------------------------------------------------------------

# 43. Cancellation

Cancellation should be protected by the backend's business rules.

UI:

``` text
Cancel Booking
        ↓
Confirmation Modal
        ↓
Backend cancellation request
        ↓
Updated booking status
```

Modal:

``` text
Cancel Booking?

Are you sure you want to cancel this booking?

[Keep Booking] [Cancel Booking]
```

Do not cancel immediately from an accidental click.

------------------------------------------------------------------------

# 44. Cancellation Policy

If the project uses the two-hour cancellation rule shown in the
reference:

``` text
Free cancellation up to 2 hours before your booking start time.
```

Display it clearly.

The backend must determine whether cancellation is actually allowed.

------------------------------------------------------------------------

# 45. Admin Page

File:

``` text
frontend/src/pages/Admin.jsx
```

The admin UI should follow the fifth reference.

It should remain visually connected to Study Café while being more
compact and data-oriented.

------------------------------------------------------------------------

# 46. Admin Layout

``` text
┌───────────────┬──────────────────────────────────────────┐
│ Study Café    │ Top Bar                                 │
│ Admin Panel   │                                          │
│               │ Dashboard                                │
│ Dashboard     │                                          │
│               │ Statistics                               │
│ Manage        │ Recent Bookings                          │
│ Seats & Zones │ Charts                                   │
│ Slots         │ Services                                 │
│ Pricing       │ Quick Actions                            │
│ Block Seats   │                                          │
│               │                                          │
│ Services      │                                          │
│               │                                          │
│ Bookings      │                                          │
│ Payments      │                                          │
│               │                                          │
│ Users         │                                          │
│ Customers     │                                          │
│               │                                          │
│ Reports       │                                          │
│ Settings      │                                          │
└───────────────┴──────────────────────────────────────────┘
```

------------------------------------------------------------------------

# 47. Admin Sidebar

Dark coffee-brown sidebar.

Sections:

### Dashboard

-   Dashboard

### Manage

-   Seats & Zones
-   Slots
-   Pricing & Availability
-   Block Seats

### Services

-   Café Services

### Bookings

-   All Bookings
-   Payments

### Users

-   Customers

### Reports

-   Reports & Analytics

### Settings

-   Settings

Only expose functionality actually implemented.

------------------------------------------------------------------------

# 48. Admin Dashboard Header

``` text
Welcome back, Admin! 👋

Here's what's happening at Study Café today.
```

A small decorative illustration may appear beside it.

Do not let decoration compete with dashboard data.

------------------------------------------------------------------------

# 49. Admin Statistics

Primary cards:

``` text
Total Bookings
256

Total Seats
120

Today's Bookings
42

Revenue (Today)
৳18,750
```

These values are examples of the UI structure only.

Final values must come from backend APIs.

Never hardcode production statistics.

------------------------------------------------------------------------

# 50. Recent Bookings

Table columns:

``` text
Customer
Zone / Seat
Date & Time
Amount
Status
```

Example:

``` text
Fatima Rahman
Standard / S11
May 18, 11:00 AM
৳145
Confirmed
```

Status badges must use the same status system as the customer interface.

------------------------------------------------------------------------

# 51. Admin Booking Overview

The reference contains a weekly chart.

Use a chart only if the backend provides analytics data.

Example:

``` text
Bookings Overview

Mon Tue Wed Thu Fri Sat Sun
```

The chart should display real booking information.

Do not build fake analytics solely to make the screenshot look complete.

------------------------------------------------------------------------

# 52. Popular Services

Possible dashboard summary:

``` text
Coffee       128 orders
Snacks        94 orders
Printing      56 orders
Others        32 orders
```

These are example values.

Final values should be derived from booking/service data.

------------------------------------------------------------------------

# 53. Quick Actions

Useful actions:

``` text
Add Seat
Create Slot
Add Service
Update Pricing
Block Seat
```

Every button must lead to a real workflow.

No dead buttons.

------------------------------------------------------------------------

# 54. Admin Management Scope

The admin side should eventually provide management screens for:

``` text
Seats & Zones
Slots
Pricing & Availability
Block Seats
Café Services
All Bookings
Payments
Customers
Reports & Analytics
Settings
```

The current `Admin.jsx` can begin as the dashboard.

As implementation grows, management screens can be separated into pages.

------------------------------------------------------------------------

# 55. Existing Frontend Structure

Current structure:

``` text
frontend/
├── index.html
├── package.json
├── package-lock.json
├── vite.config.js
└── src/
    ├── App.jsx
    ├── main.jsx
    ├── index.css
    ├── components/
    │   ├── BookingCard.jsx
    │   ├── Navbar.jsx
    │   └── SeatCard.jsx
    └── pages/
        ├── Admin.jsx
        ├── Booking.jsx
        ├── Home.jsx
        ├── Login.jsx
        └── MyBookings.jsx
```

Keep the project simple.

------------------------------------------------------------------------

# 56. Recommended Frontend Structure

Expand only where useful:

``` text
frontend/
├── index.html
├── package.json
├── package-lock.json
├── vite.config.js
│
└── src/
    ├── App.jsx
    ├── main.jsx
    ├── index.css
    │
    ├── assets/
    │   ├── logo/
    │   ├── illustrations/
    │   └── icons/
    │
    ├── components/
    │   ├── Navbar.jsx
    │   ├── Footer.jsx
    │   ├── BookingCard.jsx
    │   ├── SeatCard.jsx
    │   ├── ZoneCard.jsx
    │   ├── ServiceCard.jsx
    │   ├── StatusBadge.jsx
    │   ├── Button.jsx
    │   └── PriceSummary.jsx
    │
    ├── pages/
    │   ├── Home.jsx
    │   ├── Login.jsx
    │   ├── Register.jsx
    │   ├── Booking.jsx
    │   ├── MyBookings.jsx
    │   └── Admin.jsx
    │
    ├── services/
    │   └── api.js
    │
    └── utils/
        ├── formatCurrency.js
        ├── formatDate.js
        └── bookingUtils.js
```

Do not introduce a large architecture unless the application requires
it.

------------------------------------------------------------------------

# 57. Component Responsibilities

## Navbar

Responsible for:

-   navigation
-   authentication-aware navigation
-   user menu

Not responsible for booking logic.

## SeatCard

Responsible for:

-   seat display
-   seat state
-   seat selection

Not responsible for API calls.

## BookingCard

Responsible for:

-   booking information
-   booking actions

Not responsible for loading the entire booking list.

## ZoneCard

Responsible for:

-   zone name
-   description
-   pricing
-   selection state

## ServiceCard

Responsible for:

-   service information
-   price
-   quantity selection

## PriceSummary

Responsible for:

-   displaying cost breakdown
-   displaying total

## StatusBadge

Responsible for:

-   consistent booking/payment status appearance

------------------------------------------------------------------------

# 58. Routing

Main routes:

``` text
/
/login
/register
/booking
/my-bookings
/admin
```

Potential future routes:

``` text
/admin/seats
/admin/slots
/admin/pricing
/admin/services
/admin/bookings
/admin/payments
/admin/customers
/admin/reports
```

Only add separate routes when those screens are actually implemented.

------------------------------------------------------------------------

# 59. Authentication Roles

Three frontend states:

``` text
Guest
Customer
Admin
```

## Guest

Can access:

``` text
Home
Study Zones
Services
Pricing
Login
Register
```

## Customer

Can access:

``` text
Home
Study Zones
Services
Pricing
Booking
My Bookings
Account
```

## Admin

Can access:

``` text
Admin dashboard
Admin management features
```

The backend must enforce authorization.

Frontend route protection alone is not security.

------------------------------------------------------------------------

# 60. API Service Layer

Create:

``` text
src/services/api.js
```

Centralize API calls.

Possible functions:

``` text
login()
register()

getZones()
getSeats()
getSlots()
getServices()

createBooking()
getMyBookings()
cancelBooking()
checkInBooking()
checkOutBooking()

createPayment()
getPaymentStatus()

getDashboardStats()
getRecentBookings()
getPopularServices()
```

The exact endpoints should match the FastAPI backend.

Do not scatter API requests throughout every component.

------------------------------------------------------------------------

# 61. Data Source Rules

Backend/database is the source of truth for:

-   users
-   zones
-   seats
-   seat availability
-   study slots
-   prices
-   facilities/features
-   bookings
-   booking status
-   services
-   payments

Frontend owns:

-   temporary UI state
-   form input
-   selected seat
-   selected zone
-   selected date/time
-   selected services
-   current booking step
-   visual loading/error state

------------------------------------------------------------------------

# 62. No Hardcoded Business Data

Avoid:

``` js
const price = 45;
const seats = ["S01", "S02"];
```

inside production UI components.

Instead:

``` text
PostgreSQL
   ↓
FastAPI
   ↓
React
   ↓
Component
```

The UI should render backend data.

Mock data is acceptable during initial development, but it should be
centralized and clearly replaceable.

------------------------------------------------------------------------

# 63. Double-Booking

The frontend should communicate availability clearly.

Example:

``` text
S11
Available
```

or:

``` text
S11
Booked
```

However, the frontend must never assume that a seat is guaranteed simply
because it appeared available.

The backend/database must enforce double-booking prevention.

Booking flow:

``` text
User selects seat
        ↓
Frontend sends booking request
        ↓
FastAPI validates request
        ↓
PostgreSQL validates availability
        ↓
Booking succeeds/fails
        ↓
Frontend displays result
```

If another customer has already taken the seat:

``` text
This seat is no longer available.

Please choose another seat.
```

------------------------------------------------------------------------

# 64. Loading States

Every API-dependent screen needs a loading state.

Examples:

``` text
Loading zones...
Loading available seats...
Loading bookings...
Loading dashboard...
```

Use simple skeletons or warm loading indicators.

------------------------------------------------------------------------

# 65. Empty States

## No bookings

``` text
No bookings yet.

Find a comfortable seat and start your next study session.

[ Book a Seat ]
```

## No seats

``` text
No seats are available for this time.

Try another time or zone.
```

## No services

``` text
No café services are currently available.
```

------------------------------------------------------------------------

# 66. Error States

Use friendly messages.

Instead of:

``` text
500 Internal Server Error
```

display:

``` text
Something went wrong.

We couldn't load the available seats.

[ Try Again ]
```

Keep technical error details out of the main UI.

------------------------------------------------------------------------

# 67. Form Validation

## Login

-   Email required
-   Valid email
-   Password required

## Registration

-   Name required
-   Email required
-   Valid email
-   Password required
-   Password confirmation matches

## Booking

-   Date required
-   Time required
-   Zone required
-   Seat required

## Services

-   Quantity cannot be negative

Frontend validation improves UX.

Backend validation remains mandatory.

------------------------------------------------------------------------

# 68. Currency

Use Bangladeshi Taka consistently:

``` text
৳145
```

Do not mix:

``` text
BDT 145
Tk 145
৳145
```

Use:

``` text
formatCurrency(amount)
```

Example:

``` text
৳145
৳45/hour
```

------------------------------------------------------------------------

# 69. Date & Time

Use one user-facing format.

Date:

``` text
May 18, 2026
```

Time:

``` text
11:00 AM – 02:00 PM
```

Backend may use ISO timestamps, but the UI should format them
consistently.

------------------------------------------------------------------------

# 70. Check-In / Check-Out UI

The booking card/details should reflect the booking lifecycle:

``` text
Pending
   ↓
Confirmed
   ↓
Checked In
   ↓
Checked Out
```

Cancellation is a separate terminal path:

``` text
Pending/Confirmed
       ↓
   Cancelled
```

Only display actions that make sense for the current status.

------------------------------------------------------------------------

# 71. Responsive Design

Support:

``` text
Desktop
Tablet
Mobile
```

## Desktop

Use:

-   full navbar
-   multi-column layouts
-   booking sidebar
-   seat grid
-   admin sidebar

## Tablet

-   reduce horizontal spacing
-   reduce card widths
-   move booking summary below main content if necessary

## Mobile

Navbar:

``` text
[Study Café]       [☰]
```

Booking:

``` text
Date
↓
Time
↓
Zone
↓
Seat
↓
Add-ons
↓
Summary
↓
Payment
```

Admin sidebar becomes a drawer.

Do not simply shrink the desktop layout.

------------------------------------------------------------------------

# 72. Illustration Strategy

Use one coherent hand-drawn illustration style.

Useful assets:

``` text
logo
hero-cafe
quiet-zone
standard-zone
group-zone
coffee
books
desk
seat
booking-success
empty-bookings
admin-decoration
```

Decorations should support the brand, not interfere with usability.

Avoid putting a large random illustration inside every card.

------------------------------------------------------------------------

# 73. Decorative Rules

Good:

-   small coffee icons
-   leaves
-   books
-   hanging lamps
-   small line ornaments
-   café sketches

Avoid:

-   decorations over important text
-   excessive plants
-   huge background illustrations
-   visual clutter
-   unrelated icons

------------------------------------------------------------------------

# 74. Accessibility

The frontend should provide:

-   semantic HTML
-   labels for form inputs
-   keyboard-accessible buttons
-   visible focus states
-   adequate contrast
-   meaningful image alt text
-   accessible icon buttons
-   seat status that is understandable without color alone

For example:

``` text
S11
Selected
```

rather than relying only on a brown color.

------------------------------------------------------------------------

# 75. Interaction Rules

## Seat

Available:

``` text
click → select
```

Selected:

``` text
click → deselect
```

Booked:

``` text
disabled
```

Maintenance:

``` text
disabled
```

## Zone

``` text
click → selected zone
```

Changing zone:

``` text
refresh available seats
```

## Time

Changing time:

``` text
refresh seat availability
```

## Date

Changing date:

``` text
refresh available slots/seat availability
```

## Add-ons

``` text
+ → quantity increases
- → quantity decreases
```

## Cancellation

``` text
click
↓
confirmation modal
↓
cancel request
```

------------------------------------------------------------------------

# 76. Information Architecture

``` text
STUDY CAFÉ
│
├── CUSTOMER
│   ├── Home
│   ├── Study Zones
│   ├── Services
│   ├── Pricing
│   ├── Register
│   ├── Login
│   ├── Booking
│   └── My Bookings
│
└── ADMIN
    ├── Dashboard
    ├── Seats & Zones
    ├── Slots
    ├── Pricing & Availability
    ├── Block Seats
    ├── Café Services
    ├── All Bookings
    ├── Payments
    ├── Customers
    ├── Reports & Analytics
    └── Settings
```

------------------------------------------------------------------------

# 77. Data Consistency Rules

Use one coherent application dataset.

For example:

``` text
Application year: 2026

Zones:
Quiet Zone
Standard Zone
Group Zone
```

The same zone names must be used everywhere.

The same user should not mysteriously have different names on different
pages.

Prices should come from the database.

Booking totals should be calculated.

Dashboard statistics should come from APIs.

------------------------------------------------------------------------

# 78. Implementation Order

Build in phases.

## Phase 1 --- Foundation

1.  React/Vite setup
2.  Global CSS
3.  Georgia font
4.  Design tokens
5.  Button system
6.  Navbar
7.  Footer
8.  Responsive base

## Phase 2 --- Home

1.  Hero
2.  Study Zones
3.  Features
4.  CTA
5.  Footer

## Phase 3 --- Authentication

1.  Login
2.  Register
3.  Form validation
4.  Authentication API
5.  Role handling

## Phase 4 --- Booking

1.  Date
2.  Time slots
3.  Zones
4.  Seats
5.  Seat states
6.  Filters
7.  Price summary
8.  Add-ons
9.  Review
10. Payment
11. Confirmation
12. Check-in
13. Check-out

## Phase 5 --- My Bookings

1.  Tabs
2.  BookingCard
3.  Upcoming
4.  Past
5.  Cancelled
6.  Details
7.  Cancellation
8.  Check-in/out actions

## Phase 6 --- Admin

1.  Admin layout
2.  Sidebar
3.  Top bar
4.  Dashboard statistics
5.  Recent bookings
6.  Booking analytics
7.  Popular services
8.  Quick actions
9.  Management screens

------------------------------------------------------------------------

# 79. Definition of Done

## Visual Consistency

-   [ ] Georgia is used throughout.
-   [ ] Same coffee-brown palette everywhere.
-   [ ] Same cream background everywhere.
-   [ ] Same card system.
-   [ ] Same button system.
-   [ ] Same navbar.
-   [ ] Same footer.
-   [ ] Same terminology.
-   [ ] Same illustration style.
-   [ ] No contradictory sample data.

## Customer

-   [ ] Register
-   [ ] Login
-   [ ] Browse zones
-   [ ] Browse services
-   [ ] View pricing
-   [ ] View available slots
-   [ ] Select date
-   [ ] Select time
-   [ ] Select zone
-   [ ] Select seat
-   [ ] Double-booking handled by backend
-   [ ] Add services
-   [ ] Automatic cost calculation
-   [ ] Payment
-   [ ] Payment status
-   [ ] View bookings
-   [ ] Cancel booking
-   [ ] Check in
-   [ ] Check out

## Admin

-   [ ] Dashboard
-   [ ] Manage seats
-   [ ] Manage zones
-   [ ] Manage slots
-   [ ] Manage pricing
-   [ ] Manage availability
-   [ ] Block seats
-   [ ] Manage café services
-   [ ] View/manage bookings
-   [ ] Monitor payments
-   [ ] Customers
-   [ ] Reports/analytics

## Technical

-   [ ] React communicates through FastAPI.
-   [ ] React never connects directly to PostgreSQL.
-   [ ] API requests are centralized.
-   [ ] No production business logic is hardcoded in components.
-   [ ] Loading states exist.
-   [ ] Empty states exist.
-   [ ] Error states exist.
-   [ ] Responsive layouts exist.
-   [ ] Accessibility basics are implemented.
-   [ ] No dead buttons.
-   [ ] No duplicated component implementations.

------------------------------------------------------------------------

# 80. Final Visual Blueprint

## Customer

``` text
┌─────────────────────────────────────────────────────────┐
│ ☕ Study Café     Home  Zones  Services  Pricing        │
│                                      My Bookings  User  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Warm cream background                                  │
│                                                         │
│  Georgia typography                                    │
│                                                         │
│  Coffee-brown headings                                 │
│                                                         │
│  Hand-drawn café illustrations                         │
│                                                         │
│  Beige bordered cards                                  │
│                                                         │
│  Soft shadows                                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Admin

``` text
┌───────────────┬─────────────────────────────────────────┐
│ Study Café    │ Dashboard                               │
│ Admin Panel   │                                         │
│               │ [Bookings] [Seats] [Today] [Revenue]   │
│ Dashboard     │                                         │
│ Seats & Zones │ Recent Bookings                         │
│ Slots         │                                         │
│ Pricing       │ Booking Overview                        │
│ Block Seats   │                                         │
│ Services      │ Popular Services                        │
│ Bookings      │                                         │
│ Payments      │ Quick Actions                           │
│ Customers     │                                         │
│ Reports       │                                         │
│ Settings      │                                         │
└───────────────┴─────────────────────────────────────────┘
```

------------------------------------------------------------------------

# 81. Most Important Rule

The five reference images should be treated as **one visual language**,
not five separate designs.

The final application should feel like:

``` text
                    STUDY CAFÉ
                        │
       ┌────────────────┼────────────────┐
       │                │                │
      HOME            BOOKING          ADMIN
       │                │                │
      LOGIN        MY BOOKINGS      MANAGEMENT
       │                │                │
       └────────────────┴────────────────┘
                        │
                 SAME DESIGN SYSTEM
                        │
       ┌────────────────┼────────────────┐
       │                │                │
     Georgia       Coffee Brown      Warm Cream
       │                │                │
       └──────────── Illustrations ──────┘
```

**The frontend should look polished, but the UI must always represent
the actual Study Café project requirements.**

The screenshots provide the **look**.

The project plan provides the **functionality**.

This guide defines how the two should become **one consistent React
application**.
