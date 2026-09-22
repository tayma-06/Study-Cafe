import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Coffee, Eye, EyeOff, ArrowRight } from "lucide-react";
import { Layout, useSession } from "../components/CustomerUI";
import { post, saveSession } from "../services/api";
import reception from "../assets/illustrations/reception.png";
export default function Login({ register = false }) {
  const [show, setShow] = useState(false),
    [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  const location = useLocation(),
    navigate = useNavigate(),
    user = useSession();
  const destination =
    location.state?.from?.startsWith("/") &&
    !location.state.from.startsWith("//")
      ? location.state.from
      : "/bookings";
  async function submit(event) {
    event.preventDefault();
    setError("");
    const form = new FormData(event.currentTarget);
    const password = form.get("password");
    if (register && password !== form.get("confirm")) {
      setError("Your passwords do not match.");
      return;
    }
    if (register && new TextEncoder().encode(password).length > 72) {
      setError("Please use a password of at most 72 bytes.");
      return;
    }
    setBusy(true);
    try {
      if (register) {
        await post("/users", {
          name: form.get("name").trim(),
          email: form.get("email").trim(),
          password,
        });
        navigate("/login", {
          state: { registered: true, from: destination },
          replace: true,
        });
        return;
      }
      const result = await post("/login", {
        email: form.get("email").trim(),
        password,
      });
      saveSession(result, form.get("remember") === "on");
      navigate(destination, { replace: true });
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <Layout>
      <div className="sc-auth">
        <section className="sc-auth-art">
          <p className="sc-eyebrow">YOUR EVERYDAY STUDY RETREAT</p>
          <h1>
            A place to settle in.
            <br />
            Room to grow.
          </h1>
          <img
            src={reception}
            alt="Illustrated Study Café reception with warm lighting and plants"
          />
          <p>
            A comfortable seat, a fresh start,
            <br />
            and a little focus for what comes next.
          </p>
          <span className="sc-art-sign">
            <Coffee size={19} /> Focus. Learn. Grow.
          </span>
        </section>
        <section className="sc-auth-form">
          <p className="sc-eyebrow">WELCOME TO STUDY CAFÉ</p>
          <h2>{register ? "Make yourself at home." : "Welcome back."}</h2>
          <p>
            {register
              ? "Create an account and find your favorite study spot."
              : "Your next productive chapter starts here."}
          </p>
          {user ? (
            <div className="sc-notice">
              You’re logged in as {user.name}.{" "}
              <Link to="/bookings">View your bookings →</Link>
            </div>
          ) : (
            <>
              <form onSubmit={submit}>
                {register && (
                  <label>
                    Full name
                    <input
                      name="name"
                      required
                      maxLength={100}
                      autoComplete="name"
                    />
                  </label>
                )}
                <label>
                  Email address
                  <input
                    name="email"
                    type="email"
                    required
                    autoComplete="email"
                    placeholder="you@example.com"
                  />
                </label>
                <label>
                  Password
                  <div className="sc-password">
                    <input
                      name="password"
                      type={show ? "text" : "password"}
                      required
                      minLength={register ? 8 : undefined}
                      autoComplete={
                        register ? "new-password" : "current-password"
                      }
                    />
                    <button
                      type="button"
                      aria-label={show ? "Hide password" : "Show password"}
                      onClick={() => setShow(!show)}
                    >
                      {show ? <EyeOff size={19} /> : <Eye size={19} />}
                    </button>
                  </div>
                </label>
                {register ? (
                  <>
                    <p className="sc-small">Use at least 8 characters.</p>
                    <label>
                      Confirm password
                      <input
                        name="confirm"
                        type={show ? "text" : "password"}
                        required
                        autoComplete="new-password"
                      />
                    </label>
                  </>
                ) : (
                  <label className="sc-checkbox">
                    <input type="checkbox" name="remember" /> Keep me signed in
                    on this device
                  </label>
                )}
                {location.state?.registered && !register && (
                  <p className="sc-success" role="status">
                    Your account is ready. Log in to continue.
                  </p>
                )}
                {error && (
                  <p className="sc-error" role="alert">
                    {error}
                  </p>
                )}
                <button className="sc-button sc-wide" disabled={busy}>
                  {busy
                    ? "Please wait…"
                    : register
                      ? "Create account"
                      : "Log in"}{" "}
                  <ArrowRight size={17} />
                </button>
              </form>
              <p className="sc-auth-switch">
                {register ? "Already have an account?" : "New to Study Café?"}{" "}
                <Link
                  state={{ from: destination }}
                  to={register ? "/login" : "/register"}
                >
                  {register ? "Log in" : "Create an account"}
                </Link>
              </p>
              {!register && (
                <details className="sc-help">
                  <summary>Need help signing in?</summary>
                  <p>
                    Please speak with the café reception if you have forgotten
                    your password. Online password reset is not available yet.
                  </p>
                </details>
              )}
            </>
          )}
        </section>
      </div>
    </Layout>
  );
}
