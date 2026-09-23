import { useEffect, useRef, useState } from "react";
import { Link, NavLink, Navigate, useLocation } from "react-router-dom";
import { Coffee, Menu, X, ArrowRight } from "lucide-react";
import { api, getSession, saveSession } from "../services/api";
import { statusLabel } from "../utils/customer";
import "../styles/customer.css";
export function useSession() {
  const [session, set] = useState(getSession);
  useEffect(() => {
    const update = () => set(getSession());
    window.addEventListener("cafe-session", update);
    window.addEventListener("storage", update);
    return () => {
      window.removeEventListener("cafe-session", update);
      window.removeEventListener("storage", update);
    };
  }, []);
  return session;
}
export function Protected({ children, roles }) {
  const session = useSession(),
    location = useLocation();
  return session ? (
    roles && !roles.includes(session.role) ? (
      <Navigate to="/" replace />
    ) : (
      children
    )
  ) : (
    <Navigate
      to="/login"
      state={{ from: location.pathname + location.search }}
      replace
    />
  );
}
export function useLoad(path) {
  const [state, set] = useState({ loading: true, data: null, error: "" }),
    [version, bump] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    set({ loading: true, data: null, error: "" });
    api(path, { signal: controller.signal })
      .then((data) => set({ loading: false, data, error: "" }))
      .catch((e) => {
        if (e.name !== "AbortError")
          set({
            loading: false,
            data: null,
            error: e.message,
            errorStatus: e.status,
          });
      });
    return () => controller.abort();
  }, [path, version]);
  return { ...state, retry: () => bump((v) => v + 1) };
}
export function Feedback({ loading, error, retry, children }) {
  if (loading)
    return (
      <div className="sc-notice" role="status">
        Brewing your next study session…
      </div>
    );
  if (error)
    return (
      <div className="sc-notice sc-error" role="alert">
        <p>{error}</p>
        <button className="sc-button sc-secondary" onClick={retry}>
          Try again
        </button>
      </div>
    );
  return children;
}
export const Badge = ({ value }) => (
  <span className={"sc-badge sc-status-" + value}>{statusLabel(value)}</span>
);
export function Layout({ children }) {
  const user = useSession(),
    [open, setOpen] = useState(false),
    location = useLocation();
  useEffect(() => {
    setOpen(false);
    window.scrollTo({ top: 0, left: 0, behavior: "instant" });
  }, [location.pathname]);
  return (
    <div className="sc-app">
      <header className="sc-header">
        <div className="sc-nav">
          <Link className="sc-brand" to="/">
            <Coffee size={25} />
            Study Café
          </Link>
          <button
            className="sc-menu"
            aria-label="Toggle navigation"
            aria-expanded={open}
            onClick={() => setOpen(!open)}
          >
            {open ? <X /> : <Menu />}
          </button>
          <nav
            className={open ? "sc-links is-open" : "sc-links"}
            aria-label="Customer navigation"
          >
            <NavLink to="/">Home</NavLink>
            <NavLink to="/zones">Study Zones</NavLink>
            <NavLink to="/services">Services</NavLink>
            <NavLink to="/pricing">Pricing</NavLink>
            {user ? (
              <>
                <NavLink to="/bookings">My Bookings</NavLink>
                {user.role === "admin" && <NavLink to="/admin">Admin</NavLink>}
                {user.role === "receptionist" && (
                  <NavLink to="/reception">Reception</NavLink>
                )}
                <span className="sc-user">Hi, {user.name.split(" ")[0]}</span>
                <button
                  className="sc-nav-button"
                  onClick={() => saveSession(null)}
                >
                  Log out
                </button>
              </>
            ) : (
              <>
                <NavLink to="/login">Log In</NavLink>
                <Link className="sc-nav-button" to="/register">
                  Register <ArrowRight size={14} />
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>
      <main className="sc-main">{children}</main>
      <footer className="sc-footer">
        <div>
          <Link className="sc-brand" to="/">
            <Coffee size={21} />
            Study Café
          </Link>
          <p>A little space. A lot of possibility.</p>
        </div>
        <div>
          <Link to="/zones">Study Zones</Link>
          <Link to="/services">Café Services</Link>
          <Link to="/bookings">My Bookings</Link>
        </div>
        <p>
          © {new Date().getFullYear()} Study Café
          <br />
          Focus. Learn. Grow.
        </p>
      </footer>
    </div>
  );
}
export function Heading({
  eyebrow = "MAKE TIME FOR YOURSELF",
  title,
  children,
}) {
  return (
    <div className="sc-heading">
      <p className="sc-eyebrow">{eyebrow}</p>
      <h1>{title}</h1>
      <p>{children}</p>
    </div>
  );
}
export function Modal({ title, onClose, children }) {
  const ref = useRef();
  useEffect(() => {
    const dialog = ref.current;
    dialog.showModal();
    return () => dialog.close();
  }, []);
  return (
    <dialog className="sc-dialog sc-app" ref={ref} onCancel={onClose}>
      <button className="sc-close" aria-label="Close dialog" onClick={onClose}>
        <X />
      </button>
      <h2>{title}</h2>
      {children}
    </dialog>
  );
}
