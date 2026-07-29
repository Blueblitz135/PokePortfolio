import { Link, useParams } from "react-router-dom";

export function AssetDetailPlaceholderPage() {
  const { assetId } = useParams();

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Asset details</p>
          <h1>Asset {assetId}</h1>
          <p className="intro">
            The complete asset detail and purchase-lot editing page belongs to
            ticket 010.
          </p>
        </div>
      </header>

      <section className="panel placeholder-panel">
        <h2>Detail page not available yet</h2>
        <p>Your collection data has not been changed.</p>
        <Link className="secondary-button button-link" to="/collection">
          Return to collection
        </Link>
      </section>
    </div>
  );
}
