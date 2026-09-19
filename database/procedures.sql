-- Creating booking procedure with seat availability check and service addition
CREATE OR REPLACE PROCEDURE create_booking(
    p_user_id users.user_id%TYPE,
    p_seat_id seats.seat_id%TYPE,
    p_time_slot bookings.time_slot%TYPE,
    p_services INT[],
    p_quantities INT[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    p_booking_id bookings.booking_id%TYPE;
    i INT;
BEGIN
    IF NOT check_seat_availability(p_seat_id, p_time_slot) THEN
        RAISE EXCEPTION 'Seat is not available for the selected time slot';
    END IF;
    INSERT INTO bookings (user_id, seat_id, time_slot)
    VALUES (p_user_id, p_seat_id, p_time_slot)
    RETURNING booking_id INTO p_booking_id;
    IF COALESCE(array_length(p_services, 1), 0) > 0 THEN
        FOR i IN 1..array_length(p_services, 1) LOOP
            INSERT INTO booking_services (booking_id, service_id, quantity, unit_price)
            VALUES (
                p_booking_id,
                p_services[i],
                p_quantities[i],
                (
                    SELECT price
                    FROM services
                    WHERE service_id = p_services[i]
                )
            );
        END LOOP;
    END IF;
END;
$$;


-- Cancelling a booking and updating seat status
CREATE OR REPLACE PROCEDURE cancel_booking(
    p_booking_id bookings.booking_id%TYPE
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE bookings
    SET status = 'canceled'
    WHERE booking_id = p_booking_id;
END;
$$;


-- Checking in a booking
CREATE OR REPLACE PROCEDURE check_in_booking(
    p_booking_id bookings.booking_id%TYPE
)
LANGUAGE plpgsql
AS $$
DECLARE
    current_status booking_status;
BEGIN
    SELECT status
    INTO current_status
    FROM bookings
    WHERE booking_id = p_booking_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Booking not found';
    END IF;
    IF current_status <> 'confirmed' THEN
        RAISE EXCEPTION
            'Cannot check in booking with status: %',
            current_status;
    END IF;
    UPDATE bookings
    SET
        status = 'checked_in',
        checked_in_at = CURRENT_TIMESTAMP
    WHERE booking_id = p_booking_id;
END;
$$;


-- Checking out a booking
CREATE OR REPLACE PROCEDURE check_out_booking(
    p_booking_id bookings.booking_id%TYPE
)
LANGUAGE plpgsql
AS $$
DECLARE
    current_status booking_status;
BEGIN
    SELECT status
    INTO current_status
    FROM bookings
    WHERE booking_id = p_booking_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Booking not found';
    END IF;
    IF current_status <> 'checked_in' THEN
        RAISE EXCEPTION
            'Cannot check out booking with status: %',
            current_status;
    END IF;
    UPDATE bookings
    SET
        status = 'checked_out',
        checked_out_at = CURRENT_TIMESTAMP
    WHERE booking_id = p_booking_id;
END;
$$;


-- Adding services to an existing booking
CREATE OR REPLACE PROCEDURE add_services_to_booking(
    p_booking_id bookings.booking_id%TYPE,
    p_services INT[],
    p_quantities INT[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INT;
BEGIN
    IF COALESCE(array_length(p_services, 1), 0) > 0 THEN
        FOR i IN 1..array_length(p_services, 1) LOOP
            INSERT INTO booking_services (
                booking_id,
                service_id,
                quantity,
                unit_price
            )
            VALUES (
                p_booking_id,
                p_services[i],
                p_quantities[i],
                (
                    SELECT price
                    FROM services
                    WHERE service_id = p_services[i]
                )
            );
        END LOOP;
    END IF;
END;
$$;


-- Creating a payment for a booking and updating booking status if payment is completed
CREATE OR REPLACE PROCEDURE create_payment(
    p_booking_id NUMERIC,
    p_amount NUMERIC,
    p_method payment_method,
    p_status payment_status
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO payments (booking_id, amount, method, status, paid_at)
    VALUES (
        p_booking_id,
        p_amount,
        p_method,
        p_status,
        CASE
            WHEN p_status = 'completed'
            THEN CURRENT_TIMESTAMP
            ELSE NULL
        END
    );
    IF p_status = 'completed' THEN
        UPDATE bookings
        SET status = 'confirmed'
        WHERE booking_id = p_booking_id
          AND status = 'pending';
    END IF;
END;
$$;