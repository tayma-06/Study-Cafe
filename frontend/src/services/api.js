const base = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(
  /\/$/,
  "",
);
const key = "study-cafe-session";
export function getSession() {
  try {
    return JSON.parse(
      sessionStorage.getItem(key) || localStorage.getItem(key) || "null",
    );
  } catch {
    return null;
  }
}
export function saveSession(value, remember = false) {
  localStorage.removeItem(key);
  sessionStorage.removeItem(key);
  if (value)
    (remember ? localStorage : sessionStorage).setItem(
      key,
      JSON.stringify(value),
    );
  window.dispatchEvent(new Event("cafe-session"));
}
export async function api(path, options = {}) {
  const token = getSession()?.token;
  let response;
  try {
    response = await fetch(base + path, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
    });
  } catch (error) {
    if (error.name === "AbortError") throw error;
    throw new Error(
      "We could not connect to the café. Please try again shortly.",
    );
  }
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    if (response.status === 401 && path !== "/login") saveSession(null);
    const messages = {
      401:
        path === "/login"
          ? "The email or password is incorrect."
          : "Your session has expired. Please log in again.",
      403: "You do not have access to this item.",
      409: "This item already exists. Please check your details.",
      422: "Please check the information you entered.",
      400: "We could not complete this request. Please refresh and check your selection.",
    };
    const detail =
      data && typeof data.detail === "string" && data.detail.length
        ? data.detail
        : null;
    const error = new Error(
      path === "/users" && response.status === 409
        ? "An account already uses this email. Please log in."
        : detail ||
            messages[response.status] ||
            "We could not load this information. Please try again.",
    );
    error.status = response.status;
    throw error;
  }
  return data;
}
export const post = (path, body) =>
  api(path, { method: "POST", body: JSON.stringify(body || {}) });
