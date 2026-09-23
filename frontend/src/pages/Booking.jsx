import PaymentCheckout from "../components/PaymentCheckout";
import { useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  Check,
  ArrowRight,
  Coffee,
  CalendarDays,
  Armchair,
} from "lucide-react";
import {
  Layout,
  Heading,
  Feedback,
  useLoad,
  useSession,
  Badge,
} from "../components/CustomerUI";
import SeatCard from "../components/SeatCard";
import { api, post } from "../services/api";
import { money, today, zoneImage } from "../utils/customer";
export default function Booking() {
  const user = useSession(),
    [params] = useSearchParams(),
    zones = useLoad("/zones"),
    services = useLoad("/services");
  const [date, setDate] = useState(today),
    [start, setStart] = useState("09:00"),
    [end, setEnd] = useState("12:00"),
    [zone, setZone] = useState(params.get("zone") || ""),
    [seat, setSeat] = useState(null),
    [availability, setAvailability] = useState(null),
    [checking, setChecking] = useState(false),
    [error, setError] = useState(""),
    [step, setStep] = useState(0),
    [quantities, setQuantities] = useState({}),
    [busy, setBusy] = useState(false),
    [created, setCreated] = useState(null),
    [finalPrice, setFinalPrice] = useState(null);
  const request = useRef(0),
    lock = useRef(false);
  const selectedZone = zones.data?.find(
    (z) => String(z.zone_id) === String(zone),
  );
  const duration =
    (new Date(date + "T" + end + "+06:00") -
      new Date(date + "T" + start + "+06:00")) /
    3600000;
  const addons = (services.data || []).filter(
    (s) => quantities[s.service_id] > 0,
  );
  const estimatedBase =
      (Number(selectedZone?.price_per_hour) || 0) * Math.max(0, duration || 0),
    estimatedServices = addons.reduce(
      (total, s) => total + Number(s.price) * quantities[s.service_id],
      0,
    );
  useEffect(() => {
    request.current++;
    setAvailability(null);
    setSeat(null);
    setChecking(false);
    setError("");
  }, [date, start, end, zone]);
  useEffect(
    () => () => {
      request.current++;
    },
    [],
  );
  async function search(event) {
    event?.preventDefault();
    setError("");
    if (
      !zone ||
      !date ||
      !start ||
      !end ||
      duration <= 0 ||
      new Date(date + "T" + start + "+06:00") <= new Date()
    ) {
      setError(
        "Choose a zone and a future time, with the end after the start.",
      );
      return;
    }
    const id = ++request.current;
    setChecking(true);
    setAvailability(null);
    setSeat(null);
    try {
      const query = new URLSearchParams({
        date,
        start_time: start,
        end_time: end,
        zone_id: zone,
      });
      const [available, all] = await Promise.all([
        api("/availability?" + query),
        api("/zones/" + zone + "/seats"),
      ]);
      if (id === request.current) setAvailability({ available, all });
    } catch (e) {
      if (id === request.current) setError(e.message);
    } finally {
      if (id === request.current) setChecking(false);
    }
  }
  async function reserve() {
    if (lock.current || created) return;
    lock.current = true;
    setBusy(true);
    setError("");
    try {
      const result = await post("/bookings", {
        user_id: user.user_id,
        seat_id: seat.seat_id,
        start_time: date + "T" + start + ":00+06:00",
        end_time: date + "T" + end + ":00+06:00",
        services: addons.map((s) => s.service_id),
        quantities: addons.map((s) => quantities[s.service_id]),
      });
      setCreated(result);
      setStep(3);
      try {
        setFinalPrice(
          await api(
            "/bookings/" + encodeURIComponent(result.booking_id) + "/price",
          ),
        );
      } catch (e) {
        setError(
          "Your booking was created, but its total could not be loaded. Open My Bookings to retrieve it.",
        );
      }
    } catch (e) {
      setError(
        e.message +
          " Check My Bookings before trying again in case your reservation was saved.",
      );
      setAvailability(null);
      setSeat(null);
      setStep(0);
    } finally {
      lock.current = false;
      setBusy(false);
    }
  }
  return (
    <Layout>
      <Heading
        eyebrow="YOUR NEXT CHAPTER STARTS HERE"
        title={
          created
            ? "Your study spot is reserved."
            : "Make room for a little focus."
        }
      >
        {created
          ? "Your booking is saved. Submit a payment for staff approval."
          : "Choose your time, find a comfortable seat, and make it your own."}
      </Heading>
      <ol className="sc-steps">
        {["Time & seat", "Café add-ons", "Review", "Reservation"].map(
          (label, i) => (
            <li
              key={label}
              className={
                i === step ? "is-active" : i < step ? "is-complete" : ""
              }
            >
              <span>{i < step ? <Check size={16} /> : i + 1}</span>
              {label}
            </li>
          ),
        )}
      </ol>
      <div className="sc-booking-layout">
        <section className="sc-card sc-workspace">
          {error && (
            <p className="sc-error" role="alert">
              {error}
            </p>
          )}
          {step === 0 && (
            <>
              <h2>
                <CalendarDays size={23} /> When would you like to visit?
              </h2>
              <p className="sc-muted">All times are café local time (Dhaka).</p>
              <Feedback {...zones}>
                <form onSubmit={search}>
                  <div className="sc-fields">
                    <label>
                      Date
                      <input
                        type="date"
                        min={today()}
                        value={date}
                        onChange={(e) => setDate(e.target.value)}
                        required
                      />
                    </label>
                    <label>
                      From
                      <input
                        type="time"
                        value={start}
                        onChange={(e) => setStart(e.target.value)}
                        required
                      />
                    </label>
                    <label>
                      Until
                      <input
                        type="time"
                        value={end}
                        onChange={(e) => setEnd(e.target.value)}
                        required
                      />
                    </label>
                  </div>
                  <h3>Choose your study zone</h3>
                  <div className="sc-zone-options">
                    {zones.data?.map((z) => (
                      <button
                        type="button"
                        className={
                          String(z.zone_id) === String(zone)
                            ? "sc-zone selected"
                            : "sc-zone"
                        }
                        aria-pressed={String(z.zone_id) === String(zone)}
                        onClick={() => setZone(String(z.zone_id))}
                        key={z.zone_id}
                      >
                        <img src={zoneImage(z.name)} alt="" />
                        <strong>{z.name}</strong>
                        <small>{money(z.price_per_hour)}/hour</small>
                      </button>
                    ))}
                  </div>
                  <button
                    className="sc-button sc-secondary"
                    disabled={checking || !zone}
                  >
                    {checking ? "Checking seats…" : "Find available seats"}
                    <ArrowRight size={16} />
                  </button>
                </form>
              </Feedback>
              {availability && (
                <div className="sc-seat-area">
                  <h3>
                    <Armchair size={21} /> Find your favorite seat
                  </h3>
                  <p className="sc-small">
                    Available · Selected · Booked · Unavailable
                  </p>
                  <p className="sc-small">
                    Availability for your chosen time is confirmed when you
                    reserve. A seat shown here may already be reserved for that
                    time.
                  </p>
                  <div className="sc-seat-grid">
                    {availability.all.map((s) => (
                      <SeatCard
                        key={s.seat_id}
                        seat={s}
                        state={
                          seat?.seat_id === s.seat_id
                            ? "selected"
                            : s.status !== "available"
                              ? "unavailable"
                              : availability.available.some(
                                    (a) => a.seat_id === s.seat_id,
                                  )
                                ? "available"
                                : "booked"
                        }
                        onSelect={() =>
                          setSeat(seat?.seat_id === s.seat_id ? null : s)
                        }
                      />
                    ))}
                  </div>
                  {availability.available.length === 0 && (
                    <p className="sc-notice">
                      No seats are available for this time. Try another time or
                      zone.
                    </p>
                  )}
                </div>
              )}
              <div className="sc-actions">
                <button
                  className="sc-button"
                  disabled={!seat || checking}
                  onClick={() => setStep(1)}
                >
                  Choose add-ons <ArrowRight size={16} />
                </button>
              </div>
            </>
          )}
          {step === 1 && (
            <>
              <h2>
                <Coffee size={23} /> A little something for your session
              </h2>
              <p className="sc-muted">
                Optional extras. Add only what you need.
              </p>
              <Feedback {...services}>
                {services.data?.map((s) => (
                  <div className="sc-service-row" key={s.service_id}>
                    <div className="sc-icon-disc">
                      <Coffee size={22} />
                    </div>
                    <div>
                      <h3>{s.name}</h3>
                      <p>{s.description}</p>
                      <strong>{money(s.price)}</strong>
                    </div>
                    <div className="sc-counter">
                      <button
                        aria-label={"Remove " + s.name}
                        disabled={!quantities[s.service_id]}
                        onClick={() =>
                          setQuantities((q) => ({
                            ...q,
                            [s.service_id]: Math.max(
                              0,
                              (q[s.service_id] || 0) - 1,
                            ),
                          }))
                        }
                      >
                        −
                      </button>
                      <output aria-label={s.name + " quantity"}>
                        {quantities[s.service_id] || 0}
                      </output>
                      <button
                        aria-label={"Add " + s.name}
                        disabled={quantities[s.service_id] >= 99}
                        onClick={() =>
                          setQuantities((q) => ({
                            ...q,
                            [s.service_id]: (q[s.service_id] || 0) + 1,
                          }))
                        }
                      >
                        +
                      </button>
                    </div>
                  </div>
                ))}
                {services.data?.length === 0 && (
                  <p>No add-ons are available right now.</p>
                )}
              </Feedback>
              <div className="sc-actions">
                <button
                  className="sc-button sc-secondary"
                  onClick={() => setStep(0)}
                >
                  Back
                </button>
                <button className="sc-button" onClick={() => setStep(2)}>
                  Review booking <ArrowRight size={16} />
                </button>
              </div>
            </>
          )}
          {step === 2 && (
            <>
              <p className="sc-eyebrow">ONE LAST LOOK</p>
              <h2>Your time, well spent.</h2>
              <div className="sc-review">
                <img src={zoneImage(selectedZone?.name)} alt="" />
                <div>
                  <h3>{selectedZone?.name}</h3>
                  <p>Seat {seat?.seat_number}</p>
                  <p>
                    {date} · {start} – {end}
                  </p>
                  <p>{duration} hours · Dhaka time</p>
                </div>
              </div>
              <h3>Your add-ons</h3>
              {addons.length ? (
                addons.map((s) => (
                  <p className="sc-spread" key={s.service_id}>
                    <span>
                      {s.name} × {quantities[s.service_id]}
                    </span>
                    <span>
                      {money(Number(s.price) * quantities[s.service_id])}
                    </span>
                  </p>
                ))
              ) : (
                <p className="sc-muted">Just the seat. A little simplicity.</p>
              )}
              <div className="sc-notice">
                <strong>Choose how to pay</strong>
                <p>
                  Use the bKash payment demo after reserving, or pay cash at
                  reception. Your booking remains pending until staff approve
                  payment.
                </p>
                <p>
                  The total shown is an estimate based on current rates. Your
                  final total is calculated after reservation.
                </p>
              </div>
              <div className="sc-actions">
                <button
                  className="sc-button sc-secondary"
                  disabled={busy}
                  onClick={() => setStep(1)}
                >
                  Back
                </button>
                <button className="sc-button" disabled={busy} onClick={reserve}>
                  {busy ? "Reserving…" : "Reserve my seat"}
                  <ArrowRight size={16} />
                </button>
              </div>
            </>
          )}
          {step === 3 && (
            <>
              <div className="sc-confirm-icon">
                <Check size={32} />
              </div>
              <h2>See you at Study Café.</h2>
              <p>Booking #{created?.booking_id}</p>
              <Badge value={created?.status} />
              <div className="sc-review">
                <img src={zoneImage(selectedZone?.name)} alt="" />
                <div>
                  <h3>
                    {selectedZone?.name} · {seat?.seat_number}
                  </h3>
                  <p>
                    {date} · {start} – {end}
                  </p>
                  <p>Dhaka time</p>
                </div>
              </div>
              {finalPrice && (
                <>
                  <p className="sc-spread sc-total">
                    <span>Final total</span>
                    <strong>{money(finalPrice.total_price)}</strong>
                  </p>
                  <PaymentCheckout
                    bookingId={created.booking_id}
                    amount={finalPrice.total_price}
                  />
                </>
              )}
              <div className="sc-actions">
                <Link className="sc-button sc-secondary" to="/bookings">
                  View my bookings
                </Link>
                <Link to="/">Back to home →</Link>
              </div>
            </>
          )}
        </section>
        <aside className="sc-card sc-summary">
          <p className="sc-eyebrow">A MOMENT FOR YOURSELF</p>
          <h2>Your session</h2>
          <div className="sc-summary-art">
            <img src={zoneImage(selectedZone?.name)} alt="" />
          </div>
          <h3>{selectedZone?.name || "Your perfect study spot"}</h3>
          <p className="sc-muted">
            {seat ? "Seat " + seat.seat_number : "Select a seat to get started"}
          </p>
          <hr />
          <p className="sc-spread">
            <span>Date</span>
            <span>{date}</span>
          </p>
          <p className="sc-spread">
            <span>Time</span>
            <span>
              {start} – {end}
            </span>
          </p>
          <p className="sc-spread">
            <span>Seat · {Math.max(0, duration || 0)} hours</span>
            <span>{money(finalPrice?.base_price ?? estimatedBase)}</span>
          </p>
          <p className="sc-spread">
            <span>Add-ons</span>
            <span>{money(finalPrice?.service_cost ?? estimatedServices)}</span>
          </p>
          <hr />
          <p className="sc-spread sc-total">
            <span>{finalPrice ? "Total" : "Estimated total"}</span>
            <strong>
              {money(
                finalPrice?.total_price ?? estimatedBase + estimatedServices,
              )}
            </strong>
          </p>
          <p className="sc-small">
            {finalPrice
              ? "Calculated by the café."
              : "Final amount calculated after reservation."}
          </p>
          <div className="sc-summary-foot">
            <Coffee size={18} /> A seat. A sip. A fresh start.
          </div>
        </aside>
      </div>
    </Layout>
  );
}
