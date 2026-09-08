-- Automatically generate user_id for new users
CREATE TRIGGER trg_generate_user_id
BEFORE INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION generate_user_id();

-- Automatically generate booking_id for new bookings
CREATE TRIGGER trg_generate_booking_id
BEFORE INSERT ON bookings
FOR EACH ROW
EXECUTE FUNCTION generate_booking_id();

-- Automatically generate payment_id for new payments
CREATE TRIGGER trg_generate_payment_id
BEFORE INSERT ON payments
FOR EACH ROW
EXECUTE FUNCTION generate_payment_id();

-- Automatically updates the booking status
CREATE TRIGGER trg_booking_status_update
AFTER UPDATE ON bookings
FOR EACH ROW
EXECUTE FUNCTION update_booking_status();

-- Automatically updates the payment status
CREATE TRIGGER trg_payment_status_update
AFTER UPDATE ON payments
FOR EACH ROW
EXECUTE FUNCTION update_payment_status();