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