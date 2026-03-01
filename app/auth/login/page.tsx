"use client";

import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function LoginPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(formData: FormData) {
    setLoading(true);
    setError(null);

    const response = await signIn("credentials", {
      email: formData.get("email"),
      password: formData.get("password"),
      redirect: false
    });

    setLoading(false);

    if (response?.error) {
      setError("Неверный email или пароль");
      return;
    }

    router.push("/profile");
  }

  return (
    <section className="mx-auto max-w-md py-16 container-padding">
      <h1 className="mb-6 text-3xl font-bold text-brand-900">Вход</h1>
      <form action={handleSubmit} className="space-y-3 rounded-xl bg-white p-6 shadow-sm">
        <input className="w-full rounded-md border p-2" name="email" required type="email" />
        <input className="w-full rounded-md border p-2" name="password" required type="password" />
        <button className="w-full rounded-md bg-brand-600 py-2 text-white" disabled={loading} type="submit">
          {loading ? "Вход..." : "Войти"}
        </button>
        {error && <p className="text-sm text-red-600">{error}</p>}
      </form>
    </section>
  );
}
