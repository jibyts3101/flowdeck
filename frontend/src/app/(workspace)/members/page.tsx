
"use client";

import { useEffect, useState } from "react";

type Project = {
  id: number;
  name: string;
  key: string;
};

type ProjectMember = {
  id: number;
  project_id: number;
  user_id: number;
  username: string;
  full_name: string | null;
  email: string;
  role: string;
};

type TeamMember = ProjectMember & {
  project_name: string;
  project_key: string;
};

export default function MembersPage() {
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadMembers() {
      try {
        setLoading(true);
        setError("");

        // First, retrieve all projects accessible to the logged-in user.
        const projectsResponse = await fetch("/api/projects", {
          cache: "no-store",
        });

        if (!projectsResponse.ok) {
          throw new Error("Unable to load projects.");
        }

        const projects: Project[] = await projectsResponse.json();

        // Retrieve the members of every accessible project.
        const memberResponses = await Promise.all(
          projects.map(async (project) => {
            const response = await fetch(
              `/api/projects/${project.id}/members`,
              { cache: "no-store" }
            );

            if (!response.ok) {
              throw new Error(
                `Unable to load members for ${project.name}.`
              );
            }

            const projectMembers: ProjectMember[] =
              await response.json();

            return projectMembers.map((member) => ({
              ...member,
              project_name: project.name,
              project_key: project.key,
            }));
          })
        );

        // Combine all project member lists into one directory.
        setMembers(memberResponses.flat());
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Something went wrong."
        );
      } finally {
        setLoading(false);
      }
    }

    loadMembers();
  }, []);

  function formatRole(role: string) {
    return role.charAt(0).toUpperCase() + role.slice(1);
  }

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-black">
          Members
        </h1>

        <p className="mt-1 text-gray-600">
          View team members and their roles across your projects.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <p className="text-sm text-gray-500">
            Total Memberships
          </p>
          <p className="mt-2 text-2xl font-bold text-black">
            {loading ? "..." : members.length}
          </p>
        </div>

        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <p className="text-sm text-gray-500">
            Unique Team Members
          </p>
          <p className="mt-2 text-2xl font-bold text-black">
            {loading
              ? "..."
              : new Set(members.map((member) => member.user_id)).size}
          </p>
        </div>
      </div>

      <div className="overflow-hidden rounded-xl border border-gray-200 bg-white">
        <div className="border-b border-gray-200 p-5">
          <h2 className="text-lg font-semibold text-black">
            Team Members
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Members and their assigned project roles.
          </p>
        </div>

        {error && (
          <div className="m-5 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {loading ? (
          <p className="p-6 text-sm text-gray-500">
            Loading team members...
          </p>
        ) : !error && members.length === 0 ? (
          <p className="p-6 text-sm text-gray-500">
            No team members found in your projects yet.
          </p>
        ) : (
          !error && (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-gray-50 text-gray-600">
                  <tr>
                    <th className="px-5 py-3 font-medium">Member</th>
                    <th className="px-5 py-3 font-medium">Email</th>
                    <th className="px-5 py-3 font-medium">Project</th>
                    <th className="px-5 py-3 font-medium">Role</th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-gray-100">
                  {members.map((member) => (
                    <tr
                      key={`${member.project_id}-${member.user_id}`}
                      className="hover:bg-gray-50"
                    >
                      <td className="px-5 py-4">
                        <p className="font-medium text-black">
                          {member.full_name || member.username}
                        </p>
                        <p className="text-xs text-gray-500">
                          @{member.username}
                        </p>
                      </td>

                      <td className="px-5 py-4 text-gray-600">
                        {member.email}
                      </td>

                      <td className="px-5 py-4">
                        <p className="font-medium text-black">
                          {member.project_name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {member.project_key}
                        </p>
                      </td>

                      <td className="px-5 py-4">
                        <span className="inline-flex rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
                          {formatRole(member.role)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        )}
      </div>
    </section>
  );
}
