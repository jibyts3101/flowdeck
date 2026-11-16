
"use client";

import { useEffect, useState, type FormEvent } from "react";

type Project = {
  id: number;
  name: string;
  key: string;
};

type Issue = {
  id: number;
  title: string;
  description: string | null;
  issue_type: "task" | "bug" | "story";
  status: "todo" | "in_progress" | "done";
  priority: "low" | "medium" | "high" | "critical";
  project_id: number;
  reporter_id: number;
  assignee_id: number | null;
  due_date: string | null;
  created_at: string;
  updated_at: string;
};

const issueTypes = ["task", "bug", "story"] as const;
const statuses = ["todo", "in_progress", "done"] as const;
const priorities = ["low", "medium", "high", "critical"] as const;

const emptyForm = {
  title: "",
  description: "",
  issue_type: "task",
  status: "todo",
  priority: "medium",
  project_id: "",
  assignee_id: "",
  due_date: "",
};

export default function IssuesPage() {
  const [issues, setIssues] = useState<Issue[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [form, setForm] = useState(emptyForm);
  const [editingIssue, setEditingIssue] = useState<Issue | null>(null);
  const [filterProject, setFilterProject] = useState("all");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function readError(response: Response) {
    try {
      const data = await response.json();
      return data.detail || "Something went wrong.";
    } catch {
      return "Something went wrong.";
    }
  }

  async function loadData() {
    setLoading(true);
    setError("");

    try {
      const [issuesResponse, projectsResponse] = await Promise.all([
        fetch("/api/issues", { cache: "no-store" }),
        fetch("/api/projects", { cache: "no-store" }),
      ]);

      if (!issuesResponse.ok) {
        throw new Error(await readError(issuesResponse));
      }

      if (!projectsResponse.ok) {
        throw new Error(await readError(projectsResponse));
      }

      const issuesData: Issue[] = await issuesResponse.json();
      const projectsData: Project[] = await projectsResponse.json();

      setIssues(issuesData);
      setProjects(projectsData);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unable to load issues."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  function updateForm(
    field: keyof typeof emptyForm,
    value: string
  ) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function startEditing(issue: Issue) {
    setEditingIssue(issue);

    setForm({
      title: issue.title,
      description: issue.description || "",
      issue_type: issue.issue_type,
      status: issue.status,
      priority: issue.priority,
      project_id: String(issue.project_id),
      assignee_id: issue.assignee_id
        ? String(issue.assignee_id)
        : "",
      due_date: issue.due_date || "",
    });

    setError("");
    setMessage("");
  }

  function cancelEditing() {
    setEditingIssue(null);
    setForm(emptyForm);
    setError("");
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setMessage("");

    if (!form.project_id) {
      setError("Please select a project.");
      return;
    }

    const assigneeId = form.assignee_id
      ? Number(form.assignee_id)
      : null;

    if (
      assigneeId !== null &&
      (!Number.isInteger(assigneeId) || assigneeId <= 0)
    ) {
      setError("Enter a valid assignee user ID.");
      return;
    }

    const payload = {
      title: form.title.trim(),
      description: form.description.trim() || null,
      issue_type: form.issue_type,
      status: form.status,
      priority: form.priority,
      assignee_id: assigneeId,
      due_date: form.due_date || null,
      ...(!editingIssue && {
        project_id: Number(form.project_id),
      }),
    };

    setSaving(true);

    try {
      const response = await fetch(
        editingIssue
          ? `/api/issues/${editingIssue.id}`
          : "/api/issues",
        {
          method: editingIssue ? "PATCH" : "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        throw new Error(await readError(response));
      }

      const savedIssue: Issue = await response.json();

      if (editingIssue) {
        setIssues((current) =>
          current.map((issue) =>
            issue.id === savedIssue.id ? savedIssue : issue
          )
        );
        setMessage("Issue updated successfully.");
      } else {
        setIssues((current) => [savedIssue, ...current]);
        setMessage("Issue created successfully.");
      }

      setEditingIssue(null);
      setForm(emptyForm);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unable to save issue."
      );
    } finally {
      setSaving(false);
    }
  }

  async function changeIssueField(
    issue: Issue,
    field: "status" | "priority",
    value: string
  ) {
    setError("");
    setMessage("");

    try {
      const response = await fetch(`/api/issues/${issue.id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ [field]: value }),
      });

      if (!response.ok) {
        throw new Error(await readError(response));
      }

      const updatedIssue: Issue = await response.json();

      setIssues((current) =>
        current.map((item) =>
          item.id === updatedIssue.id ? updatedIssue : item
        )
      );

      setMessage("Issue updated successfully.");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unable to update issue."
      );
    }
  }

  async function deleteIssue(issue: Issue) {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${issue.title}"?`
    );

    if (!confirmed) return;

    setError("");
    setMessage("");

    try {
      const response = await fetch(`/api/issues/${issue.id}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error(await readError(response));
      }

      setIssues((current) =>
        current.filter((item) => item.id !== issue.id)
      );

      if (editingIssue?.id === issue.id) {
        cancelEditing();
      }

      setMessage("Issue deleted successfully.");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unable to delete issue."
      );
    }
  }

  const filteredIssues =
    filterProject === "all"
      ? issues
      : issues.filter(
          (issue) => issue.project_id === Number(filterProject)
        );

  function projectName(projectId: number) {
    const project = projects.find((item) => item.id === projectId);
    return project ? `${project.key} — ${project.name}` : `Project #${projectId}`;
  }

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Issues</h1>
        <p className="mt-1 text-sm text-gray-600">
          Track and manage your tasks, bugs, and stories.
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {message && (
        <div className="rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-700">
          {message}
        </div>
      )}

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">
          {editingIssue ? "Edit Issue" : "Create New Issue"}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Issue title
              </label>
              <input
                value={form.title}
                onChange={(event) =>
                  updateForm("title", event.target.value)
                }
                maxLength={200}
                required
                placeholder="Enter issue title"
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />
            </div>

            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Description
              </label>
              <textarea
                value={form.description}
                onChange={(event) =>
                  updateForm("description", event.target.value)
                }
                rows={3}
                placeholder="Describe the issue"
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Project
              </label>
              <select
                value={form.project_id}
                onChange={(event) =>
                  updateForm("project_id", event.target.value)
                }
                disabled={Boolean(editingIssue)}
                required
                className="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 disabled:bg-gray-100"
              >
                <option value="">Select project</option>
                {projects.map((project) => (
                  <option key={project.id} value={project.id}>
                    {project.key} — {project.name}
                  </option>
                ))}
              </select>
              {editingIssue && (
                <p className="mt-1 text-xs text-gray-500">
                  The project cannot be changed while editing.
                </p>
              )}
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Issue type
              </label>
              <select
                value={form.issue_type}
                onChange={(event) =>
                  updateForm("issue_type", event.target.value)
                }
                className="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900"
              >
                {issueTypes.map((item) => (
                  <option key={item} value={item}>
                    {item.charAt(0).toUpperCase() + item.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Status
              </label>
              <select
                value={form.status}
                onChange={(event) =>
                  updateForm("status", event.target.value)
                }
                className="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900"
              >
                {statuses.map((item) => (
                  <option key={item} value={item}>
                    {item === "in_progress"
                      ? "In Progress"
                      : item.charAt(0).toUpperCase() + item.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Priority
              </label>
              <select
                value={form.priority}
                onChange={(event) =>
                  updateForm("priority", event.target.value)
                }
                className="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900"
              >
                {priorities.map((item) => (
                  <option key={item} value={item}>
                    {item.charAt(0).toUpperCase() + item.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Assignee user ID
              </label>
              <input
                type="number"
                min="1"
                value={form.assignee_id}
                onChange={(event) =>
                  updateForm("assignee_id", event.target.value)
                }
                placeholder="Optional user ID"
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Due date
              </label>
              <input
                type="date"
                value={form.due_date}
                onChange={(event) =>
                  updateForm("due_date", event.target.value)
                }
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900"
              />
            </div>
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              type="submit"
              disabled={saving}
              className="rounded-md bg-blue-600 px-5 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {saving
                ? "Saving..."
                : editingIssue
                  ? "Save Changes"
                  : "Create Issue"}
            </button>

            {editingIssue && (
              <button
                type="button"
                onClick={cancelEditing}
                className="rounded-md border border-gray-300 px-5 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
            )}
          </div>
        </form>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              All Issues
            </h2>
            <p className="mt-1 text-sm text-gray-500">
              {filteredIssues.length} issue(s) found
            </p>
          </div>

          <select
            value={filterProject}
            onChange={(event) => setFilterProject(event.target.value)}
            className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900"
          >
            <option value="all">All projects</option>
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.key} — {project.name}
              </option>
            ))}
          </select>
        </div>

        {loading ? (
          <p className="py-6 text-sm text-gray-500">Loading issues...</p>
        ) : filteredIssues.length === 0 ? (
          <p className="py-6 text-sm text-gray-500">
            No issues found. Create your first issue above.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[850px] text-left text-sm">
              <thead>
                <tr className="border-b border-gray-200 text-gray-500">
                  <th className="px-3 py-3 font-medium">Issue</th>
                  <th className="px-3 py-3 font-medium">Project</th>
                  <th className="px-3 py-3 font-medium">Type</th>
                  <th className="px-3 py-3 font-medium">Status</th>
                  <th className="px-3 py-3 font-medium">Priority</th>
                  <th className="px-3 py-3 font-medium">Assignee</th>
                  <th className="px-3 py-3 text-right font-medium">
                    Actions
                  </th>
                </tr>
              </thead>

              <tbody>
                {filteredIssues.map((issue) => (
                  <tr
                    key={issue.id}
                    className="border-b border-gray-100 last:border-0"
                  >
                    <td className="px-3 py-4">
                      <p className="font-medium text-gray-900">
                        {issue.title}
                      </p>
                      <p className="mt-1 text-xs text-gray-500">
                        FLOW-{issue.id}
                      </p>
                    </td>

                    <td className="px-3 py-4 text-gray-600">
                      {projectName(issue.project_id)}
                    </td>

                    <td className="px-3 py-4 capitalize text-gray-600">
                      {issue.issue_type}
                    </td>

                    <td className="px-3 py-4">
                      <select
                        value={issue.status}
                        onChange={(event) =>
                          changeIssueField(
                            issue,
                            "status",
                            event.target.value
                          )
                        }
                        className="rounded-md border border-gray-300 bg-white px-2 py-1.5 text-xs text-gray-800"
                      >
                        {statuses.map((item) => (
                          <option key={item} value={item}>
                            {item === "in_progress"
                              ? "In Progress"
                              : item.charAt(0).toUpperCase() + item.slice(1)}
                          </option>
                        ))}
                      </select>
                    </td>

                    <td className="px-3 py-4">
                      <select
                        value={issue.priority}
                        onChange={(event) =>
                          changeIssueField(
                            issue,
                            "priority",
                            event.target.value
                          )
                        }
                        className="rounded-md border border-gray-300 bg-white px-2 py-1.5 text-xs text-gray-800"
                      >
                        {priorities.map((item) => (
                          <option key={item} value={item}>
                            {item.charAt(0).toUpperCase() + item.slice(1)}
                          </option>
                        ))}
                      </select>
                    </td>

                    <td className="px-3 py-4 text-gray-600">
                      {issue.assignee_id ?? "Unassigned"}
                    </td>

                    <td className="px-3 py-4 text-right">
                      <div className="flex justify-end gap-3">
                        <button
                          type="button"
                          onClick={() => startEditing(issue)}
                          className="font-medium text-blue-600 hover:text-blue-800"
                        >
                          Edit
                        </button>

                        <button
                          type="button"
                          onClick={() => deleteIssue(issue)}
                          className="font-medium text-red-600 hover:text-red-800"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}
