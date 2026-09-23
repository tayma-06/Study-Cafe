// Run against npm run dev with Playwright installed in the test environment.
// API requests are intercepted so no real accounts or payments are changed.
import assert from "node:assert/strict";
import { chromium } from "playwright";
const browser = await chromium.launch({
  headless: true,
  executablePath: process.env.CHROME_PATH || undefined,
  args: ["--no-sandbox"],
});
const page = await browser.newPage({ viewport: { width: 1440, height: 1050 } });
page.setDefaultTimeout(10000);
const errors = [];
page.on("pageerror", (e) => errors.push(e.message));
const calls = [];
let role = "admin";
let paymentStatus = "pending";
const zones = [
  {
    zone_id: 1,
    name: "Quiet Zone",
    price_per_hour: 100,
    description: "Room to focus",
    facilities: ["Wi-Fi"],
  },
];
const customers = [
  {
    user_id: 7,
    name: "Test Customer",
    email: "customer@example.com",
    role: "customer",
  },
];
const booking = {
  booking_id: "20260924.0001",
  user_id: 7,
  customer_name: "Test Customer",
  seat_number: "Q1",
  zone_name: "Quiet Zone",
  time_slot: "[2099-10-01 10:00:00+06:00, 2099-10-01 12:00:00+06:00)",
  total: 200,
  booking_status: "pending",
};
await page.route("http://localhost:8000/**", async (route) => {
  const request = route.request(),
    url = new URL(request.url()),
    path = url.pathname;
  const payload = request.postDataJSON();
  calls.push({ path, payload });
  let body = {},
    status = 200;
  if (request.method() === "OPTIONS")
    return route.fulfill({
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Methods": "*",
      },
    });
  if (path === "/login")
    body = {
      user_id: 1,
      name: "Café Staff",
      email: "staff@studycafe.example",
      role,
      token: "test",
    };
  else if (path === "/staff/summary")
    body = {
      total_bookings: 1,
      total_seats: 12,
      today_bookings: 1,
      today_revenue: 200,
      pending_payments: paymentStatus === "pending" ? 1 : 0,
    };
  else if (path === "/staff/bookings" && request.method() === "POST") {
    status = 201;
    body = { ...booking, ...payload };
  } else if (path === "/staff/bookings") body = [booking];
  else if (path === "/staff/customers") body = customers;
  else if (path === "/zones") body = zones;
  else if (path === "/seats")
    body = [{ seat_id: 1, zone_id: 1, seat_number: "Q1", status: "available" }];
  else if (path === "/services")
    body = [{ service_id: 1, name: "Coffee", price: 50 }];
  else if (path === "/availability")
    body = [
      {
        seat_id: 1,
        zone_name: "Quiet Zone",
        seat_number: "Q1",
        price_per_hour: 100,
      },
    ];
  else if (path === "/payment-requests")
    body = [
      {
        transaction_id: "DEMO-TEST123",
        booking_id: booking.booking_id,
        customer_name: "Test Customer",
        amount: 200,
        phone: "01711111111",
        status: paymentStatus,
      },
    ];
  else if (path.endsWith("/review")) {
    paymentStatus = payload.decision;
    body = { status: paymentStatus };
  } else if (path === "/admin/receptionists") body = payload;
  else if (path.endsWith("/role")) body = payload;
  else if (path === "/admin/zones") body = payload;
  else {
    status = 404;
    body = { detail: "Unexpected endpoint " + path };
  }
  return route.fulfill({
    status,
    contentType: "application/json",
    headers: { "Access-Control-Allow-Origin": "*" },
    body: JSON.stringify(body),
  });
});
async function login() {
  await page.goto("http://127.0.0.1:5173/login");
  await page.getByLabel("Email address").fill("staff@studycafe.example");
  await page.getByLabel("Password", { exact: true }).fill("password123");
  await page.getByRole("button", { name: "Log in", exact: true }).click();
}
await login();
await page.waitForURL("**/admin");
await page.getByText("Keep the café running", { exact: false }).waitFor();
await page.screenshot({
  path: process.env.STAFF_SCREENSHOT || "/tmp/study-admin.png",
  fullPage: true,
});
await page
  .getByRole("button", { name: "Customers & staff", exact: true })
  .click();
await page
  .getByRole("button", { name: "Create receptionist", exact: true })
  .click();
