-- Extension Definitions
CREATE EXTENSION IF NOT EXISTS btree_gist;


-- DOMAIN DEFINITIONS

CREATE DOMAIN user_role AS TEXT CHECK (VALUE IN ('admin', 'customer', 'receptionist'));
CREATE DOMAIN booking_status AS TEXT CHECK (VALUE IN ('pending', 'confirmed', 'checked_in', 'checked_out', 'canceled'));
CREATE DOMAIN seat_status AS TEXT CHECK (VALUE IN ('available', 'unavailable'));
CREATE DOMAIN payment_status AS TEXT CHECK (VALUE IN ('pending', 'completed', 'failed'));
CREATE DOMAIN payment_method AS TEXT CHECK (VALUE IN ('credit_card', 'mobile_banking', 'cash'));

-- COMPOSITE TYPE DEFINITIONS

CREATE TYPE price_breakdown AS (
    base_price NUMERIC(10,2),
    service_cost NUMERIC(10,2),
    total_price NUMERIC(10,2)
);

-- TABLE DEFINITIONS

CREATE TABLE users(
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role user_role NOT NULL DEFAULT 'customer',
    work_email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE zones(
    zone_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price_per_hour NUMERIC NOT NULL,
    facilities TEXT[]
);
CREATE TABLE seats(
    seat_id SERIAL PRIMARY KEY,
    zone_id INT REFERENCES zones(zone_id),
    seat_number TEXT NOT NULL,
    UNIQUE (zone_id, seat_number),
    status seat_status NOT NULL DEFAULT 'available'
);
CREATE TABLE bookings(
    booking_id NUMERIC(12,4) PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    seat_id INT REFERENCES seats(seat_id),
    time_slot TSTZRANGE NOT NULL,
    status booking_status NOT NULL DEFAULT 'pending',
    checked_in_at TIMESTAMPTZ,
    checked_out_at TIMESTAMPTZ,
    guest_name TEXT,
    guest_phone TEXT,
    guest_email TEXT,
    created_by BIGINT REFERENCES users(user_id),
    hourly_rate NUMERIC,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE services(
    service_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price NUMERIC NOT NULL
);
CREATE TABLE booking_services(
    booking_id NUMERIC(12,4) REFERENCES bookings(booking_id),
    service_id INT REFERENCES services(service_id),
    PRIMARY KEY (booking_id, service_id),
    quantity INT NOT NULL DEFAULT 1,
    unit_price NUMERIC NOT NULL
);
CREATE TABLE payments(
    payment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    booking_id NUMERIC(12,4) REFERENCES bookings(booking_id) UNIQUE,
    amount NUMERIC NOT NULL,
    method payment_method NOT NULL,
    status payment_status NOT NULL DEFAULT 'pending',
    received_by BIGINT REFERENCES users(user_id),
    paid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE payment_requests(
    transaction_id TEXT PRIMARY KEY,
    booking_id NUMERIC(12,4) NOT NULL REFERENCES bookings(booking_id),
    amount NUMERIC(10,2) NOT NULL CHECK (amount > 0),
    method payment_method NOT NULL DEFAULT 'mobile_banking',
    provider TEXT NOT NULL DEFAULT 'bkash',
    phone TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    submitted_by BIGINT NOT NULL REFERENCES users(user_id),
    reviewed_by BIGINT REFERENCES users(user_id),
    review_note TEXT,
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table constraints for guest bookings, time slots, service quantities, and receptionist work email
ALTER TABLE users ADD CONSTRAINT receptionist_work_email CHECK (role <> 'receptionist' OR work_email IS NOT NULL);
ALTER TABLE bookings ADD CONSTRAINT booking_guest_details CHECK (user_id IS NOT NULL OR (guest_name IS NOT NULL AND guest_phone IS NOT NULL)) NOT VALID;
ALTER TABLE bookings ADD CONSTRAINT booking_time_valid CHECK (NOT isempty(time_slot) AND NOT lower_inf(time_slot) AND NOT upper_inf(time_slot) AND lower(time_slot) < upper(time_slot)) NOT VALID;
ALTER TABLE booking_services ADD CONSTRAINT service_quantity_positive CHECK (quantity > 0) NOT VALID;

-- Exclusion constraints to prevent overlapping bookings for the same seat
ALTER TABLE bookings ADD CONSTRAINT no_overlapping_bookings EXCLUDE USING GIST (
    seat_id WITH =,
    time_slot WITH &&
) WHERE (status <> 'canceled');

-- INDEX DEFINITIONS
CREATE UNIQUE INDEX IF NOT EXISTS users_work_email_key ON users (lower(work_email)) WHERE work_email IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS payment_request_active ON payment_requests(booking_id) WHERE status IN ('pending', 'approved');
CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_seat_id ON bookings(seat_id);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);