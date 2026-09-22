import { Link } from "react-router-dom";
import { Badge } from "./CustomerUI";
import { slotLabel, zoneImage, money } from "../utils/customer";
export default function BookingCard({ booking, onDetails }) {
  return (
    <article className="sc-card sc-booking-card">
      <img src={zoneImage(booking.zone_name)} alt="" />
      <div>
        <p className="sc-eyebrow">BOOKING #{booking.booking_id}</p>
        <h2>
          {booking.zone_name} · {booking.seat_number}
        </h2>
        <p>{slotLabel(booking.time_slot)}</p>
        <p>
          Payment: <Badge value={booking.payment_status} />
          {booking.payment_amount != null &&
            " · " + money(booking.payment_amount)}
        </p>
      </div>
      <div className="sc-booking-actions">
        <Badge value={booking.booking_status} />
        <button className="sc-button sc-secondary" onClick={onDetails}>
          View details
        </button>
        {booking.booking_status === "checked_out" && (
          <Link to="/booking">Book again →</Link>
        )}
      </div>
    </article>
  );
}
