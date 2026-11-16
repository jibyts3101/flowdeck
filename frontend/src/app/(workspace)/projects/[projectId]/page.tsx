import { cookies } from "next/headers";
import { redirect, notFound } from "next/navigation";
import Link from "next/link";
import ProjectEditForm from "./project-edit-form";
import ProjectMembers from "./project-members";

type Project = {
  id: number;
  name: string;
  key: string;
  description: string | null;
  owner_id: number;
  created_at: string;
  updated_at: string;
};

type CurrentUser = {
  id: number;
  username: string;
  full_name: string | null;
  email: string;
};

type ProjectDetailsPageProps = {
  params: Promise<{
    projectId: string;
  }>;
};

export default async function ProjectDetailsPage({
  params,
}: ProjectDetailsPageProps) {
  const { projectId } = await params;

  const cookieStore = await cookies();
  const token = cookieStore.get("flowdeck_token")?.value;

  if (!token) {
    redirect("/");
  }

  const response = await fetch(
    `${process.env.API_URL}/projects/${projectId}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    }
  );

  if (response.status === 404) {
    notFound();
  }

  if (response.status === 401) {
    redirect("/");
  }

  if (response.status === 403) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-6">
        <h1 className="text-lg font-semibold text-red-700">
          Access denied
        </h1>
        <p className="mt-2 text-sm text-red-600">
          You do not have permission to view this project.
        </p>
        <Link
          href="/projects"
          className="mt-4 inline-block text-sm font-medium text-blue-600 hover:underline"
        >
          Back to Projects
        </Link>
      </div>
    );
  }

  if (!response.ok) {
    throw new Error("Unable to fetch project details.");
  }

  const project: Project = await response.json();
  const userResponse = await fetch(`${process.env.API_URL}/auth/me`, {
  headers: {
    Authorization: `Bearer ${token}`,
  },
  cache: "no-store",
});

if (!userResponse.ok) {
  redirect("/");
}

const currentUser: CurrentUser = await userResponse.json();

const isOwner = project.owner_id === currentUser.id;

  return (
    <section className="space-y-6">
      <Link
        href="/projects"
        className="text-sm font-medium text-gray-600 hover:text-gray-900"
      >
        ← Back to Projects
      </Link>

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-500">
              Project {project.key}
            </p>

            <h1 className="mt-2 text-2xl font-bold text-gray-900">
              {project.name}
            </h1>
          </div>

          <span className="rounded-md bg-gray-100 px-3 py-1 text-sm font-semibold text-gray-700">
            {project.key}
          </span>
          {isOwner && <ProjectEditForm project={project} />}
        </div>

        <div className="mt-6 border-t border-gray-100 pt-5">
          <h2 className="text-sm font-semibold text-gray-900">
            Description
          </h2>

          <p className="mt-2 text-sm text-gray-600">
            {project.description || "No description provided."}
          </p>
        </div>

        <div className="mt-6 grid gap-4 border-t border-gray-100 pt-5 sm:grid-cols-2">
          <div>
            <p className="text-xs font-medium text-gray-500">
              Project ID
            </p>
            <p className="mt-1 text-sm font-semibold text-gray-900">
              {project.id}
            </p>
          </div>

          <div>
            <p className="text-xs font-medium text-gray-500">
              Owner ID
            </p>
            <p className="mt-1 text-sm font-semibold text-gray-900">
              {project.owner_id}
            </p>
          </div>
        </div>
      </div>
      <ProjectMembers projectId={project.id} />
    </section>
  );
}