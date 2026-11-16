
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

async function forwardRequest(
  request: NextRequest,
  method: "GET" | "POST"
) {
  const cookieStore = await cookies();
  const token = cookieStore.get("flowdeck_token")?.value;

  if (!token) {
    return NextResponse.json(
      { detail: "Authentication required." },
      { status: 401 }
    );
  }

  const body = method === "POST" ? await request.json() : undefined;

  const response = await fetch(`${process.env.API_URL}/issues/`, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      ...(body && { "Content-Type": "application/json" }),
    },
    ...(body && { body: JSON.stringify(body) }),
    cache: "no-store",
  });

  const responseBody = await response.text();

  return new NextResponse(responseBody || null, {
    status: response.status,
    headers: {
      "Content-Type":
        response.headers.get("Content-Type") || "application/json",
    },
  });
}

export async function GET(request: NextRequest) {
  return forwardRequest(request, "GET");
}

export async function POST(request: NextRequest) {
  return forwardRequest(request, "POST");
}