await page.getByLabel("Full name").fill("New Receptionist");
await page.getByLabel("Work email").fill("new@studycafe.example");
await page.getByLabel("Password", { exact: true }).fill("password123");
await page.getByRole("button", { name: "Save access" }).click();
await page.getByRole("dialog").waitFor({ state: "hidden" });
assert.ok(
  calls.some(
    (c) =>
      c.path === "/admin/receptionists" &&
      c.payload.email === "new@studycafe.example",
  ),
);
await page
  .getByRole("button", { name: "Grant receptionist", exact: true })
  .click();
await page.getByLabel("Work email").fill("customer@studycafe.example");
await page.getByRole("button", { name: "Save access" }).click();
await page.getByRole("dialog").waitFor({ state: "hidden" });
assert.ok(
  calls.some(
    (c) =>
      c.path === "/admin/users/7/role" && c.payload.role === "receptionist",
  ),
);
await page
  .getByRole("button", { name: "Payment approvals", exact: false })
  .click();
await page.getByRole("button", { name: "Approve", exact: true }).click();
await page.getByLabel("Review note").fill("Checked demo transaction");
await page.getByRole("button", { name: "Approve & confirm booking" }).click();
await page.getByRole("dialog").waitFor({ state: "hidden" });
assert.equal(paymentStatus, "approved");
await page
  .getByRole("button", { name: "Zones & pricing", exact: true })
  .click();
await page.getByRole("button", { name: "Edit", exact: true }).click();
await page.getByLabel("Hourly rate (BDT)").fill("120");
await page.getByRole("button", { name: "Save changes" }).click();
await page.getByRole("dialog").waitFor({ state: "hidden" });
assert.ok(
  calls.some(
    (c) => c.path === "/admin/zones" && c.payload.price_per_hour === "120",
  ),
);
await page.getByRole("button", { name: "Log out", exact: true }).click();
role = "receptionist";
await login();
await page.waitForURL("**/reception");
assert.equal(
  await page
    .getByRole("button", { name: "Customers & staff", exact: true })
    .count(),
  0,
);
await page
  .getByRole("button", { name: "Book a visit", exact: true })
  .first()
  .click();
await page.getByRole("button", { name: "Guest", exact: true }).click();
await page.getByLabel("Customer name").fill("Guest Visitor");
await page.getByLabel("Guest phone").fill("01711111111");
await page.getByLabel("Date", { exact: true }).fill("2099-10-01");
await page.getByRole("button", { name: "Find available seats" }).click();
await page.getByLabel("Available seat").selectOption("1");
await page.getByRole("button", { name: "Create reservation" }).click();
await page.getByRole("heading", { name: "Reservation created" }).waitFor();
assert.ok(
  calls.some(
    (c) =>
      c.path === "/staff/bookings" &&
      c.payload?.guest_name === "Guest Visitor" &&
      c.payload.user_id === undefined,
  ),
);
await page.getByRole("button", { name: "Book another visit" }).click();
await page
  .getByRole("button", { name: "Register customer", exact: true })
  .click();
await page.getByLabel("Customer name").fill("New Visitor");
await page.getByLabel("Customer email").fill("new@example.com");
await page.getByLabel("Password chosen by customer").fill("password123");
await page.getByLabel("The customer agrees to create an account.").check();
await page.getByRole("button", { name: "Find available seats" }).click();
await page.getByLabel("Available seat").selectOption("1");
await page.getByRole("button", { name: "Create reservation" }).click();
await page.getByRole("heading", { name: "Reservation created" }).waitFor();
assert.ok(
  calls.some(
    (c) =>
      c.path === "/staff/bookings" &&
      c.payload?.customer?.email === "new@example.com" &&
      c.payload.consent === true,
  ),
);
await page.setViewportSize({ width: 390, height: 844 });
for (const tab of [
  "Overview",
  "Bookings",
  "Payment approvals",
  "Customers",
  "Book a visit",
]) {
  await page
    .getByRole("navigation", { name: "Staff navigation" })
    .getByRole("button", { name: tab, exact: false })
    .click();
  assert.equal(
    await page.locator("body").evaluate((e) => e.scrollWidth > innerWidth + 1),
    false,
    "mobile overflow " + tab,
  );
}
await page.goto("http://127.0.0.1:5173/admin");
await page.waitForURL("http://127.0.0.1:5173/");
assert.deepEqual(errors, []);
console.log(
  "PASS: admin/receptionist routing, create/grant receptionist, approve demo payment, pricing edit, guest booking, consent registration, mobile layout, restricted admin page.",
);
await browser.close();
