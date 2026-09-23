import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Booking from "./pages/Booking";
import MyBookings from "./pages/MyBookings";
import Discover from "./pages/Discover";
import Admin from "./pages/Admin";
import Reception from "./pages/Reception";
import { Layout, Heading, Protected } from "./components/CustomerUI";
export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login key="login" />} />
        <Route path="/register" element={<Login key="register" register />} />
        <Route path="/zones" element={<Discover />} />
        <Route path="/services" element={<Discover kind="services" />} />
        <Route path="/pricing" element={<Discover kind="pricing" />} />
        <Route
          path="/booking"
          element={
            <Protected roles={["customer"]}>
              <Booking />
            </Protected>
          }
        />
        <Route
          path="/bookings"
          element={
            <Protected roles={["customer"]}>
              <MyBookings />
            </Protected>
          }
        />
        <Route
          path="/my-bookings"
          element={
            <Protected roles={["customer"]}>
              <MyBookings />
            </Protected>
          }
        />
        <Route
          path="/admin"
          element={
            <Protected roles={["admin"]}>
              <Admin />
            </Protected>
          }
        />
        <Route
          path="/reception"
          element={
            <Protected roles={["admin", "receptionist"]}>
              <Reception />
            </Protected>
          }
        />
        <Route
          path="*"
          element={
            <Layout>
              <Heading title="This spot is still empty.">
                We couldn’t find that page.
              </Heading>
              <Link className="sc-button" to="/">
                Back to home
              </Link>
            </Layout>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
