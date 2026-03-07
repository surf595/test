import { AppointmentForm } from "@/components/appointment-form";

export default function BookPage() {
  return (
    <div className="mx-auto max-w-3xl py-12 container-padding">
      <h1 className="mb-4 text-3xl font-bold text-brand-900">Онлайн-запись</h1>
      <p className="mb-6 text-slate-700">Выберите удобное время, и я подтвержу сессию после проверки расписания.</p>
      <AppointmentForm />
    </div>
  );
}
