import { getServerSession } from "next-auth";
import { NextResponse } from "next/server";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { contactSchema } from "@/lib/validations";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const parsed = contactSchema.safeParse(body);

    if (!parsed.success) {
      return NextResponse.json({ message: "Некорректные данные формы" }, { status: 400 });
    }

    const session = await getServerSession(authOptions);

    await prisma.contactMessage.create({
      data: {
        userId: session?.user?.id,
        name: parsed.data.name,
        email: parsed.data.email,
        message: parsed.data.message
      }
    });

    return NextResponse.json({ message: "Message sent" }, { status: 201 });
  } catch (error) {
    console.error("Contact error", error);
    return NextResponse.json({ message: "Внутренняя ошибка сервера" }, { status: 500 });
  }
}
