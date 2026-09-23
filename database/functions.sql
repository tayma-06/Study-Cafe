-- Automatically generate user_id for new users
CREATE OR REPLACE FUNCTION generate_user_id()
RETURNS TRIGGER AS $$
DECLARE
    max_id users.user_id%TYPE;
BEGIN
    PERFORM pg_advisory_xact_lock(101);
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
-- Format: YYYYMMDD + 4 decimal places (e.g., 20240101.0001)
CREATE OR REPLACE FUNCTION generate_booking_id()
RETURNS TRIGGER AS $$
DECLARE
    max_id bookings.booking_id%TYPE;
BEGIN
    PERFORM pg_advisory_xact_lock(102);
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
BEGIN
    NEW.payment_id := NULL;
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
    SELECT b.time_slot, COALESCE(b.hourly_rate, z.price_per_hour) INTO time_slot, price_per_hour
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
    SELECT COALESCE(SUM(bs.quantity * bs.unit_price), 0) INTO total_service_cost
    FROM booking_services bs
    JOIN services s ON bs.service_id = s.service_id
    WHERE bs.booking_id = p_booking_id;
    RETURN total_service_cost;
END;
$$ LANGUAGE plpgsql;

-- Calculates the total price for a booking, including the base price and service costs
CREATE OR REPLACE FUNCTION calculate_total_price(p_booking_id NUMERIC)
RETURNS price_breakdown
LANGUAGE plpgsql
AS $$
DECLARE
    base_price NUMERIC(10,2) := calculate_booking_price(p_booking_id);
    service_cost NUMERIC(10,2) := calculate_service_cost(p_booking_id);
    total_price NUMERIC(10,2) := base_price + service_cost;
BEGIN
    RETURN (base_price, service_cost, total_price);
END;
$$;

-- Updates seat status when a booking status changes
CREATE OR REPLACE FUNCTION update_booking_status()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'checked_in' AND OLD.status IS DISTINCT FROM NEW.status THEN
        UPDATE seats SET status = 'unavailable'
        WHERE seat_id = NEW.seat_id;
    ELSIF NEW.status = 'checked_out' AND OLD.status IS DISTINCT FROM NEW.status THEN
        UPDATE seats SET status = 'available'
        WHERE seat_id = NEW.seat_id;
    ELSIF NEW.status = 'canceled' AND OLD.status IS DISTINCT FROM NEW.status THEN
        UPDATE seats SET status = 'available'
        WHERE seat_id = NEW.seat_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Updates booking status based on payment status
CREATE OR REPLACE FUNCTION update_payment_status()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'completed' AND OLD.status IS DISTINCT FROM NEW.status THEN
        UPDATE bookings SET status = 'confirmed'
        WHERE booking_id = NEW.booking_id AND status = 'pending';
    ELSIF NEW.status = 'failed' AND OLD.status IS DISTINCT FROM NEW.status THEN
        UPDATE bookings SET status = 'pending'
        WHERE booking_id = NEW.booking_id AND status = 'confirmed';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Checks whether a seat is available for a requested time slot
CREATE OR REPLACE FUNCTION check_seat_availability( p_seat_id seats.seat_id%TYPE, p_time_slot TSTZRANGE)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN NOT EXISTS (
        SELECT 1
        FROM bookings
        WHERE seat_id = p_seat_id AND status <> 'canceled' AND time_slot && p_time_slot
    );
END;
$$ LANGUAGE plpgsql;

--- Prevent duplicate login emails across customer, receptionist, and admin accounts
CREATE OR REPLACE FUNCTION check_login_email()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_advisory_xact_lock(103);
    IF EXISTS (SELECT 1 FROM users WHERE user_id <> NEW.user_id AND
        (lower(email)=lower(NEW.email) OR lower(work_email)=lower(NEW.email) OR
         lower(email)=lower(NEW.work_email) OR lower(work_email)=lower(NEW.work_email))) THEN
        RAISE EXCEPTION 'Email already belongs to another account' USING ERRCODE='23505';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Keeps the booked hourly rate and blocks cancellations while a payment is in review
CREATE OR REPLACE FUNCTION protect_booking_payment()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP='INSERT' THEN
        IF NEW.hourly_rate IS NULL THEN
            SELECT z.price_per_hour INTO NEW.hourly_rate FROM seats s JOIN zones z USING(zone_id) WHERE s.seat_id=NEW.seat_id;
        END IF;
    ELSIF NEW.status='canceled' AND OLD.status <> 'canceled' THEN
        IF OLD.status NOT IN ('pending','confirmed') OR
           EXISTS(SELECT 1 FROM payments WHERE booking_id=OLD.booking_id AND status='completed') OR
           EXISTS(SELECT 1 FROM payment_requests WHERE booking_id=OLD.booking_id AND status='pending') THEN
            RAISE EXCEPTION 'Reject pending payments before canceling. Paid bookings require a separate refund process.';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Prevents service changes once a payment has been submitted
CREATE OR REPLACE FUNCTION protect_booking_services()
RETURNS TRIGGER AS $$
DECLARE
    target_id NUMERIC;
    current_status TEXT;
BEGIN
    target_id := COALESCE(NEW.booking_id, OLD.booking_id);
    SELECT status INTO current_status FROM bookings WHERE booking_id=target_id FOR UPDATE;
    IF current_status <> 'pending' OR
       EXISTS(SELECT 1 FROM payment_requests WHERE booking_id=target_id AND status IN ('pending','approved')) OR
       EXISTS(SELECT 1 FROM payments WHERE booking_id=target_id AND status='completed') THEN
        RAISE EXCEPTION 'Services cannot change after payment is submitted';
    END IF;
    IF TG_OP='DELETE' THEN RETURN OLD; END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Returns the available seats for a given time slot and optional zone filter
CREATE OR REPLACE FUNCTION get_available_seats(
    p_time_slot TSTZRANGE,
    p_zone_id INT DEFAULT NULL
)
RETURNS TABLE (
    seat_id INT,
    seat_number TEXT,
    zone_id INT,
    zone_name TEXT,
    price_per_hour NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT s.seat_id, s.seat_number, z.zone_id, z.name, z.price_per_hour
    FROM seats s
    JOIN zones z ON s.zone_id = z.zone_id
    WHERE s.status = 'available'
        AND (p_zone_id IS NULL OR s.zone_id = p_zone_id)
        AND NOT EXISTS (
            SELECT 1
            FROM bookings b
            WHERE b.seat_id = s.seat_id AND b.status <> 'canceled' AND b.time_slot && p_time_slot)
    ORDER BY z.zone_id, s.seat_number;
END;
$$;