/** Friendly fallback for unknown client-side routes. */
import { Link } from "react-router-dom";

/** Offer navigation back to the main collection after a route miss. */
export function NotFoundPage() {
  return (
    <div className="app-shell">
      <section className="panel not-found-panel">
        <p className="eyebrow">404</p>
        <h1>Page not found</h1>
        <p className="intro">
          The page you requested does not exist in PokePortfolio.
        </p>
        <Link className="primary-button button-link" to="/collection">
          Return to collection
        </Link>
      </section>
    </div>
  );
}
