import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

function ZoneCard({ image, name, description, price }) {
  return (
    <article className="zone-card">
      <div className="zone-card-image">
        <img src={image} alt={name} />
        <span>{price}</span>
      </div>
      <div className="zone-card-content">
        <h3>{name}</h3>
        <p>{description}</p>
        <div className="zone-card-bottom">
          <span className="zone-card-note">
            Reserve your spot
          </span>
          <Link
            to="/booking"
            className="zone-card-link"
          >
            Book
            <ArrowRight size={16} />
          </Link>
        </div>
      </div>
    </article>
  );
}

export default ZoneCard;