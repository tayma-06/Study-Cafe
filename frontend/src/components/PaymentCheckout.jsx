import { useRef, useState } from "react";
import { post } from "../services/api";
import "../styles/staff.css";
import { money } from "../utils/customer";

export default function PaymentCheckout({ bookingId, amount, onSubmitted }) {
  const [phone, setPhone] = useState("");
  const [receipt, setReceipt] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const lock = useRef(false);
  async function pay(event) {
    event.preventDefault();
    if (lock.current) return;
    lock.current = true;
    setBusy(true);
    setError("");
    try {
      const result = await post("/payment-requests", {
        booking_id: bookingId,
        phone,
      });
      setReceipt(result);
      onSubmitted?.(result);
    } catch (e) {
      setError(e.message);
    } finally {
      lock.current = false;
      setBusy(false);
    }
  }
  return (
    <section className="sc-checkout" aria-label="Payment checkout">
      <p className="sc-eyebrow">PAYMENT DEMO</p>
      <h3>{receipt ? "Payment submitted" : "Pay with bKash"}</h3>
      <p className="sc-small">
        Simulated payment only. No money is transferred. Do not enter a PIN or
        OTP.
      </p>
      {receipt ? (
        <div role="status">
          <p>
            Amount: <strong>{money(receipt.amount)}</strong>
          </p>
          <p>
            Transaction ID
            <br />
            <strong className="sc-transaction">{receipt.transaction_id}</strong>
          </p>
          <p>
            Awaiting admin or receptionist approval. Your booking will be
            confirmed after approval.
          </p>
        </div>
      ) : (
        <form onSubmit={pay}>
          <label className="sc-field">
            bKash mobile number
            <input
              required
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              pattern="[+0-9]{7,15}"
              placeholder="01XXXXXXXXX"
            />
          </label>
          {error && (
            <p className="sc-error" role="alert">
              {error}
            </p>
          )}
          <button className="sc-button" disabled={busy}>
            {busy ? "Submitting…" : `Pay ${money(amount)} with bKash`}
          </button>
        </form>
      )}
    </section>
  );
}
