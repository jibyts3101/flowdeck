
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import Sidebar from "../components/sidebar";
import Topbar from "../components/topbar";

type DashboardLayoutProps = {
  children: React.ReactNode;
};

export default async function DashboardLayout({
  children,
}: DashboardLayoutProps) {
  const cookieStore = await cookies();
  const token = cookieStore.get("flowdeck_token")?.value;

  if (!token) {
    redirect("/");
  }

  const response = await fetch(
    `${process.env.API_URL}/auth/me`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    }
  );

  if (!response.ok) {
    redirect("/");
  }

  const user = await response.json();

  return (
    <div className="flex min-h-screen bg-gray-100">
      <Sidebar />

      <div className="flex flex-1 flex-col">
        <Topbar
          username={user.full_name || user.username}
        />

        <main className="flex-1 p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
