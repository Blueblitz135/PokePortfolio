/** Declare client-side routes inside the shared application shell. */
import { Navigate, Route, Routes } from "react-router-dom";

import { AppShell } from "./components/AppShell";
import { AssetDetailPage } from "./pages/AssetDetailPage";
import { CollectionPage } from "./pages/CollectionPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { SearchPage } from "./pages/SearchPage";
import { SealedProductsPage } from "./pages/SealedProductsPage";
import { SettingsPage } from "./pages/SettingsPage";

/** Render the portfolio page router and fallback route. */
export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<Navigate to="/collection" replace />} />
        <Route path="collection" element={<CollectionPage />} />
        <Route path="search" element={<SearchPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="sealed-products" element={<SealedProductsPage />} />
        <Route path="assets/:assetId" element={<AssetDetailPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
