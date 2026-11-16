"use client";

import { useEffect, useState } from "react";

type ProjectMember = {
  id: number;
  project_id: number;
  user_id: number;
  role: string;
  username: string;
  full_name: string | null;
  email: string;
};

type ProjectMembersProps = {
  projectId: number;
};

const roles = ["admin", "developer", "viewer"];

export default function ProjectMembers({
  projectId,
}: ProjectMembersProps) {
  const [members, setMembers] = useState<ProjectMember[]>([]);
  const [userId, setUserId] = useState("");
  const [role, setRole] = useState("developer");
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function loadMembers() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `/api/projects/${projectId}/members`,
        { cache: "no-store" }
      );

      if (response.status === 403) {
        setError("Only the project owner or an admin can manage members.");
        return;
      }

      if (!response.ok) {
        throw new Error("Unable to load project members.");
      }

      const data: ProjectMember[] = await response.json();
      setMembers(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadMembers();
  }, [projectId]);

  async function addMember(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setMessage("");

    const parsedUserId = Number(userId);

    if (!Number.isInteger(parsedUserId) || parsedUserId <= 0) {
      setError("Enter a valid user ID.");
      return;
    }

    setAdding(true);

    try {
      const response = await fetch(
        `/api/projects/${projectId}/members`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_id: parsedUserId,
            role,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to add member.");
      }

      setMembers((current) => [...current, data]);
      setUserId("");
      setRole("developer");
      setMessage("Member added successfully.");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Something went wrong."
      );
    } finally {
      setAdding(false);
    }
  }

  async function updateRole(member: ProjectMember, newRole: string) {
    setError("");
    setMessage("");

    try {
      const response = await fetch(
        `/api/projects/${projectId}/members/${member.user_id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ role: newRole }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to update member role.");
      }

      setMembers((current) =>
        current.map((item) =>
          item.user_id === member.user_id ? data : item
        )
      );

      setMessage(`Role updated for ${member.username}.`);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Something went wrong."
      );
    }
  }

  async function removeMember(member: ProjectMember) {
    const confirmed = window.confirm(
      `Remove ${member.username} from this project?`
    );

    if (!confirmed) return;

    setError("");
    setMessage("");

    try {
      const response = await fetch(
        `/api/projects/${projectId}/members/${member.user_id}`,
        { method: "DELETE" }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Unable to remove member.");
      }

      setMembers((current) =>
        current.filter((item) => item.user_id !== member.user_id)
      );

      setMessage(`${member.username} was removed from the project.`);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Something went wrong."
      );
    }
  }

  return (
    <section className="rounded-xl border border-gray-200 bg-white p-6">
      <div className="mb-5">
        <h2 className="text-lg font-semibold text-gray-900">
          Project Members
        </h2>
        <p className="mt-1 text-sm text-gray-500">
          Add people to this project and manage their access roles.
        </p>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {message && (
        <div className="mb-4 rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-700">
          {message}
        </div>
      )}

      {loading ? (
        <p className="py-4 text-sm text-gray-500">
          Loading members...
        </p>
      ) : error ? (
        <p className="py-2 text-sm text-gray-500">
          Member management is unavailable for your account.
        </p>
      ) : (
        <>
          <form
            onSubmit={addMember}
            className="mb-6 grid gap-3 rounded-lg bg-gray-50 p-4 sm:grid-cols-[1fr_1fr_auto]"
          >
            <input
              type="number"
              min="1"
              value={userId}
              onChange={(event) => setUserId(event.target.value)}
              placeholder="Enter user ID"
              className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              required
            />

            <select
              value={role}
              onChange={(event) => setRole(event.target.value)}
              className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            >
              {roles.map((item) => (
                <option key={item} value={item}>
                  {item.charAt(0).toUpperCase() + item.slice(1)}
                </option>
              ))}
            </select>

            <button
              type="submit"
              disabled={adding}
              className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {adding ? "Adding..." : "Add Member"}
            </button>
          </form>

          {members.length === 0 ? (
            <p className="py-4 text-sm text-gray-500">
              No members have been added to this project yet.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-gray-200 text-gray-500">
                    <th className="px-3 py-3 font-medium">Member</th>
                    <th className="px-3 py-3 font-medium">Email</th>
                    <th className="px-3 py-3 font-medium">Role</th>
                    <th className="px-3 py-3 text-right font-medium">
                      Action
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {members.map((member) => (
                    <tr
                      key={member.id}
                      className="border-b border-gray-100 last:border-0"
                    >
                      <td className="px-3 py-3">
                        <p className="font-medium text-gray-900">
                          {member.full_name || member.username}
                        </p>
                        <p className="text-xs text-gray-500">
                          @{member.username}
                        </p>
                      </td>

                      <td className="px-3 py-3 text-gray-600">
                        {member.email}
                      </td>

                      <td className="px-3 py-3">
                        <select
                          value={member.role}
                          onChange={(event) =>
                            updateRole(member, event.target.value)
                          }
                          className="rounded-md border border-gray-300 bg-white px-2 py-1.5 text-sm text-gray-800"
                        >
                          {roles.map((item) => (
                            <option key={item} value={item}>
                              {item.charAt(0).toUpperCase() + item.slice(1)}
                            </option>
                          ))}
                        </select>
                      </td>

                      <td className="px-3 py-3 text-right">
                        <button
                          type="button"
                          onClick={() => removeMember(member)}
                          className="font-medium text-red-600 hover:text-red-800"
                        >
                          Remove
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </section>
  );
}