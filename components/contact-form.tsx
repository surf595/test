"use client";

import { useState } from "react";

export function ContactForm() {
  const [state, setState] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  async function onSubmit(formData: FormData) {
    setState("loading");

    const response = await fetch("/api/contact", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: formData.get("name"),
        email: formData.get("email"),
        message: formData.get("message")
      })
    });

    if (!response.ok) {
      setState("error");
      setMessage("Не удалось отправить форму. Попробуйте позже.");
      return;
    }

    setState("success");
    setMessage("Сообщение отправлено. Я свяжусь с вами в течение 24 часов.");
  }

  return (
    <form action={onSubmit} className="space-y-3 rounded-xl bg-white p-6 shadow-sm">
      <input className="w-full rounded-md border p-2" name="name" placeholder="Ваше имя" required />
      <input className="w-full rounded-md border p-2" name="email" placeholder="Email" required type="email" />
      <textarea className="w-full rounded-md border p-2" name="message" placeholder="Чем могу помочь?" required rows={5} />
      <button className="rounded-md bg-brand-600 px-4 py-2 text-white" disabled={state === "loading"} type="submit">
        {state === "loading" ? "Отправка..." : "Отправить"}
      </button>
      {state === "success" && <p className="text-sm text-green-700">{message}</p>}
      {state === "error" && <p className="text-sm text-red-600">{message}</p>}
    </form>
  );
}
