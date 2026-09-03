function MyBookings() {
  return (
    <main>
      <h1>My Bookings</h1>

      <div>
        <h2>Booking #1001</h2>
        <p>Zone: Quiet Zone</p>
        <p>Seat: Seat 01</p>
        <p>Start: September 5, 2026 - 10:00 AM</p>
        <p>End: September 5, 2026 - 12:00 PM</p>
        <p>Status: Confirmed</p>

        <button>Cancel Booking</button>
      </div>

      <hr />

      <div>
        <h2>Booking #1002</h2>
        <p>Zone: Group Zone</p>
        <p>Seat: Seat 04</p>
        <p>Start: September 6, 2026 - 2:00 PM</p>
        <p>End: September 6, 2026 - 5:00 PM</p>
        <p>Status: Pending</p>

        <button>Cancel Booking</button>
      </div>
    </main>
  );
}

export default MyBookings;