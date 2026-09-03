import Navbar from "../components/Navbar";

function Home() {
  return (
    <>
      <Navbar />

      <main>
        <h1>Welcome to Study Café</h1>
        <p>Book a comfortable seat and study without distractions.</p>

        <h2>Study Zones</h2>

        <ul>
          <li>Quiet Zone</li>
          <li>Standard Zone</li>
          <li>Group Zone</li>
        </ul>

        <a href="/booking">Book a Seat</a>
      </main>
    </>
  );
}

export default Home;