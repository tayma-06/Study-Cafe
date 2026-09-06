import { useEffect, useState } from "react";
import {
  ArrowRight,
  CalendarCheck,
  Coffee,
  ReceiptText,
  ShieldCheck,
} from "lucide-react";
import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import ZoneCard from "../components/ZoneCard";
import cafeExterior from "../assets/illustrations/cafe-exterior.jpeg";
import quietZone from "../assets/illustrations/quiet-zone.png";
import standardZone from "../assets/illustrations/standard-zone.png";
import groupZone from "../assets/illustrations/group-zone.png";
import reception from "../assets/illustrations/reception.png";
import serviceArea from "../assets/illustrations/service-area.png";

function Home() {
  const [currentImage, setCurrentImage] = useState(0);
  const heroImages = [
    cafeExterior,
    quietZone,
    standardZone,
    groupZone,
    reception,
    serviceArea,
  ];
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImage(
        (previous) => (previous + 1) % heroImages.length
      );
    }, 5000);
    return () => clearInterval(interval);
  }, [heroImages.length]);
  const zones = [
    {
      name: "Quiet Zone",
      image: quietZone,
      description:
        "A calm, distraction-free space for focused individual study.",
      price: "From ৳60/hour",
    },
    {
      name: "Standard Zone",
      image: standardZone,
      description:
        "A comfortable study space for everyday work, reading and assignments.",
      price: "View pricing",
    },
    {
      name: "Group Zone",
      image: groupZone,
      description:
        "Private group spaces designed for discussions, teamwork and projects.",
      price: "View pricing",
    },
  ];
  const features = [
    {
      icon: <CalendarCheck size={28} />,
      title: "Easy Booking",
      description:
        "Choose your zone, seat and preferred time in just a few steps.",
    },
    {
      icon: <Coffee size={28} />,
      title: "Café Services",
      description:
        "Order drinks, snacks and other services while you study.",
    },
    {
      icon: <ShieldCheck size={28} />,
      title: "Secure & Reliable",
      description:
        "Your bookings and payments are handled through a reliable system.",
    },
    {
      icon: <ReceiptText size={28} />,
      title: "Transparent Pricing",
      description:
        "Know your booking and service costs before completing your reservation.",
    },
  ];
  return (
    <div className="page">
      <Navbar />

      <main>
        {/*Hero Section*/}
        <section className="hero">
          <div className="hero-image-wrapper">
            <div
              className="hero-tape"
              style={{
                transform: `translateY(-${currentImage * 100}%)`,
              }}
            >
              {heroImages.map((src, index) => (
                <img
                  key={index}
                  src={src}
                  alt="Study Café"
                  className="hero-tape-image"
                />
              ))}
            </div>
            <div className="hero-scrim" />
            <div className="hero-dots">
              {heroImages.map((_, index) => (
                <button
                  key={index}
                  className={
                    index === currentImage
                      ? "active"
                      : ""
                  }
                  onClick={() =>
                    setCurrentImage(index)
                  }
                  aria-label={`Show image ${
                    index + 1
                  }`}
                />
              ))}
            </div>
          </div>
          <div className="hero-content">
            <span className="eyebrow">
              A better place to study
            </span>
            <h1>
              Find your perfect
              <span> study spot.</span>
            </h1>
            <div className="hero-title-shade" />
            <p>
              A cozy, comfortable study café where you can
              focus, get things done and enjoy your time.
            </p>
            <div className="hero-actions">
              <Link
                to="/booking"
                className="btn btn-primary btn-large"
              >
                Book a Seat
                <ArrowRight size={18} />
              </Link>
              <a
                href="#zones"
                className="btn btn-secondary btn-large"
              >
                Explore Zones
              </a>
            </div>
          </div>
        </section>
        {/* Study Zones */}
        <section
          className="section"
          id="zones"
        >
          <div className="section-heading">
            <div>
              <span className="eyebrow">
                Choose your space
              </span>
              <h2>Study Zones</h2>
            </div>
            <p>
              Different spaces for different ways of
              studying. Find the one that works best for you.
            </p>
          </div>
          <div className="zones-grid">
            {zones.map((zone) => (
              <ZoneCard
                key={zone.name}
                image={zone.image}
                name={zone.name}
                description={zone.description}
                price={zone.price}
              />
            ))}
          </div>
        </section>
        {/* Features */}
        <section
          className="section features-section"
          id="services"
        >
          <div className="section-heading centered">
            <span className="eyebrow">
              Why Study Café?
            </span>
            <h2>
              Everything you need to focus
            </h2>
            <p>
              Designed to make your study sessions
              comfortable, convenient and productive.
            </p>
          </div>
          <div className="features-grid">
            {features.map((feature) => (
              <div
                className="feature-card"
                key={feature.title}
              >
                <div className="feature-icon">
                  {feature.icon}
                </div>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </div>
            ))}
          </div>
        </section>
        {/*CTA*/}
        <section
          className="cta-section"
          id="pricing"
        >
          <div>
            <span className="eyebrow">
              Ready to focus?
            </span>
            <h2>
              Find your perfect study spot today.
            </h2>
            <p>
              Pick a zone, choose your seat and start
              your next productive session.
            </p>
          </div>
          <Link
            to="/booking"
            className="btn btn-primary btn-large"
          >
            Book a Seat
            <ArrowRight size={18} />
          </Link>
        </section>
      </main>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-brand">
          <div className="navbar-logo">
            <Coffee size={22} />
            <span>Study Café</span>
          </div>
          <p>
            A cozy place to focus, learn and get things done.
          </p>
        </div>
        <div className="footer-links">
          <div>
            <h4>Explore</h4>
            <a href="#zones">
              Study Zones
            </a>
            <a href="#services">
              Services
            </a>
            <a href="#pricing">
              Pricing
            </a>
          </div>
          <div>
            <h4>Account</h4>
            <Link to="/login">
              Log In
            </Link>
            <Link to="/booking">
              Book a Seat
            </Link>
            <Link to="/bookings">
              My Bookings
            </Link>
          </div>
        </div>
        <div className="footer-bottom">
          <span>
            © 2026 Study Café. All rights reserved.
          </span>
          <span>
            Study better. Together.
          </span>
        </div>
      </footer>
    </div>
  );
}

export default Home;