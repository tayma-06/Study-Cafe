// Run against npm run dev with Playwright installed in the test environment.
// All API requests are intercepted; this test never contacts a real database.
import assert from "node:assert/strict";
import { chromium } from "playwright";
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const errors = [];
page.on("pageerror", (e) => errors.push(e.message));
const zones = [
  {
    zone_id: 1,
    name: "Quiet Zone",
    description: "A calm space for deep focus.",
    price_per_hour: 100,
    facilities: ["Power outlets", "Quiet space"],
  },
  {
    zone_id: 2,
    name: "Standard Zone",
    description: "A little room for everyday progress.",
    price_per_hour: 80,
    facilities: ["Wi-Fi"],
  },
  {
    zone_id: 3,
    name: "Group Zone",
    description: "Good ideas start together.",
    price_per_hour: 150,
    facilities: ["Shared desks"],
  },
];
let bookings = [],
  payments = {},
  createCount = 0,
  failPrice = false;
const calls = [];
await page.route("http://localhost:8000/**", async (route) => {
  const req = route.request(),
    url = new URL(req.url()),
    p = url.pathname;
  calls.push([req.method(), p]);
  let body = {},
    status = 200;
  const payload = req.postDataJSON();
  if (req.method() === "OPTIONS")
    return route.fulfill({
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Methods": "*",
      },
    });
  if (p === "/login")
    body = {
      user_id: 7,
      name: "Test Customer",
      email: "test@example.com",
      role: "customer",
      token: "test-token",
    };
  else if (p === "/users" && req.method() === "POST")
    body = {
      user_id: 7,
      name: payload.name,
      email: payload.email,
      role: "customer",
      created_at: "2026-09-22",
    };
  else if (p === "/zones") body = zones;
  else if (p === "/services")
    body = [
      {
        service_id: 1,
        name: "Coffee",
        description: "A warm cup for your next chapter.",
        price: 80,
      },
    ];
  else if (/^\/zones\/\d+\/seats$/.test(p))
    body = [
      { seat_id: 1, zone_id: 1, seat_number: "S01", status: "available" },
      { seat_id: 2, zone_id: 1, seat_number: "S02", status: "unavailable" },
    ];
  else if (p === "/availability")
    body = [
      {
        seat_id: 1,
        zone_id: 1,
        seat_number: "S01",
        zone_name: "Quiet Zone",
        price_per_hour: 100,
      },
    ];
  else if (p === "/bookings" && req.method() === "POST") {
    createCount++;
    assert.equal(payload.user_id, 7);
    assert.ok(payload.start_time.endsWith("+06:00"));
    body = {
      booking_id: "1001.1234",
      user_id: 7,
      seat_id: 1,
      status: "pending",
      created_at: "2026-09-22",
    };
    bookings = [
      {
        ...body,
        booking_status: "pending",
        zone_name: "Quiet Zone",
        seat_number: "S01",
        time_slot: "[2099-10-01 09:00:00+06:00, 2099-10-01 12:00:00+06:00)",
        payment_status: null,
        payment_amount: null,
      },
    ];
  } else if (p === "/bookings/me") body = bookings;
  else if (p.endsWith("/price")) {
    if (failPrice) {
      status = 500;
      body = { detail: "db failure" };
    } else
      body = {
        booking_id: "1001.1234",
        base_price: 300,
        service_cost: 80,
        total_price: 380,
      };
  } else if (p.startsWith("/payments/") && req.method() === "GET") {
    body = payments[p.split("/").pop()];
    if (!body) {
      status = 404;
      body = { detail: "Payment not found" };
    }
  } else if (p === "/payments" && req.method() === "POST") {
    assert.equal(payload.status, "pending");
    assert.equal(payload.method, "cash");
    assert.equal(payload.amount, 380);
    body = { ...payload, payment_id: 1 };
    payments[payload.booking_id] = body;
    bookings[0].payment_status = "pending";
    bookings[0].payment_amount = 380;
  } else if (p.endsWith("/check-in")) {
    bookings[0].booking_status = "checked_in";
    body = { message: "checked in" };
  } else if (p.endsWith("/check-out")) {
    bookings[0].booking_status = "checked_out";
    body = { message: "checked out" };
  } else if (p.endsWith("/cancel")) {
    bookings[0].booking_status = "canceled";
    body = { message: "canceled" };
  } else {
    status = 404;
    body = { detail: "unknown " + p };
  }
  return route.fulfill({
    status,
    contentType: "application/json",
    headers: { "Access-Control-Allow-Origin": "*" },
    body: JSON.stringify(body),
  });
});
await page.goto("http://127.0.0.1:5173/booking");
await page.waitForURL("**/login");
await page.getByRole("link", { name: "Create an account" }).click();
await page.getByLabel("Full name").fill("Test Customer");
await page.getByLabel("Email address").fill("test@example.com");
await page.getByLabel("Password", { exact: true }).fill("password123");
await page.getByLabel("Confirm password").fill("notmatching");
await page.getByRole("button", { name: "Create account", exact: true }).click();
await page.getByText("Your passwords do not match.").waitFor();
await page.getByLabel("Confirm password").fill("password123");
await page.getByRole("button", { name: "Create account", exact: true }).click();
await page.waitForURL("**/login");
await page.getByText("Your account is ready.", { exact: false }).waitFor();
await page.getByLabel("Email address").fill("test@example.com");
await page.getByLabel("Password", { exact: true }).fill("password123");
await page.getByRole("button", { name: "Log in", exact: true }).click();
await page.waitForURL("**/booking");
await page.getByLabel("Date", { exact: true }).fill("2099-10-01");
await page.getByRole("button", { name: "Quiet Zone" }).click();
await page.getByRole("button", { name: "Find available seats" }).click();
await page.getByRole("button", { name: "S01 Available" }).click();
assert.equal(
  await page.getByRole("button", { name: "S02 Unavailable" }).isDisabled(),
  true,
);
await page.getByRole("button", { name: "Choose add-ons" }).click();
await page.getByRole("button", { name: "Add Coffee", exact: true }).click();
await page.getByRole("button", { name: "Review booking" }).click();
await page.getByRole("button", { name: "Reserve my seat" }).click();
await page.getByText("See you at Study Café.").waitFor();
await page.getByRole("button", { name: "Save pay-at-café choice" }).click();
await page
  .getByText("Please pay at the café.", { exact: false })
  .last()
  .waitFor();
