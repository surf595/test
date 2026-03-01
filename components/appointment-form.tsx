"use client";

import { useState } from "react";

export function AppointmentForm() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function onSubmit(formData: FormData) {
    setLoading(true);
    setError(null);
    setSuccess(null);

    const payload = {
      scheduledAt: new Date(String(formData.get("scheduledAt"))).toISOString(),
      notes: String(formData.get("notes") || "")
    };

    const response = await fetch("/api/appointments", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = (await response.json()) as { message?: string };
    if (!response.ok) {
      setError(data.message ?? "Не удалось создать запись");
    } else {
      setSuccess("Запись успешно создана. Мы отправили подтверждение на email.");
    }

    setLoading(false);
  }

  return (
    <form action={onSubmit} className="space-y-4 rounded-xl bg-white p-6 shadow-sm">
      <div>
        <label className="mb-1 block text-sm font-medium" htmlFor="scheduledAt">
          Выберите дату и время
        </label>
        <input className="w-full rounded-md border p-2" id="scheduledAt" name="scheduledAt" required type="datetime-local" />
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium" htmlFor="notes">
          Комментарий
        </label>
        <textarea className="w-full rounded-md border p-2" id="notes" name="notes" rows={4} />
      </div>
      <button className="rounded-md bg-brand-600 px-4 py-2 text-white disabled:opacity-50" disabled={loading} type="submit">
        {loading ? "Сохранение..." : "Записаться"}
      </button>
      {error && <p className="text-sm text-red-600">{error}</p>}
      {success && <p className="text-sm text-green-700">{success}</p>}
    </form>
  );
}
