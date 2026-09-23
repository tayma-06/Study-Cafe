import { useRef, useState } from "react";
import {
  LayoutDashboard,
  CalendarDays,
  CreditCard,
  Users,
  Plus,
  RefreshCw,
  SlidersHorizontal,
} from "lucide-react";
import {
  Badge,
  Feedback,
  Heading,
  Layout,
  Modal,
  useLoad,
} from "../components/CustomerUI";
import PaymentCheckout from "../components/PaymentCheckout";
import { api, post } from "../services/api";
import { money, slotLabel, today } from "../utils/customer";
import receptionArt from "../assets/illustrations/reception.png";
import "../styles/staff.css";

function Field({ label, children, ...props }) {
  return (
    <label className="sc-field">
      {label}
      {children || <input {...props} />}
    </label>
  );
}

function DeskBooking({ onSaved }) {
  const [mode, setMode] = useState("existing");
  const [query, setQuery] = useState("");
  const customers = useLoad("/staff/customers?q=" + encodeURIComponent(query));
  const services = useLoad("/services");
  const [date, setDate] = useState(today());
  const [start, setStart] = useState("10:00");
  const [end, setEnd] = useState("12:00");
  const [seats, setSeats] = useState(null);
  const [seat, setSeat] = useState("");
  const [quantities, setQuantities] = useState({});
  const [saved, setSaved] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const lock = useRef(false);
  const searchSequence = useRef(0);
  function changeTime(setter, value) {
    searchSequence.current += 1;
    setter(value);
    setSeats(null);
    setSeat("");
  }
  async function findSeats() {
    setError("");
    setBusy(true);
    const sequence = ++searchSequence.current;
    try {
      const result = await api(
        "/availability?" +
          new URLSearchParams({ date, start_time: start, end_time: end }),
      );
      if (sequence === searchSequence.current) {
        setSeats(result);
        setSeat("");
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  async function submit(event) {
    event.preventDefault();
    if (lock.current) return;
    lock.current = true;
    setBusy(true);
    setError("");
    const form = new FormData(event.currentTarget);
    const chosen = Object.entries(quantities).filter(
      ([, quantity]) => Number(quantity) > 0,
    );
    const body = {
      seat_id: Number(seat),
      start_time: `${date}T${start}:00+06:00`,
      end_time: `${date}T${end}:00+06:00`,
      services: chosen.map(([id]) => Number(id)),
      quantities: chosen.map(([, quantity]) => Number(quantity)),
    };
    if (mode === "existing") body.user_id = Number(form.get("customer_id"));
    if (mode === "new") {
      body.customer = {
        name: form.get("name"),
        email: form.get("email"),
        password: form.get("password"),
      };
      body.consent = form.get("consent") === "on";
    }
    if (mode === "guest") {
      body.guest_name = form.get("name");
      body.guest_phone = form.get("phone");
    }
    try {
      const booking = await post("/staff/bookings", body);
      setSaved(booking);
      onSaved();
    } catch (e) {
      setError(e.message);
    } finally {
      lock.current = false;
      setBusy(false);
    }
  }
  if (saved)
    return (
      <div className="sc-card">
        <div className="sc-card-body">
          <h2>Reservation created</h2>
          <p>
            Booking #{saved.booking_id}. Open Bookings to collect cash or submit
            a bKash payment.
          </p>
          <button
            className="sc-button"
            onClick={() => {
              setSaved(null);
              setSeats(null);
              setSeat("");
              setQuantities({});
            }}
          >
            Book another visit
          </button>
        </div>
      </div>
    );
  return (
    <form className="sc-card" onSubmit={submit}>
      <div className="sc-card-body">
        <h2>A seat for every visitor.</h2>
        <p>
          Ask whether the customer wants an account, or book their visit as a
          guest.
        </p>
        <div className="staff-choice" role="group" aria-label="Customer type">
          {[
            ["existing", "Existing customer"],
            ["new", "Register customer"],
            ["guest", "Guest"],
          ].map(([value, title]) => (
            <button
              type="button"
              className={mode === value ? "sc-button" : "sc-button sc-secondary"}
              onClick={() => setMode(value)}
              key={value}
            >
              {title}
            </button>
          ))}
        </div>
        {mode === "existing" ? (
          <>
            <Field
              label="Find customer"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Name or email"
            />
            <Feedback {...customers}>
              <Field label="Customer">
                <select name="customer_id" required defaultValue="">
                  <option value="">Select a customer</option>
                  {customers.data
                    ?.filter((c) => c.role === "customer")
                    .map((c) => (
                      <option key={c.user_id} value={c.user_id}>
                        {c.name} · {c.email}
                      </option>
                    ))}
                </select>
              </Field>
            </Feedback>
          </>
        ) : (
          <div className="staff-form-grid">
            <Field label="Customer name" name="name" required maxLength={100} />
            {mode === "new" ? (
              <>
                <Field
                  label="Customer email"
                  name="email"
                  type="email"
                  required
                />
                <Field
                  label="Password chosen by customer"
                  name="password"
                  type="password"
                  required
                  minLength={8}
                  maxLength={72}
                  autoComplete="new-password"
                />
                <label className="staff-consent">
                  <input type="checkbox" name="consent" required /> The customer
                  agrees to create an account.
                </label>
              </>
            ) : (
              <Field
                label="Guest phone"
                name="phone"
                type="tel"
                required
                pattern="[+0-9]{7,15}"
              />
            )}
          </div>
        )}
        <hr />
        <h3>Visit details</h3>
        <p className="sc-small">All times are in Dhaka time.</p>
        <div className="staff-form-grid">
          <Field
            label="Date"
            type="date"
            min={today()}
            value={date}
            onChange={(e) => changeTime(setDate, e.target.value)}
            required
          />
          <Field
            label="Start"
            type="time"
            value={start}
            onChange={(e) => changeTime(setStart, e.target.value)}
            required
          />
          <Field
            label="End"
            type="time"
            value={end}
            onChange={(e) => changeTime(setEnd, e.target.value)}
            required
          />
        </div>
        <button
          type="button"
          className="sc-button sc-secondary"
          disabled={busy || !date || start >= end}
          onClick={findSeats}
        >
          Find available seats
        </button>
        {seats && (
          <Field label="Available seat">
            <select
              required
              value={seat}
              onChange={(e) => setSeat(e.target.value)}
            >
              <option value="">
                {seats.length
                  ? "Choose a seat"
                  : "No seats available for this time"}
              </option>
              {seats.map((s) => (
                <option key={s.seat_id} value={s.seat_id}>
                  {s.zone_name} · {s.seat_number} · {money(s.price_per_hour)}/hour
                </option>
              ))}
            </select>
          </Field>
        )}
        <hr />
        <h3>Café add-ons</h3>
        <Feedback {...services}>
          <div className="staff-form-grid">
            {services.data?.map((s) => (
              <Field
                key={s.service_id}
                label={`${s.name} · ${money(s.price)}`}
                type="number"
                min={0}
                max={100}
                value={quantities[s.service_id] || 0}
                onChange={(e) =>
                  setQuantities({ ...quantities, [s.service_id]: e.target.value })
                }
              />
            ))}
          </div>
        </Feedback>
        {error && (
          <p className="sc-error" role="alert">
            {error}
          </p>
        )}
        <button className="sc-button" disabled={busy || !seat}>
          {busy ? "Saving…" : "Create reservation"}
        </button>
      </div>
    </form>
  );
}

function BookingList({ state, onSaved }) {
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const lock = useRef(false);
  async function action(booking, kind, amount) {
    if (lock.current) return;
    lock.current = true;
    setBusy(true);
    setError("");
    try {
      if (kind === "cash")
        await post("/staff/payments/cash", {
          booking_id: booking.booking_id,
          amount_received: amount,
        });
      else await post(`/bookings/${booking.booking_id}/${kind}`);
      setSelected(null);
      onSaved();
    } catch (e) {
      setError(e.message);
    } finally {
      lock.current = false;
      setBusy(false);
    }
  }
  const rows = (state.data || []).filter((b) =>
    `${b.customer_name} ${b.booking_id} ${b.seat_number}`
      .toLowerCase()
      .includes(search.toLowerCase()),
  );
  return (
    <>
      <div className="staff-section-heading">
        <h2>Bookings</h2>
        <Field
          label="Search bookings"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Customer, seat, or booking ID"
        />
      </div>
      {error && (
        <p role="alert" className="sc-error">
          {error}
        </p>
      )}
      <Feedback {...state}>
        <div className="staff-table-wrap">
          <table className="staff-table">
            <thead>
              <tr>
                <th>Customer</th>
                <th>Seat & visit</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((b) => (
                <tr key={b.booking_id}>
                  <td>
                    <strong>{b.customer_name || "Guest"}</strong>
                    <small>
                      #{b.booking_id}
                      {!b.user_id ? " · Guest" : ""}
                    </small>
                  </td>
                  <td>
                    {b.zone_name} · {b.seat_number}
                    <small>{slotLabel(b.time_slot)}</small>
                  </td>
                  <td>
                    {money(b.total)}
                    <small>
                      {b.payment_status === "completed"
                        ? "Paid · " + b.method
                        : "Awaiting payment"}
                    </small>
                  </td>
                  <td>
                    <Badge value={b.booking_status} />
                  </td>
                  <td>
                    <div className="staff-row-actions">
                      {b.booking_status === "pending" && (
                        <>
                          <button
                            disabled={busy}
                            onClick={() => {
                              setError("");
                              setSelected({ ...b, kind: "cash" });
                            }}
                          >
                            Collect cash
                          </button>
                          <button
                            disabled={busy}
                            onClick={() => setSelected({ ...b, kind: "demo" })}
                          >
                            bKash demo
                          </button>
                          <button
                            disabled={busy}
                            onClick={() =>
                              setSelected({ ...b, kind: "cancel" })
                            }
                          >
                            Cancel
                          </button>
                        </>
                      )}
                      {b.booking_status === "confirmed" && (
                        <button
                          disabled={busy}
                          onClick={() => action(b, "check-in")}
                        >
                          Check in
                        </button>
                      )}
                      {b.booking_status === "checked_in" && (
                        <button
                          disabled={busy}
                          onClick={() => action(b, "check-out")}
                        >
                          Check out
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!rows.length && <p className="sc-notice">No bookings found.</p>}
        </div>
      </Feedback>
      {selected && (
        <Modal
          title={
            selected.kind === "cash"
              ? "Collect cash"
              : selected.kind === "demo"
                ? "Customer payment"
                : "Cancel booking?"
          }
          onClose={() => !busy && setSelected(null)}
        >
          <p>
            {selected.customer_name} · #{selected.booking_id}
          </p>
          {selected.kind === "demo" ? (
            <PaymentCheckout
              bookingId={selected.booking_id}
              amount={selected.total}
              onSubmitted={onSaved}
            />
          ) : selected.kind === "cash" ? (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                action(
                  selected,
                  "cash",
                  new FormData(e.currentTarget).get("amount"),
                );
              }}
            >
              <p>
                Total due: <strong>{money(selected.total)}</strong>
              </p>
              <Field
                label="Cash received (exact amount)"
                name="amount"
                type="number"
                min="0.01"
                step="0.01"
                required
              />
              <p className="sc-small">
                Confirm only after receiving the money.
              </p>
              <button className="sc-button" disabled={busy}>
                Confirm cash received
              </button>
            </form>
          ) : (
            <>
              <p>
                This releases the seat. A pending payment must be rejected
                first.
              </p>
              <button
                className="sc-button sc-danger"
                disabled={busy}
                onClick={() => action(selected, "cancel")}
              >
                Cancel booking
              </button>
            </>
          )}
          {error && (
            <p role="alert" className="sc-error">
              {error}
            </p>
          )}
        </Modal>
      )}
    </>
  );
}

function Payments({ state, onSaved }) {
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const lock = useRef(false);
  async function review(event) {
    event.preventDefault();
    if (lock.current) return;
    lock.current = true;
    setBusy(true);
    setError("");
    try {
      await post(`/staff/payment-requests/${selected.transaction_id}/review`, {
        decision: selected.decision,
        note: new FormData(event.currentTarget).get("note"),
      });
      setSelected(null);
      onSaved();
    } catch (e) {
      setError(e.message);
    } finally {
      lock.current = false;
      setBusy(false);
    }
  }
  return (
    <>
      <h2>Payment approvals</h2>
      <p>
        bKash transactions here are simulated. Approval confirms the booking; no
        money moves.
      </p>
      <Feedback {...state}>
        <div className="staff-table-wrap">
          <table className="staff-table">
            <thead>
              <tr>
                <th>Transaction</th>
                <th>Customer</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Review</th>
              </tr>
            </thead>
            <tbody>
              {state.data?.map((r) => (
                <tr key={r.transaction_id}>
                  <td>
                    <strong className="sc-transaction">
                      {r.transaction_id}
                    </strong>
                    <small>Booking #{r.booking_id} · bKash demo</small>
                  </td>
                  <td>
                    {r.customer_name}
                    <small>{r.phone}</small>
                  </td>
                  <td>{money(r.amount)}</td>
                  <td>
                    <Badge value={r.status} />
                  </td>
                  <td>
                    {r.status === "pending" ? (
                      <div className="staff-row-actions">
                        <button
                          onClick={() => {
                            setError("");
                            setSelected({ ...r, decision: "approved" });
                          }}
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => {
                            setError("");
                            setSelected({ ...r, decision: "rejected" });
                          }}
                        >
                          Reject
                        </button>
                      </div>
                    ) : (
                      <>
                        <small>{r.reviewer_name}</small>
                        <small>{r.review_note}</small>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!state.data?.length && (
            <p className="sc-notice">No payment requests yet.</p>
          )}
        </div>
      </Feedback>
      {selected && (
        <Modal
          title={
            selected.decision === "approved"
              ? "Approve payment?"
              : "Reject payment?"
          }
          onClose={() => !busy && setSelected(null)}
        >
          <p>{selected.transaction_id}</p>
          <p>
            {selected.customer_name} · {money(selected.amount)}
          </p>
          <form onSubmit={review}>
            <Field
              label="Review note"
              name="note"
              maxLength={500}
              required={selected.decision === "rejected"}
            />
            {error && (
              <p role="alert" className="sc-error">
                {error}
              </p>
            )}
            <button className="sc-button" disabled={busy}>
              {busy
                ? "Saving…"
                : selected.decision === "approved"
                  ? "Approve & confirm booking"
                  : "Reject payment"}
            </button>
          </form>
        </Modal>
      )}
    </>
  );
}

function Accounts({ admin, onSaved }) {
  const [query, setQuery] = useState("");
  const state = useLoad("/staff/customers?q=" + encodeURIComponent(query));
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const lock = useRef(false);
  async function submit(event) {
    event.preventDefault();
    if (lock.current) return;
    lock.current = true;
    setBusy(true);
    setError("");
    const f = new FormData(event.currentTarget);
    try {
      if (selected === "new")
        await post("/admin/receptionists", {
          name: f.get("name"),
          email: f.get("email"),
          password: f.get("password"),
        });
      else
        await post(`/admin/users/${selected.user_id}/role`, {
          role: selected.role === "receptionist" ? "customer" : "receptionist",
          work_email: selected.role === "receptionist" ? null : f.get("email"),
        });
      setSelected(null);
      state.retry();
      onSaved();
    } catch (e) {
      setError(e.message);
    } finally {
      lock.current = false;
      setBusy(false);
    }
  }
  return (
    <>
      <div className="staff-section-heading">
        <h2>{admin ? "Customers & staff" : "Customers"}</h2>
        {admin && (
          <button
            className="sc-button"
            onClick={() => {
              setError("");
              setSelected("new");
            }}
          >
            <Plus size={16} /> Create receptionist
          </button>
        )}
      </div>
      <Field
        label="Find an account"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Name or email"
      />
      <Feedback {...state}>
        <div className="staff-table-wrap">
          <table className="staff-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                {admin && <th>Access</th>}
              </tr>
            </thead>
            <tbody>
              {state.data?.map((c) => (
                <tr key={c.user_id}>
                  <td>{c.name}</td>
                  <td>
                    {c.email}
                    {c.work_email && <small>Work: {c.work_email}</small>}
                  </td>
                  <td>
                    <Badge value={c.role} />
                  </td>
                  {admin && (
                    <td>
                      {c.role !== "admin" && (
                        <button
                          className="sc-button sc-secondary"
                          onClick={() => {
                            setError("");
                            setSelected(c);
                          }}
                        >
                          {c.role === "receptionist"
                            ? "Remove staff access"
                            : "Grant receptionist"}
                        </button>
                      )}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
          {!state.data?.length && (
            <p className="sc-notice">No accounts found.</p>
          )}
        </div>
      </Feedback>
      {selected && (
        <Modal
          title={
            selected === "new"
              ? "Create receptionist"
              : selected.role === "receptionist"
                ? "Remove staff access?"
                : "Grant receptionist access"
          }
          onClose={() => !busy && setSelected(null)}
        >
          <form onSubmit={submit}>
            {selected === "new" && (
              <Field label="Full name" name="name" required maxLength={100} />
            )}
            {selected.role !== "receptionist" && (
              <Field label="Work email" name="email" type="email" required />
            )}
            {selected === "new" && (
              <Field
                label="Password"
                name="password"
                type="password"
                minLength={8}
                maxLength={72}
                required
                autoComplete="new-password"
              />
            )}
            <p className="sc-small">
              Receptionists sign in with their café work email. Only the admin
              can grant this role.
            </p>
            {error && (
              <p role="alert" className="sc-error">
                {error}
              </p>
            )}
            <button className="sc-button" disabled={busy}>
              Save access
            </button>
          </form>
        </Modal>
      )}
    </>
  );
}

function Management({ kind }) {
  const state = useLoad("/" + kind);
  const zones = useLoad("/zones");
  const [selected, setSelected] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const lock = useRef(false);
  const idKey = { zones: "zone_id", seats: "seat_id", services: "service_id" }[
    kind
  ];
  async function submit(event) {
    event.preventDefault();
    if (lock.current) return;
    lock.current = true;
    setBusy(true);
    setError("");
    const f = new FormData(event.currentTarget);
    const body = { [idKey]: selected[idKey] || null };
    if (kind === "seats")
      Object.assign(body, {
        zone_id: Number(f.get("zone_id")),
        seat_number: f.get("seat_number"),
        status: f.get("status"),
      });
    else {
      Object.assign(body, {
        name: f.get("name"),
        description: f.get("description"),
        [kind === "zones" ? "price_per_hour" : "price"]: f.get("price"),
      });
      if (kind === "zones")
        body.facilities = f
          .get("facilities")
          .split(",")
          .map((v) => v.trim())
          .filter(Boolean);
    }
    try {
      await post("/admin/" + kind, body);
      setSelected(null);
      state.retry();
    } catch (e) {
      setError(e.message);
    } finally {
      lock.current = false;
      setBusy(false);
    }
  }
  return (
    <>
      <div className="staff-section-heading">
        <h2>
          {kind === "zones"
            ? "Zones & pricing"
            : kind === "seats"
              ? "Seats & availability"
              : "Café services"}
        </h2>
        <button
          className="sc-button"
          onClick={() => {
            setError("");
            setSelected({});
          }}
        >
          Add {kind.slice(0, -1)}
        </button>
      </div>
      <Feedback {...state}>
        <div className="staff-table-wrap">
          <table className="staff-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>{kind === "seats" ? "Zone" : "Price"}</th>
                <th>Details</th>
                <th>Edit</th>
              </tr>
            </thead>
            <tbody>
              {state.data?.map((r) => (
                <tr key={r[idKey]}>
                  <td>{r.name || r.seat_number}</td>
                  <td>
                    {kind === "seats"
                      ? zones.data?.find((z) => z.zone_id === r.zone_id)?.name
                      : money(r.price ?? r.price_per_hour)}
                  </td>
                  <td>
                    {kind === "seats" ? (
                      <Badge value={r.status} />
                    ) : (
                      r.description
                    )}
                  </td>
                  <td>
                    <button
                      className="sc-button sc-secondary"
                      onClick={() => {
                        setError("");
                        setSelected(r);
                      }}
                    >
                      Edit
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!state.data?.length && <p className="sc-notice">No {kind} yet.</p>}
        </div>
      </Feedback>
      {selected && (
        <Modal
          title={`${selected[idKey] ? "Edit" : "Add"} ${kind.slice(0, -1)}`}
          onClose={() => !busy && setSelected(null)}
        >
          <form onSubmit={submit}>
            {kind === "seats" ? (
              <>
                <Feedback {...zones}>
                  <Field label="Zone">
                    <select
                      name="zone_id"
                      defaultValue={selected.zone_id || ""}
                      required
                    >
                      <option value="">Choose a zone</option>
                      {zones.data?.map((z) => (
                        <option key={z.zone_id} value={z.zone_id}>
                          {z.name}
                        </option>
                      ))}
                    </select>
                  </Field>
                </Feedback>
                <Field
                  label="Seat number"
                  name="seat_number"
                  defaultValue={selected.seat_number}
                  required
                  maxLength={30}
                />
                <Field label="Availability">
                  <select
                    name="status"
                    defaultValue={selected.status || "available"}
                  >
                    <option value="available">Available</option>
                    <option value="unavailable">Unavailable</option>
                  </select>
                </Field>
              </>
            ) : (
              <>
                <Field
                  label="Name"
                  name="name"
                  defaultValue={selected.name}
                  required
                  maxLength={100}
                />
                <Field
                  label="Description"
                  name="description"
                  defaultValue={selected.description}
                />
                <Field
                  label={kind === "zones" ? "Hourly rate (BDT)" : "Price (BDT)"}
                  name="price"
                  type="number"
                  min={kind === "zones" ? "0.01" : "0"}
                  step="0.01"
                  defaultValue={selected.price ?? selected.price_per_hour}
                  required
                />
                {kind === "zones" && (
                  <Field
                    label="Facilities (comma separated)"
                    name="facilities"
                    defaultValue={selected.facilities?.join(", ")}
                  />
                )}
              </>
            )}
            {error && (
              <p role="alert" className="sc-error">
                {error}
              </p>
            )}
            <button className="sc-button" disabled={busy}>
              Save changes
            </button>
          </form>
        </Modal>
      )}
    </>
  );
}

export default function StaffDashboard({ admin = false }) {
  const [tab, setTab] = useState("overview");
  const [manage, setManage] = useState("zones");
  const summary = useLoad("/staff/summary");
  const bookings = useLoad("/staff/bookings");
  const payments = useLoad("/payment-requests");
  function refresh() {
    summary.retry();
    bookings.retry();
    payments.retry();
  }
  const tabs = [
    ["overview", "Overview", LayoutDashboard],
    ["new", "Book a visit", Plus],
    ["bookings", "Bookings", CalendarDays],
    ["payments", "Payment approvals", CreditCard],
    ["customers", admin ? "Customers & staff" : "Customers", Users],
    ...(admin ? [["management", "Café management", SlidersHorizontal]] : []),
  ];
  const activeTab = tabs.find(([key]) => key === tab)?.[1];
  return (
    <Layout>
      <div className="sc-heading-row">
        <Heading
          eyebrow={admin ? "ADMINISTRATION" : "RECEPTION DESK"}
          title={activeTab}
        >
          {admin
            ? "Half the work, twice the calm—customers, bookings, and prices in one place."
            : "Book visits, record payments, and keep the café flowing."}
        </Heading>
        <button className="sc-button sc-secondary" onClick={refresh}>
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>
      <div className="sc-tabs" aria-label="Workspace navigation">
        {tabs.map(([key, label, Icon]) => (
          <button
            key={key}
            aria-pressed={tab === key}
            className={tab === key ? "active" : ""}
            onClick={() => setTab(key)}
          >
            <Icon size={16} />
            {label}
            {key === "payments" &&
              Number(summary.data?.pending_payments) > 0 && (
                <span className="sc-badge sc-status-confirmed">
                  {summary.data.pending_payments}
                </span>
              )}
          </button>
        ))}
      </div>
      {tab === "overview" && (
        <>
          <section className="staff-welcome">
            <div>
              <p className="sc-eyebrow">WELCOME BACK</p>
              <h2>
                Keep the café running
                <br />
                as calmly as it feels.
              </h2>
              <p>
                Bookings, visitors, and the little details—all in one place.
              </p>
              <button className="sc-button" onClick={() => setTab("new")}>
                <Plus size={16} />
                Book a visit
              </button>
            </div>
            <img
              src={receptionArt}
              alt="Illustration of the Study Café reception"
            />
          </section>
          <Feedback {...summary}>
            <div className="staff-stats">
              {[
                ["Total bookings", summary.data?.total_bookings],
                [
                  "Seat inventory",
                  `${summary.data?.total_seats ?? 0} seats`,
                ],
                ["Visits today", summary.data?.today_bookings],
                ["Recorded today", money(summary.data?.today_revenue)],
              ].map(([label, value]) => (
                <div className="sc-card" key={label}>
                  <div className="sc-card-body">
                    <p>{label}</p>
                    <strong>{value}</strong>
                  </div>
                </div>
              ))}
            </div>
            <p className="sc-small">
              Recorded totals include approved demo payments and recorded cash.
              Today follows Dhaka time.
            </p>
          </Feedback>
          <div className="staff-section-heading">
            <h2>Recent visits</h2>
            <button
              className="sc-button sc-secondary"
              onClick={() => setTab("payments")}
            >
              {summary.data?.pending_payments || 0} awaiting payment review
            </button>
          </div>
          <BookingList
            state={{ ...bookings, data: bookings.data?.slice(0, 6) }}
            onSaved={refresh}
          />
        </>
      )}
      {tab === "new" && <DeskBooking onSaved={refresh} />}
      {tab === "bookings" && (
        <>
          <p className="sc-small">Showing the most recent 500 bookings.</p>
          <BookingList state={bookings} onSaved={refresh} />
        </>
      )}
      {tab === "payments" && (
        <>
          <p className="sc-small">
            Showing the most recent 500 payment requests.
          </p>
          <Payments state={payments} onSaved={refresh} />
        </>
      )}
      {tab === "customers" && <Accounts admin={admin} onSaved={refresh} />}
      {admin && tab === "management" && (
        <>
          <div
            className="staff-choice"
            role="group"
            aria-label="Management section"
          >
            {(
              [
                ["zones", "Zones & pricing"],
                ["seats", "Seats & availability"],
                ["services", "Café services"],
              ]
            ).map(([value, label]) => (
              <button
                type="button"
                key={value}
                className={
                  manage === value ? "sc-button" : "sc-button sc-secondary"
                }
                onClick={() => setManage(value)}
              >
                {label}
              </button>
            ))}
          </div>
          <Management kind={manage} key={manage} />
        </>
      )}
    </Layout>
  );
}