assert.equal(createCount, 1);
await page.getByRole("link", { name: "View my bookings" }).click();
await page.getByRole("button", { name: "View details" }).click();
await page.getByRole("button", { name: "Cancel booking", exact: true }).click();
await page.getByRole("button", { name: "Keep booking" }).waitFor();
await page.getByRole("button", { name: "Cancel booking", exact: true }).click();
await page.getByRole("button", { name: "Cancelled", exact: true }).click();
await page.getByRole("button", { name: "View details" }).waitFor();
for (const route of [
  "/login",
  "/register",
  "/zones",
  "/services",
  "/pricing",
  "/booking",
  "/bookings",
]) {
  await page.goto("http://127.0.0.1:5173" + route);
  await page.waitForTimeout(150);
  assert.equal(
    await page.locator("body").evaluate((e) => e.scrollWidth > innerWidth + 1),
    false,
    "desktop overflow " + route,
  );
}
await page.setViewportSize({ width: 390, height: 844 });
for (const route of [
  "/zones",
  "/services",
  "/pricing",
  "/booking",
  "/bookings",
]) {
  await page.goto("http://127.0.0.1:5173" + route);
  await page.waitForTimeout(150);
  assert.equal(
    await page.locator("body").evaluate((e) => e.scrollWidth > innerWidth + 1),
    false,
    "mobile overflow " + route,
  );
}
await page.goto("http://127.0.0.1:5173/zones");
await page.getByRole("button", { name: "Toggle navigation" }).click();
await page.getByRole("button", { name: "Log out" }).click();
await page.goto("http://127.0.0.1:5173/login");
await page.setViewportSize({ width: 1440, height: 1000 });
// Verify lifecycle actions and recovery after reservation succeeds but price loading fails.
await page.goto("http://127.0.0.1:5173/login");
await page.getByLabel("Email address").fill("test@example.com");
await page.getByLabel("Password", { exact: true }).fill("password123");
await page.getByRole("button", { name: "Log in", exact: true }).click();
await page.waitForURL("**/bookings");
bookings[0].booking_status = "confirmed";
await page.reload();
await page.getByRole("button", { name: "View details" }).click();
await page.getByRole("button", { name: "Check in", exact: true }).click();
await page.getByRole("button", { name: "View details" }).click();
await page.getByRole("button", { name: "Check out", exact: true }).click();
await page.getByRole("button", { name: "Past", exact: true }).click();
await page.getByRole("button", { name: "View details" }).waitFor();
failPrice = true;
await page.goto("http://127.0.0.1:5173/booking");
await page.getByLabel("Date", { exact: true }).fill("2099-10-01");
await page.getByRole("button", { name: "Quiet Zone" }).click();
await page.getByRole("button", { name: "Find available seats" }).click();
await page.getByRole("button", { name: "S01 Available" }).click();
await page.getByRole("button", { name: "Choose add-ons" }).click();
await page.getByRole("button", { name: "Review booking" }).click();
await page.getByRole("button", { name: "Reserve my seat" }).click();
await page
  .getByText("Your booking was created, but its total could not be loaded.", {
    exact: false,
  })
  .waitFor();
assert.equal(createCount, 2);
assert.equal(
  await page.getByRole("button", { name: "Reserve my seat" }).count(),
  0,
);
assert.equal(
  await page.getByRole("button", { name: "Save pay-at-café choice" }).count(),
  0,
);
assert.deepEqual(errors, []);
console.log(
  "PASS: protected routing, registration mismatch/success, login redirect, unavailable seat, add-ons, reservation, pending cash payment, cancel confirmation, desktop/mobile overflow, logout, check-in/out, price failure recovery, no browser exceptions.",
);
await browser.close();
