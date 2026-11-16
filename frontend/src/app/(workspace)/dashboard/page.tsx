
"use client";

import { useEffect, useState } from "react";

type Project = {
  id: number;
  name: string;
  key: string;
  owner_id?: number;
};

type Issue = {
  id: number;
  title: string;
  status: string;
  priority: string;
  issue_type: string;
  project_id: number;
  created_at: string;
};

type ProjectMember = {
  user_id: number;
};

export default function DashboardPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [issues, setIssues] = useState<Issue[]>([]);
  const [teamMembers, setTeamMembers] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        setError("");

        const [projectsResponse, issuesResponse] = await Promise.all([
          fetch("/api/projects", { cache: "no-store" }),
          fetch("/api/issues", { cache: "no-store" }),
        ]);

        if (!projectsResponse.ok || !issuesResponse.ok) {
          throw new Error("Unable to load dashboard data.");
        }

        const projectsData: Project[] = await projectsResponse.json();
        const issuesData: Issue[] = await issuesResponse.json();

        setProjects(projectsData);
        setIssues(issuesData);

        // Collect unique team members across all accessible projects.
        const memberResponses = await Promise.all(
          projectsData.map((project) =>
            fetch(`/api/projects/${project.id}/members`, {
              cache: "no-store",
            })
          )
        );

        const memberIds = new Set<number>();

        projectsData.forEach((project) => {
          if (project.owner_id) {
            memberIds.add(project.owner_id);
          }
        });

        for (const response of memberResponses) {
          if (!response.ok) continue;

          const members: ProjectMember[] = await response.json();

          members.forEach((member) => {
            memberIds.add(member.user_id);
          });
        }

        setTeamMembers(memberIds.size);
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

    loadDashboard();
  }, []);

  const todoCount = issues.filter(
    (issue) => issue.status === "todo"
  ).length;

  const inProgressCount = issues.filter(
    (issue) => issue.status === "in_progress"
  ).length;

  const completedCount = issues.filter(
    (issue) => issue.status === "done"
  ).length;

  const highPriorityCount = issues.filter(
    (issue) =>
      issue.priority === "high" ||
      issue.priority === "critical"
  ).length;

  const criticalCount = issues.filter(
    (issue) => issue.priority === "critical"
  ).length;

  const recentIssues = [...issues]
    .sort(
      (a, b) =>
        new Date(b.created_at).getTime() -
        new Date(a.created_at).getTime()
    )
    .slice(0, 5);

  function getProjectName(projectId: number) {
    return (
      projects.find((project) => project.id === projectId)?.name ||
      `Project #${projectId}`
    );
  }

  const summaryCards = [
    { label: "Projects", value: projects.length },
    { label: "Issues", value: issues.length },
    { label: "Team Members", value: teamMembers },
  ];

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-black">
          Dashboard
        </h1>
        <p className="mt-1 text-gray-600">
          Welcome to your Flowdeck workspace.
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {summaryCards.map((card) => (
          <div
            key={card.label}
            className="rounded-xl border border-gray-200 bg-white p-6"
          >
            <p className="text-sm text-gray-500">{card.label}</p>
            <p className="mt-2 text-2xl font-bold text-black">
              {loading ? "..." : card.value}
            </p>
          </div>
        ))}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "To Do", value: todoCount },
          { label: "In Progress", value: inProgressCount },
          { label: "Completed", value: completedCount },
          { label: "High / Critical", value: highPriorityCount },
        ].map((item) => (
          <div
            key={item.label}
            className="rounded-xl border border-gray-200 bg-white p-5"
          >
            <p className="text-sm text-gray-500">{item.label}</p>
            <p className="mt-2 text-2xl font-bold text-black">
              {loading ? "..." : item.value}
            </p>
          </div>
        ))}
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-black">
            Priority Overview
          </h2>
        </div>

        <div className="flex flex-wrap gap-6">
          <div>
            <p className="text-sm text-gray-500">Critical Issues</p>
            <p className="mt-1 text-xl font-bold text-red-600">
              {loading ? "..." : criticalCount}
            </p>
          </div>

          <div>
            <p className="text-sm text-gray-500">
              High and Critical Issues
            </p>
            <p className="mt-1 text-xl font-bold text-orange-600">
              {loading ? "..." : highPriorityCount}
            </p>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <h2 className="mb-4 text-lg font-semibold text-black">
          Recent Issues
        </h2>

        {loading ? (
          <p className="text-sm text-gray-500">
            Loading recent issues...
          </p>
        ) : recentIssues.length === 0 ? (
          <p className="text-sm text-gray-500">
            No issues found. Create your first issue to see it here.
          </p>
        ) : (
          <div className="space-y-3">
            {recentIssues.map((issue) => (
              <div
                key={issue.id}
                className="flex flex-col justify-between gap-2 border-b border-gray-100 pb-3 sm:flex-row sm:items-center"
              >
                <div>
                  <p className="font-medium text-black">
                    {issue.title}
                  </p>
                  <p className="text-sm text-gray-500">
                    {getProjectName(issue.project_id)} ·{" "}
                    {issue.issue_type}
                  </p>
                </div>

                <div className="flex gap-3 text-sm">
                  <span className="text-gray-600">
                    {issue.status.replace("_", " ")}
                  </span>
                  <span className="font-medium capitalize text-gray-800">
                    {issue.priority}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
