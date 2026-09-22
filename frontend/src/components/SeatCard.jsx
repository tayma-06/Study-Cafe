import { Armchair } from "lucide-react";
export default function SeatCard({ seat, state, onSelect }) {
  return (
    <button
      type="button"
      className={"sc-seat sc-seat-" + state}
      disabled={state === "booked" || state === "unavailable"}
      aria-pressed={state === "selected"}
      onClick={onSelect}
    >
      <Armchair size={25} />
      <strong>{seat.seat_number}</strong>
      <small>
        {state === "unavailable"
          ? "Unavailable"
          : state[0].toUpperCase() + state.slice(1)}
      </small>
    </button>
  );
}
