import PaymentCheckout from "../components/PaymentCheckout";
import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Coffee } from "lucide-react";
import {
  Layout,
  Heading,
  Feedback,
  useLoad,
  Modal,
  Badge,
} from "../components/CustomerUI";
import BookingCard from "../components/BookingCard";
import { api, post } from "../services/api";
import { money, slotDates, slotLabel } from "../utils/customer";
function Details({ booking, onClose, onUpdate }) {
  const price = useLoad(
    "/bookings/" + encodeURIComponent(booking.booking_id) + "/price",
  );
  const payment = useLoad(
    "/payments/" + encodeURIComponent(booking.booking_id),
  );
  const requests = useLoad("/payment-requests");
  const activeRequest = requests.data?.find(
    (r) => String(r.booking_id) === String(booking.booking_id),
  );
  const [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [cancel, setCancel] = useState(false);
  const lock = useRef(false);
  async function action(kind) {
    if (lock.current) return;
    lock.current = true;
    setBusy(true);
    setError("");
    try {
      await post(
        "/bookings/" + encodeURIComponent(booking.booking_id) + "/" + kind,
      );
      onUpdate();
      onClose();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
      lock.current = false;
    }
  }
  return (
    <Modal
      title={cancel ? "Cancel your booking?" : "Your booking details"}
      onClose={() => {
        if (!busy) onClose();
      }}
    >
      {cancel ? (
        <>
          <p>This will release your seat. Are you sure you want to cancel?</p>
          {error && (
            <p role="alert" className="sc-error">
              {error}
            </p>
          )}
          <div className="sc-actions">
            <button
              className="sc-button sc-secondary"
              disabled={busy}
              onClick={() => setCancel(false)}
            >
              Keep booking
            </button>
            <button
              className="sc-button sc-danger"
              disabled={busy}
              onClick={() => action("cancel")}
            >
              {busy ? "Cancelling…" : "Cancel booking"}
            </button>
          </div>
        </>
      ) : (
        <>
          <p className="sc-small">#{booking.booking_id}</p>
          <h3>
            {booking.zone_name} · {booking.seat_number}
          </h3>
          <p>{slotLabel(booking.time_slot)}</p>
          <Badge value={booking.booking_status} />
          <Feedback {...price}>
            <div className="sc-price-detail">
              <p className="sc-spread">
                <span>Seat</span>
                <span>{money(price.data?.base_price)}</span>
              </p>
              <p className="sc-spread">
                <span>Add-ons</span>
                <span>{money(price.data?.service_cost)}</span>
              </p>
              <p className="sc-spread sc-total">
                <span>Total</span>
                <strong>{money(price.data?.total_price)}</strong>
              </p>
            </div>
          </Feedback>
          {payment.loading ? (
            <p>Loading payment…</p>
          ) : payment.errorStatus === 404 ? (
            <p className="sc-small">
              No approved payment yet. Submit a payment below or pay cash at
              reception.
            </p>
          ) : payment.error ? (
            <>
              <p className="sc-small">
                {booking.payment_status
                  ? "Payment details could not be loaded."
                  : "Payment is not yet recorded or could not be loaded."}
              </p>
              <button
                className="sc-button sc-secondary"
                onClick={payment.retry}
              >
                Refresh payment
              </button>
            </>
          ) : (
            <p>
              Payment: <Badge value={payment.data?.status} />
              {payment.data?.method === "cash" ? " · Pay at the café" : ""}
            </p>
          )}
          {error && (
            <p role="alert" className="sc-error">
              {error}
            </p>
          )}
          <div className="sc-actions">
            {["pending", "confirmed"].includes(booking.booking_status) && (
              <button
                className="sc-button sc-secondary"
                disabled={busy}
                onClick={() => setCancel(true)}
              >
                Cancel booking
              </button>
            )}
            {booking.booking_status === "confirmed" && (
              <button
                className="sc-button"
                disabled={busy}
                onClick={() => action("check-in")}
              >
                Check in
              </button>
            )}
            {booking.booking_status === "checked_in" && (
              <button
                className="sc-button"
                disabled={busy}
                onClick={() => action("check-out")}
              >
                Check out
              </button>
            )}
          </div>
          <Feedback {...requests}>
            {activeRequest && (
              <div className="sc-notice">
                <p>
                  Transaction:{" "}
                  <strong className="sc-transaction">
                    {activeRequest.transaction_id}
                  </strong>
                </p>
                <p>
                  Status: {activeRequest.status}
                  {activeRequest.review_note
                    ? ` · ${activeRequest.review_note}`
                    : ""}
                </p>
              </div>
            )}
            {booking.booking_status === "pending" &&
              price.data &&
              (!activeRequest || activeRequest.status === "rejected") && (
                <PaymentCheckout
                  bookingId={booking.booking_id}
                  amount={price.data.total_price}
                  onSubmitted={requests.retry}
                />
              )}
            {activeRequest?.status === "pending" && (
              <p>
                Waiting for admin or receptionist approval.{" "}
                <button
                  className="sc-button sc-secondary"
                  onClick={() => {
                    requests.retry();
                    payment.retry();
                    onUpdate();
                  }}
                >
                  Refresh status
                </button>
              </p>
            )}
          </Feedback>
        </>
      )}
    </Modal>
  );
}
export default function MyBookings() {
  const state = useLoad("/bookings/me"),
    [tab, setTab] = useState("Upcoming"),
    [selected, setSelected] = useState(null);
  const items = (state.data || []).filter((b) => {
    if (b.booking_status === "canceled") return tab === "Cancelled";
    const end = slotDates(b.time_slot)[1];
    const past =
      b.booking_status === "checked_out" ||
      (b.booking_status !== "checked_in" &&
        end &&
        !isNaN(end) &&
        end < new Date());
    return past ? tab === "Past" : tab === "Upcoming";
  });
  return (
    <Layout>
      <div className="sc-heading-row">
        <Heading
          eyebrow="YOUR OWN LITTLE CORNER"
          title="Your study days, organized."
        >
          A new session to look forward to. A little progress to look back on.
        </Heading>
        <Link className="sc-button" to="/booking">
          Book a seat →
        </Link>
      </div>
      <div className="sc-tabs" aria-label="Booking categories">
        {["Upcoming", "Past", "Cancelled"].map((t) => (
          <button
            key={t}
            aria-pressed={tab === t}
            className={tab === t ? "active" : ""}
            onClick={() => setTab(t)}
          >
            {t}
          </button>
        ))}
      </div>
      <Feedback {...state}>
        <div className="sc-bookings-list">
          {items.map((b) => (
            <BookingCard
              key={b.booking_id}
              booking={b}
              onDetails={() => setSelected(b)}
            />
          ))}
        </div>
        {items.length === 0 && (
          <div className="sc-card sc-empty">
            <div className="sc-icon-disc">
              <Coffee size={30} />
            </div>
            <h2>
              {tab === "Upcoming"
                ? "Your next chapter is waiting."
                : "Nothing here just yet."}
            </h2>
            <p>
              {tab === "Upcoming"
                ? "Find a comfortable seat and make time for what matters."
                : "Your " + tab.toLowerCase() + " bookings will appear here."}
            </p>
            <Link className="sc-button" to="/booking">
              Find a study spot →
            </Link>
          </div>
        )}
      </Feedback>
      {selected && (
        <Details
          booking={selected}
          onClose={() => setSelected(null)}
          onUpdate={state.retry}
        />
      )}
    </Layout>
  );
}
