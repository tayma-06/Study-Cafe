import { Coffee } from "lucide-react";
import { Link } from "react-router-dom";

function Navbar() {
  return (
    <nav className="navbar">
      <Link to="/" className="navbar-logo"><Coffee size={24} /><span>Study Café</span></Link>
      <div className="navbar-links">
        <Link to="/">Home</Link>
          <a href="#zones">Study Zones</a>
          <a href="#services">Services</a>
          <a href="#pricing">Pricing</a>
        <Link to="/bookings">My Bookings</Link>
      </div>
      <div className="navbar-actions">
        <Link to="/login" className="btn btn-secondary">Log In</Link>
        <Link to="/login" className="btn btn-primary">Register</Link>
      </div>
    </nav>
  );
}

export default Navbar;