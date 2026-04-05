import { NavLink, Outlet } from "react-router-dom";
import {
  LayoutDashboard,
  Store,
  Search,
  FileText,
  Wrench,
  Settings,
} from "lucide-react";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/stores", icon: Store, label: "Stores" },
  { to: "/keywords", icon: Search, label: "Keywords" },
  { to: "/on-page", icon: FileText, label: "On-Page SEO" },
  { to: "/audits", icon: Wrench, label: "Technical SEO" },
  { to: "/settings", icon: Settings, label: "Settings" },
];

export default function Layout() {
  return (
    <div className="flex h-screen bg-gray-950 text-gray-100">
      {/* Sidebar */}
      <nav className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col">
        <div className="p-6 border-b border-gray-800">
          <h1 className="text-xl font-bold text-white">SEO Bot</h1>
          <p className="text-sm text-gray-400 mt-1">Shopify SEO Manager</p>
        </div>
        <div className="flex-1 py-4">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 px-6 py-3 text-sm transition-colors ${
                  isActive
                    ? "bg-blue-600/20 text-blue-400 border-r-2 border-blue-400"
                    : "text-gray-400 hover:text-white hover:bg-gray-800"
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </div>
      </nav>

      {/* Main content */}
      <main className="flex-1 overflow-auto p-8">
        <Outlet />
      </main>
    </div>
  );
}
