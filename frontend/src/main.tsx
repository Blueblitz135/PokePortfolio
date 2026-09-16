/** Bootstrap React, routing, and preference context into the document root. */
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import App from "./App";
import { PortfolioPreferencesProvider } from "./preferences/PortfolioPreferencesProvider";
import "./styles.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <PortfolioPreferencesProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </PortfolioPreferencesProvider>
  </StrictMode>,
);
