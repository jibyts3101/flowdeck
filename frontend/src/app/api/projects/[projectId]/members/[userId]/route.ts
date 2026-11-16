
import { cookies } from "next/headers";
import { NextResponse } from "next/server";

type RouteContext = {
  params: Promise<{
    projectId: string;
    userId: string;
  }>;
};

async function getAuthenticatedRequest(
  context: RouteContext,
  method: "PUT" | "DELETE",
  body?: unknown
) {
  const { projectId, userId } = await context.params;

  const cookieStore = await cookies();
  const token = cookieStore.get("flowdeck_token")?.value;

  if (!token) {
    return NextResponse.json(
      { detail: "Not authenticated" },
      { status: 401 }
    );
  }

  const response = await fetch(
    `${process.env.API_URL}/projects/${projectId}/members/${userId}`,
    {
      method,
      headers: {
        Authorization: `Bearer ${token}`,
        ...(body !== undefined && {
          "Content-Type": "application/json",
        }),
      },
      ...(body !== undefined && {
        body: JSON.stringify(body),
      }),
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
}

export async function PUT(
  request: Request,
  context: RouteContext
) {
  try {
    const memberData = await request.json();

    return await getAuthenticatedRequest(
      context,
      "PUT",
      memberData
    );
  } catch {
    return NextResponse.json(
      { detail: "Unable to update project member." },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: Request,
  context: RouteContext
) {
  try {
    return await getAuthenticatedRequest(
      context,
      "DELETE"
    );
  } catch {
    return NextResponse.json(
      { detail: "Unable to remove project member." },
      { status: 500 }
    );
  }
}
