
import { cookies } from "next/headers";
import { NextResponse } from "next/server";

type RouteContext = {
  params: Promise<{
    projectId: string;
  }>;
};

export async function PATCH(
  request: Request,
  context: RouteContext
) {
  try {
    const { projectId } = await context.params;

    const cookieStore = await cookies();
    const token = cookieStore.get("flowdeck_token")?.value;

    if (!token) {
      return NextResponse.json(
        { detail: "Not authenticated" },
        { status: 401 }
      );
    }

    const projectData = await request.json();

    const response = await fetch(
      `${process.env.API_URL}/projects/${projectId}`,
      {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(projectData),
        cache: "no-store",
      }
    );

    const data = await response.json();

    return NextResponse.json(data, {
      status: response.status,
    });
  } catch {
    return NextResponse.json(
      { detail: "Unable to update project. Please try again." },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: Request,
  context: RouteContext
) {
  try {
    const { projectId } = await context.params;

    const cookieStore = await cookies();
    const token = cookieStore.get("flowdeck_token")?.value;

    if (!token) {
      return NextResponse.json(
        { detail: "Not authenticated" },
        { status: 401 }
      );
    }

    const response = await fetch(
      `${process.env.API_URL}/projects/${projectId}`,
      {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        cache: "no-store",
      }
    );

    if (response.status === 204) {
      return new NextResponse(null, { status: 204 });
    }

    const data = await response.json();

    return NextResponse.json(data, {
      status: response.status,
    });
  } catch {
    return NextResponse.json(
      { detail: "Unable to delete project. Please try again." },
      { status: 500 }
    );
  }
}
