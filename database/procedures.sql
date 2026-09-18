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
    IF p_services IS NOT NULL THEN
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
BEGIN
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
BEGIN
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
    IF p_services IS NOT NULL THEN
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