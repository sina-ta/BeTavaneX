import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PUBLIC_PATHS = ["/login", "/auth"];

const PROTECTED_PREFIXES = ["/dashboard", "/task"];

function isPublicPath(pathname: string): boolean {
  return PUBLIC_PATHS.some((path) =>
    pathname.startsWith(path)
  );
}

function isProtectedPath(pathname: string): boolean {
  return PROTECTED_PREFIXES.some((prefix) =>
    pathname.startsWith(prefix)
  );
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (isPublicPath(pathname)) {
    return NextResponse.next();
  }

  if (!isProtectedPath(pathname)) {
    return NextResponse.next();
  }

  // Phase 1 auth: the access token is mirrored into the `auth_token` cookie by
  // the client on sign-in. Middleware cannot read localStorage, so the cookie
  // is the server-visible signal. Unauthenticated users are sent to /login.
  const token = request.cookies.get("auth_token")?.value;

  if (!token) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/task/:path*",
    "/login",
    "/auth/:path*",
  ],
};
