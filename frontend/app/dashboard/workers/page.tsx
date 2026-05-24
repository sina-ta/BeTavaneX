import { redirect } from "next/navigation";

export default function WorkersLegacyRedirect() {
  redirect("/dashboard/workforce");
}
