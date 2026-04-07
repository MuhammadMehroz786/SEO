import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Stores from "./pages/Stores";
import StoreDetail from "./pages/StoreDetail";
import Keywords from "./pages/Keywords";
import Backlinks from "./pages/Backlinks";
import OnPageSEO from "./pages/OnPageSEO";
import TechnicalAudit from "./pages/TechnicalAudit";
import Settings from "./pages/SettingsPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/stores" element={<Stores />} />
          <Route path="/stores/:id" element={<StoreDetail />} />
          <Route path="/keywords" element={<Keywords />} />
          <Route path="/backlinks" element={<Backlinks />} />
          <Route path="/on-page" element={<OnPageSEO />} />
          <Route path="/audits" element={<TechnicalAudit />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
