function Booking() {
  return (
    <main>
      <h1>Book a Seat</h1>

      <form>
        <div>
          <label>Study Zone</label>
          <br />
          <select>
            <option>Quiet Zone</option>
            <option>Standard Zone</option>
            <option>Group Zone</option>
          </select>
        </div>

        <br />

        <div>
          <label>Seat</label>
          <br />
          <select>
            <option>Seat 01</option>
            <option>Seat 02</option>
            <option>Seat 03</option>
          </select>
        </div>

        <br />

        <div>
          <label>Start Time</label>
          <br />
          <input type="datetime-local" />
        </div>

        <br />

        <div>
          <label>End Time</label>
          <br />
          <input type="datetime-local" />
        </div>

        <br />

        <button type="submit">Book Seat</button>
      </form>
    </main>
  );
}

export default Booking;