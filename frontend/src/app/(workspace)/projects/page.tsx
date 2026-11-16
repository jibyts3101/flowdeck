import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import ProjectCreateForm from "./project-create-form";
import Link from "next/link";


type Project={
    id: number;
    name: string;
    key: string;
    description: string|null;
    owner_id: number;
    created_at: string;
    updated_at: string;
}

export default async function ProjectsPage() {
    const cookieStore=await cookies();

    const token=cookieStore.get("flowdeck_token")?.value;

    if(!token){
        redirect("/");
    }

    const response= await fetch(
        `${process.env.API_URL}/projects/`,
        {
            headers:{
                Authorization:`Bearer ${token}`
            },
            cache:"no-store",
        }
    );

    if(!response.ok){
        if (response.status==401||response.status==403){
            redirect("/");
        }

        throw new Error("Unable to fetch Projects");
    }

    const projects:Project[]=await response.json();
    
    return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
  <div>
    <h1 className="text-2xl font-bold text-black">
      Projects
    </h1>

    <p className="mt-1 text-gray-600">
      Manage and track all your projects.
    </p>
  </div>

  <ProjectCreateForm />
</div>

      {projects.length === 0 ? (
        <div className="rounded-xl border border-gray-200 bg-white p-8">
          <h2 className="text-lg font-semibold text-black">
            No projects found
          </h2>

          <p className="mt-2 text-sm text-gray-500">
            Create your first project to get started.
          </p>
        </div>
      ) : (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => (
           <Link
           key={project.id}
           href={`/projects/${project.id}`}
           className="block rounded-xl border border-gray-200 bg-white p-6 transition hover:border-gray-400 hover:shadow-md"
           >
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-black">
                  {project.name}
                </h2>

                <span className="rounded-md bg-gray-100 px-3 py-1 text-xs font-semibold text-gray-700">
                  {project.key}
                </span>
              </div>

              <p className="mt-3 text-sm text-gray-600">
                {project.description || "No description provided."}
              </p>

              <p className="mt-5 text-xs text-gray-400">
                Project ID: {project.id}
              </p>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}