import { useSession } from "./CustomerUI";
import { saveSession } from "../services/api";
import { Coffee } from "lucide-react";
import { Link } from "react-router-dom";

function Navbar() {
  const user = useSession();
  return (
    <nav className="navbar">
      <Link to="/" className="navbar-logo">
        <Coffee size={24} />
        <span>Study Café</span>
      </Link>
      <div className="navbar-links">
        <Link to="/">Home</Link>
        <a href="#zones">Study Zones</a>
        <a href="#services">Services</a>
        <a href="#pricing">Pricing</a>
        {user?.role === "customer" && <Link to="/bookings">My Bookings</Link>}
        {user?.role === "admin" && <Link to="/admin">Admin</Link>}
        {user?.role === "receptionist" && (
          <Link to="/reception">Reception</Link>
        )}
      </div>
      <div className="navbar-actions">
        {user ? (
          <button
            className="btn btn-secondary"
            onClick={() => saveSession(null)}
          >
            Log out
          </button>
        ) : (
          <>
            <Link to="/login" className="btn btn-secondary">
              Log In
            </Link>
            <Link to="/register" className="btn btn-primary">
              Register
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
