import { useEffect } from "react";

import { CollectionPage } from "./pages/CollectionPage";
import { SealedProductsPage } from "./pages/SealedProductsPage";

export default function App() {
  const path = window.location.pathname;

  useEffect(() => {
    if (path === "/") {
      window.history.replaceState(null, "", "/collection");
    }
  }, [path]);

  if (path === "/sealed-products") {
    return <SealedProductsPage />;
  }

  return <CollectionPage />;
}
