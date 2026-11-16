
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navigationItems = [
  { name: "Dashboard", href: "/dashboard", icon: "⌂" },
  { name: "Projects", href: "/projects", icon: "▦" },
  { name: "Issues", href: "/issues", icon: "☷" },
  { name: "Members", href: "/members", icon: "♙" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex min-h-screen w-64 flex-col border-r border-gray-200 bg-white px-5 py-6">
      <div className="mb-10">
        <h1 className="text-2xl font-bold text-black">
          Flowdeck
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Project Management
        </p>
      </div>

      <nav className="space-y-2">
        {navigationItems.map((item) => {
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium transition ${
                isActive
                  ? "bg-gray-900 text-white"
                  : "text-gray-600 hover:bg-gray-100 hover:text-black"
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto border-t border-gray-200 pt-5">
        <p className="text-xs text-gray-400">
          Flowdeck Workspace
        </p>
      </div>
    </aside>
  );
}
