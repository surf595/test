import { getServerSession } from "next-auth";
import { redirect } from "next/navigation";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export default async function ProfilePage() {
  const session = await getServerSession(authOptions);
  if (!session?.user?.email) {
    redirect("/auth/login");
  }

  const appointments = await prisma.appointment.findMany({
    where: { user: { email: session.user.email } },
    orderBy: { scheduledAt: "asc" }
  });

  return (
    <section className="mx-auto max-w-4xl py-12 container-padding">
      <h1 className="text-3xl font-bold text-brand-900">Личный кабинет</h1>
      {appointments.length === 0 ? (
        <p className="mt-4 text-slate-600">Пока нет запланированных сессий.</p>
      ) : (
        <ul className="mt-6 space-y-3">
          {appointments.map((appointment) => (
            <li className="rounded-lg bg-white p-4 shadow-sm" key={appointment.id}>
              <p className="font-medium">{new Date(appointment.scheduledAt).toLocaleString("ru-RU")}</p>
              <p className="text-sm text-slate-600">Статус: {appointment.status}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
