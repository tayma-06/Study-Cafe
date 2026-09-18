-- Shows a list of all bookings for users, including seat, zone, and payment details
CREATE OR REPLACE VIEW user_bookings AS
SELECT
    b.booking_id,
    b.user_id,
    b.seat_id,
    b.time_slot,
    b.status AS booking_status,
    b.checked_in_at,
    b.checked_out_at,
    b.created_at,
    s.seat_number,
    z.name AS zone_name,
    p.status AS payment_status,
    p.amount AS payment_amount
FROM bookings b
JOIN seats s ON b.seat_id = s.seat_id
JOIN zones z ON s.zone_id = z.zone_id
LEFT JOIN payments p ON b.booking_id = p.booking_id;

-- Shows a list of available seats along with their zone and price per hour
CREATE OR REPLACE VIEW available_seats AS
SELECT
    s.seat_id,
    s.seat_number,
    z.zone_id,
    z.name AS zone_name,
    z.price_per_hour
FROM seats s
JOIN zones z
ON s.zone_id = z.zone_id
WHERE s.status = 'available';