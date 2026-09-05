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
cREATE TRIGGER trg_generate_user_id
BEFORE INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION generate_user_id();

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
CREATE TRIGGER trg_generate_booking_id
BEFORE INSERT ON bookings
FOR EACH ROW
EXECUTE FUNCTION generate_booking_id();

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
CREATE TRIGGER trg_generate_payment_id
BEFORE INSERT ON payments
FOR EACH ROW
EXECUTE FUNCTION generate_payment_id();


CREATE OR REPLACE FUNCTION update_booking_status()
CREATE TRIGGER trg_booking_status_update
AFTER UPDATE ON bookings
FOR EACH ROW
EXECUTE FUNCTION update_booking_status();

CREATE OR REPLACE FUNCTION update_payment_status()
CREATE TRIGGER trg_payment_status_update
AFTER UPDATE ON payments
FOR EACH ROW
EXECUTE FUNCTION update_payment_status();