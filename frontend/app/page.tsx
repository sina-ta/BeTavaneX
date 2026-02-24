import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-100">
      <div className="text-center space-y-6">
        <h1 className="text-3xl font-bold">
          Welcome to BeTavanX
        </h1>

        <Link
          href="/login"
          className="inline-block bg-black text-white px-6 py-2 rounded"
        >
          Login
        </Link>
      </div>
    </main>
  );
}