
"use client";

import { useRouter } from "next/navigation";

export default function LogoutButton() {
  const router = useRouter();

  async function handleLogout() {
    try {
      const response = await fetch("/api/auth/logout", {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error("Logout failed");
      }

      router.replace("/");
      router.refresh();
    } catch {
      alert("Unable to logout. Please try again.");
    }
  }

  return (
    <button
      onClick={handleLogout}
      className="mt-6 rounded-lg bg-red-600 px-6 py-3 font-semibold text-white hover:bg-red-700"
    >
      Logout
    </button>
  );
}
