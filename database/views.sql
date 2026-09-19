-- Shows a list of all bookings for customers, including seat, zone, and payment details
CREATE OR REPLACE VIEW user_bookings AS
SELECT
    b.booking_id,
    b.user_id,
    u.name AS customer_name,
    u.email,
    s.seat_id,
    s.seat_number,
    z.zone_id,
    z.name AS zone_name,
    lower(b.time_slot) AS start_time,
    upper(b.time_slot) AS end_time,
    b.status AS booking_status,
    b.booking_cost,
    p.status AS payment_status,
    p.amount AS payment_amount,
    b.checked_in_at,
    b.checked_out_at,
    b.created_at
FROM bookings b
JOIN users u ON b.user_id = u.user_id
JOIN seats s ON b.seat_id = s.seat_id
JOIN zones z ON s.zone_id = z.zone_id
LEFT JOIN payments p ON b.booking_id = p.booking_id
ORDER BY b.created_at DESC;

-- Shows a list of available seats along with their zone and price per hour
CREATE OR REPLACE VIEW available_seats AS
SELECT
    s.seat_id,
    s.seat_number,
    z.zone_id,
    z.name AS zone_name,
    z.price_per_hour
FROM seats s
JOIN zones z ON s.zone_id = z.zone_id
WHERE s.status = 'available'
ORDER BY z.zone_id, s.seat_number;

-- Shows a list of all bookings for admin, including seat, zone, and payment details
CREATE OR REPLACE VIEW admin_bookings AS
SELECT
    b.booking_id,
    b.user_id,
    u.name AS customer_name,
    u.email AS customer_email,
    s.seat_id,
    s.seat_number,
    z.zone_id,
    z.name AS zone_name,
    z.price_per_hour,
    lower(b.time_slot) AS start_time,
    upper(b.time_slot) AS end_time,
    b.status AS booking_status,
    p.payment_id,
    p.amount AS payment_amount,
    p.method AS payment_method,
    p.status AS payment_status,
    p.paid_at,
    b.checked_in_at,
    b.checked_out_at,
    b.created_at
FROM bookings b
JOIN users u ON b.user_id = u.user_id
JOIN seats s ON b.seat_id = s.seat_id
JOIN zones z ON s.zone_id = z.zone_id
LEFT JOIN payments p ON b.booking_id = p.booking_id
ORDER BY b.created_at DESC;

-- Shows payment information for each booking
CREATE OR REPLACE VIEW payment_summary AS
SELECT
    p.payment_id,
    p.booking_id,
    b.user_id,
    u.name AS customer_name,
    u.email AS customer_email,
    p.amount,
    p.method AS payment_method,
    p.status AS payment_status,
    p.paid_at,
    p.created_at
FROM payments p
JOIN bookings b ON p.booking_id = b.booking_id
JOIN users u ON b.user_id = u.user_id
ORDER BY p.created_at DESC;

-- Shows service usage for bookings
CREATE OR REPLACE VIEW service_usage AS
SELECT
    bs.booking_id,
    b.user_id,
    u.name AS customer_name,
    u.email AS customer_email,
    bs.service_id,
    s.name AS service_name,
    bs.quantity,
    bs.unit_price,
    (bs.quantity * bs.unit_price) AS service_total
FROM booking_services bs
JOIN bookings b ON bs.booking_id = b.booking_id
JOIN users u ON b.user_id = u.user_id
JOIN services s ON bs.service_id = s.service_id
ORDER BY bs.booking_id DESC, bs.service_id;

