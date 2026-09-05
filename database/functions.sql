-- Automatically generate user_id for new users
CREATE OR REPLACE FUNCTION generate_user_id()
RETURNS TRIGGER AS $$
DECLARE
    max_id users.user_id%TYPE;
BEGIN
    SELECT MAX(user_id) INTO max_id FROM users
    WHERE TO_CHAR(created_at, 'YYYYMMDD') = TO_CHAR(NEW.created_at, 'YYYYMMDD');
    IF max_id IS NULL THEN
        NEW.user_id := (TO_CHAR(NEW.created_at, 'YYYYMMDD') || '0001') :: BIGINT;
    ELSE
        NEW.user_id := max_id + 1;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Automatically generate booking_id for new bookings
CREATE OR REPLACE FUNCTION generate_booking_id()
RETURNS TRIGGER AS $$
DECLARE
    max_id bookings.booking_id%TYPE;
BEGIN
    SELECT MAX(booking_id) INTO max_id FROM bookings
    WHERE TO_CHAR(created_at, 'YYYYMMDD') = TO_CHAR(NEW.created_at, 'YYYYMMDD');
    IF max_id IS NULL THEN
        NEW.booking_id := TO_CHAR(NEW.created_at, 'YYYYMMDD') :: NUMERIC(12,4) + 0.0001;
    ELSE
        NEW.booking_id := max_id + 0.0001;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Automatically generate payment_id for new payments
CREATE OR REPLACE FUNCTION generate_payment_id()
RETURNS TRIGGER AS $$
DECLARE
    max_id payments.payment_id%TYPE;
BEGIN
    SELECT MAX(payment_id) INTO max_id FROM payments
    WHERE TO_CHAR(created_at, 'YYYYMMDD') = TO_CHAR(NEW.created_at, 'YYYYMMDD');
    IF max_id IS NULL THEN
        NEW.payment_id := TO_CHAR(NEW.created_at, 'YYYYDDMM') :: NUMERIC(12,4) + 0.0001;
    ELSE
        NEW.payment_id := max_id + 0.0001;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Calculates the booking price based on the slot time and the zone's price per hour
CREATE OR REPLACE FUNCTION calculate_booking_price(p_booking_id NUMERIC(12,4))

RETURNS NUMERIC AS $$

DECLARE

    time_slot bookings.time_slot%TYPE;

    price_per_hour zones.price_per_hour%TYPE;

    duration NUMERIC;

BEGIN
    SELECT b.time_slot, z.price_per_hour INTO time_slot, price_per_hour
    FROM bookings b
    JOIN seats s ON b.seat_id = s.seat_id
    JOIN zones z ON s.zone_id = z.zone_id
    WHERE b.booking_id = p_booking_id;
    duration := EXTRACT(EPOCH FROM (UPPER(time_slot) - LOWER(time_slot))) / 3600;
    RETURN duration * price_per_hour;
END;
$$ LANGUAGE plpgsql;

-- Calculates the total service cost for a booking based on the selected services and their quantities
CREATE OR REPLACE FUNCTION calculate_service_cost(p_booking_id NUMERIC(12,4))
RETURNS NUMERIC AS $$
DECLARE
    total_service_cost NUMERIC;
BEGIN
    SELECT COALESCE(SUM(bs.quantity * s.price), 0) INTO total_service_cost
    FROM booking_services bs
    JOIN services s ON bs.service_id = s.service_id
    WHERE bs.booking_id = p_booking_id;
    RETURN total_service_cost;
END;
$$ LANGUAGE plpgsql;

-- Calculates the total price for a booking, including the base price and service costs
CREATE OR REPLACE FUNCTION calculate_total_price(p_booking_id NUMERIC(12,4))
RETURNS price_breakdown AS $$
DECLARE
    base_price NUMERIC := calculate_booking_price(p_booking_id);
    service_cost NUMERIC := calculate_service_cost(p_booking_id);
    total_price NUMERIC := base_price + service_cost;
BEGIN
    RETURN (base_price, service_cost, total_price);
END;
$$ LANGUAGE plpgsql;  

CREATE OR REPLACE FUNCTION update_booking_status()
CREATE OR REPLACE FUNCTION update_payment_status()
CREATE OR REPLACE FUNCTION check_seat_availability()


