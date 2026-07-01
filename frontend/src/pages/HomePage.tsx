import { useEffect, useState } from "react";

import { getHealth } from "../api/health";
import { ApiStatus } from "../components/ApiStatus";

type ApiState = "loading" | "online" | "offline";

export function HomePage() {
  const [apiState, setApiState] = useState<ApiState>("loading");

  useEffect(() => {
    getHealth()
      .then(() => setApiState("online"))
      .catch(() => setApiState("offline"));
  }, []);

  return (
    <main className="page-shell">
      <section className="welcome-card">
        <p className="eyebrow">Pokemon Portfolio</p>
        <h1>Track your collection as a portfolio.</h1>
        <p className="intro">
          The project is ready for asset and purchase tracking features in the
          next tickets.
        </p>
        <ApiStatus status={apiState} />
      </section>
    </main>
  );
}
