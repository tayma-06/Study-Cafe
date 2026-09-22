import quiet from "../assets/illustrations/quiet-zone.png";
import standard from "../assets/illustrations/standard-zone.png";
import group from "../assets/illustrations/group-zone.png";
export const zoneImage = (name) =>
  /quiet/i.test(name) ? quiet : /group/i.test(name) ? group : standard;
export const money = (value) =>
  "৳" +
  Number(value || 0).toLocaleString("en-US", { maximumFractionDigits: 2 });
export const statusLabel = (value) =>
  ({
    canceled: "Cancelled",
    completed: "Paid",
    checked_in: "Checked In",
    checked_out: "Checked Out",
    pending: "Pending",
    confirmed: "Confirmed",
    failed: "Failed",
  })[value] ||
  value ||
  "Not recorded";
export function slotDates(slot) {
  return String(slot || "")
    .replace(/^[[(]|[)\]]$/g, "")
    .split(",")
    .map((s) => {
      let value = s.trim().replaceAll('"', "");
      if (!/([zZ]|[+-]\d{2}(?::?\d{2})?)$/.test(value)) value += "+06:00";
      return new Date(value);
    });
}
export function slotLabel(slot) {
  const [a, b] = slotDates(slot);
  if (!a || !b || isNaN(a) || isNaN(b)) return "Time unavailable";
  const options = { timeZone: "Asia/Dhaka" };
  return (
    a.toLocaleDateString("en-US", {
      ...options,
      month: "short",
      day: "numeric",
      year: "numeric",
    }) +
    " · " +
    a.toLocaleTimeString("en-US", {
      ...options,
      hour: "numeric",
      minute: "2-digit",
    }) +
    " – " +
    b.toLocaleTimeString("en-US", {
      ...options,
      hour: "numeric",
      minute: "2-digit",
    })
  );
}
export const today = () =>
  new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Dhaka",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date());
