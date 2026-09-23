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

-- Prevents duplicate login emails across customer, receptionist, and admin accounts
CREATE TRIGGER trg_check_login_email
BEFORE INSERT OR UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION check_login_email();

-- Keeps the booked hourly rate and blocks cancellations while a payment is in review
CREATE TRIGGER trg_protect_booking_payment
BEFORE INSERT OR UPDATE ON bookings
FOR EACH ROW
EXECUTE FUNCTION protect_booking_payment();

-- Prevents service changes once a payment has been submitted
CREATE TRIGGER trg_protect_booking_services
BEFORE INSERT OR UPDATE OR DELETE ON booking_services
FOR EACH ROW
EXECUTE FUNCTION protect_booking_services();