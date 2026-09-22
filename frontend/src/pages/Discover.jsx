import { Link } from "react-router-dom";
import { ArrowRight, Coffee, Check } from "lucide-react";
import { Layout, Heading, Feedback, useLoad } from "../components/CustomerUI";
import { money, zoneImage } from "../utils/customer";
export default function Discover({ kind = "zones" }) {
  const services = kind === "services",
    pricing = kind === "pricing";
  const state = useLoad(services ? "/services" : "/zones");
  return (
    <Layout>
      <Heading
        eyebrow={
          services ? "A LITTLE SOMETHING EXTRA" : "FIND YOUR KIND OF FOCUS"
        }
        title={
          services
            ? "Good study days, served."
            : pricing
              ? "Simple rates. Space to focus."
              : "A space for every study style."
        }
      >
        {services
          ? "Coffee, snacks, and the little essentials that keep you going."
          : pricing
            ? "Choose the space that suits you. See your full estimate before reserving."
            : "Quiet concentration, everyday progress, or ideas shared around a table."}
      </Heading>
      <Feedback {...state}>
        <div className="sc-card-grid">
          {state.data?.map((item) => (
            <article
              className="sc-card sc-discover"
              key={item.zone_id || item.service_id}
            >
              {!services && !pricing && (
                <img
                  src={zoneImage(item.name)}
                  alt={item.name + " illustration"}
                />
              )}
              <div className="sc-card-body">
                {services && (
                  <div className="sc-icon-disc">
                    <Coffee />
                  </div>
                )}
                <h2>{item.name}</h2>
                <p>{item.description}</p>
                {item.facilities?.length > 0 && (
                  <ul className="sc-facilities">
                    {item.facilities.map((f) => (
                      <li key={f}>
                        <Check size={14} />
                        {f}
                      </li>
                    ))}
                  </ul>
                )}
                <p className="sc-price">
                  {money(services ? item.price : item.price_per_hour)}
                  <small>{services ? " / item" : " / hour"}</small>
                </p>
                <Link
                  className="sc-button sc-secondary"
                  to={services ? "/booking" : "/booking?zone=" + item.zone_id}
                >
                  {services ? "Add to a booking" : "Choose this zone"}
                  <ArrowRight size={16} />
                </Link>
              </div>
            </article>
          ))}
        </div>
        {state.data?.length === 0 && (
          <div className="sc-notice">
            {services
              ? "No café services are currently available."
              : "No study zones are currently available."}
          </div>
        )}
      </Feedback>
      <div className="sc-note">
        <Coffee size={23} />
        <div>
          <h3>
            {services
              ? "A little extra, only if you want it."
              : "Take your time. Make it yours."}
          </h3>
          <p>
            {services
              ? "Choose your add-ons while booking. Their cost is included in your booking total."
              : "All prices are in Bangladeshi Taka. Choose your date and time to browse seats and reserve your session."}
          </p>
        </div>
        <Link to="/booking">Book a seat →</Link>
      </div>
    </Layout>
  );
}
