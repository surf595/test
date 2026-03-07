"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function handleSubmit(formData: FormData) {
    setLoading(true);
    setMessage(null);

    const response = await fetch("/api/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: formData.get("name"),
        email: formData.get("email"),
        password: formData.get("password")
      })
    });

    if (!response.ok) {
      const data = (await response.json()) as { message?: string };
      setMessage(data.message ?? "Не удалось зарегистрироваться");
      setLoading(false);
      return;
    }

    setMessage("Регистрация завершена. Теперь вы можете войти.");
    setLoading(false);
    setTimeout(() => router.push("/auth/login"), 700);
  }

  return (
    <section className="mx-auto max-w-md py-16 container-padding">
      <h1 className="mb-6 text-3xl font-bold text-brand-900">Регистрация</h1>
      <form action={handleSubmit} className="space-y-3 rounded-xl bg-white p-6 shadow-sm">
        <input className="w-full rounded-md border p-2" name="name" placeholder="Имя" required />
        <input className="w-full rounded-md border p-2" name="email" placeholder="Email" required type="email" />
        <input className="w-full rounded-md border p-2" minLength={8} name="password" placeholder="Пароль" required type="password" />
        <button className="w-full rounded-md bg-brand-600 py-2 text-white" disabled={loading} type="submit">
          {loading ? "Создание..." : "Создать аккаунт"}
        </button>
        {message && <p className="text-sm text-slate-700">{message}</p>}
      </form>
    </section>
  );
}
