-- Extension Definitions
CREATE EXTENSION IF NOT EXISTS btree_gist;


-- DOMAIN DEFINITIONS

CREATE DOMAIN user_role AS TEXT CHECK (VALUE IN ('admin', 'customer'));
CREATE DOMAIN booking_status AS TEXT CHECK (VALUE IN ('pending', 'confirmed', 'checked_in', 'checked_out', 'canceled'));
CREATE DOMAIN seat_status AS TEXT CHECK (VALUE IN ('available', 'unavailable'));
CREATE DOMAIN payment_status AS TEXT CHECK (VALUE IN ('pending', 'completed', 'failed'));
CREATE DOMAIN payment_method AS TEXT CHECK (VALUE IN ('credit_card', 'mobile_banking', 'cash'));

-- COMPOSITE TYPE DEFINITIONS

CREATE TYPE price_breakdown AS (
    base_price NUMERIC,
    service_cost NUMERIC,
    total_price NUMERIC
);

-- TABLE DEFINITIONS

CREATE TABLE users(
    user_id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role user_role NOT NULL DEFAULT 'customer',
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
    status seat_status NOT NULL DEFAULT 'available'
);
CREATE TABLE bookings(
    booking_id NUMERIC(12,4) PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    seat_id INT REFERENCES seats(seat_id),
    time_slot TSTZRANGE NOT NULL,
    status booking_status NOT NULL DEFAULT 'pending',
    checked_in_at TIMESTAMP,
    checked_out_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    payment_id NUMERIC(12,4) PRIMARY KEY,
    booking_id NUMERIC(12,4) REFERENCES bookings(booking_id),
    amount NUMERIC NOT NULL,
    method payment_method NOT NULL,
    status payment_status NOT NULL DEFAULT 'pending',
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Exclusion constraints to prevent overlapping bookings for the same seat
ALTER TABLE bookings ADD CONSTRAINT no_overlapping_bookings EXCLUDE USING GIST (
    seat_id WITH =,
    time_slot WITH &&
);