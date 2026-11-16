import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

type RouteContext = {
  params: Promise<{
    issueId: string;
  }>;
};

async function forwardRequest(
  request: NextRequest,
  context: RouteContext,
  method: "GET" | "PATCH" | "DELETE"
) {
  const { issueId } = await context.params;

  const cookieStore = await cookies();
  const token = cookieStore.get("flowdeck_token")?.value;

  if (!token) {
    return NextResponse.json(
      { detail: "Authentication required." },
      { status: 401 }
    );
  }

  const body = method === "PATCH" ? await request.json() : undefined;

  const response = await fetch(
    `${process.env.API_URL}/issues/${issueId}`,
    {
      method,
      headers: {
        Authorization: `Bearer ${token}`,
        ...(body && { "Content-Type": "application/json" }),
      },
      ...(body && { body: JSON.stringify(body) }),
      cache: "no-store",
    }
  );

  if (response.status === 204) {
    return new NextResponse(null, { status: 204 });
  }

  const responseBody = await response.text();

  return new NextResponse(responseBody || null, {
    status: response.status,
    headers: {
      "Content-Type":
        response.headers.get("Content-Type") || "application/json",
    },
  });
}

export async function GET(
  request: NextRequest,
  context: RouteContext
) {
  return forwardRequest(request, context, "GET");
}

export async function PATCH(
  request: NextRequest,
  context: RouteContext
) {
  return forwardRequest(request, context, "PATCH");
}

export async function DELETE(
  request: NextRequest,
  context: RouteContext
) {
  return forwardRequest(request, context, "DELETE");
}