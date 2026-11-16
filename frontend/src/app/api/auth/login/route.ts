
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  try {
    const credentials = await request.json();

    const backendResponse = await fetch(
      `${process.env.API_URL}/auth/login`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(credentials),
        cache: "no-store",
      }
    );

    const data = await backendResponse.json();

    if (!backendResponse.ok) {
      return NextResponse.json(
        { detail: data.detail || "Login failed" },
        { status: backendResponse.status }
      );
    }

    const response = NextResponse.json({
      message: "Login successful",
    });

    response.cookies.set("flowdeck_token", data.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
    });

    return response;
  } catch {
    return NextResponse.json(
      { detail: "Unable to connect to the authentication service" },
      { status: 503 }
    );
  }
}
