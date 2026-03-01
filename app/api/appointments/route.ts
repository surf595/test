import { getServerSession } from "next-auth";
import { NextResponse } from "next/server";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { appointmentSchema } from "@/lib/validations";

export async function POST(request: Request) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.email) {
      return NextResponse.json({ message: "Необходимо войти в аккаунт" }, { status: 401 });
    }

    const body = await request.json();
    const parsed = appointmentSchema.safeParse(body);

    if (!parsed.success) {
      return NextResponse.json({ message: "Некорректные данные записи" }, { status: 400 });
    }

    const user = await prisma.user.findUnique({ where: { email: session.user.email } });
    if (!user) {
      return NextResponse.json({ message: "Пользователь не найден" }, { status: 404 });
    }

    const scheduledAt = new Date(parsed.data.scheduledAt);
    if (scheduledAt < new Date()) {
      return NextResponse.json({ message: "Нельзя выбрать прошедшее время" }, { status: 400 });
    }

    await prisma.appointment.create({
      data: {
        userId: user.id,
        scheduledAt,
        notes: parsed.data.notes
      }
    });

    return NextResponse.json({ message: "Appointment created" }, { status: 201 });
  } catch (error) {
    console.error("Appointment error", error);
    return NextResponse.json({ message: "Внутренняя ошибка сервера" }, { status: 500 });
  }
}
