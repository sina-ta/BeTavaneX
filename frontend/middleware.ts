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

  // Auth skeleton — enable when JWT/cookie auth is implemented:
  // const token =
  //   request.cookies.get("auth_token")?.value ??
  //   request.headers.get("authorization")?.replace("Bearer ", "");
  //
  // if (!token) {
  //   return NextResponse.redirect(
  //     new URL("/login", request.url)
  //   );
  // }

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
