import { Routes, Route } from "react-router-dom";

import Dashboard from "../pages/Dashboard";
import Emails from "../pages/Emails";
import Analytics from "../pages/Analytics";
import EmailDetails from "../pages/EmailDetails";

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/emails" element={<Emails />} />
      <Route path="/emails/:id" element={<EmailDetails />} />
      <Route path="/analytics" element={<Analytics />} />
    </Routes>
  );
}

export default AppRoutes;