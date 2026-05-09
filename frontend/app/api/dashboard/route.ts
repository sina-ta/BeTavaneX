import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET() {
  const filePath = path.join(process.cwd(), "app/data/dashboard.json");
  const jsonData = fs.readFileSync(filePath, "utf-8");

  return NextResponse.json(JSON.parse(jsonData));
}