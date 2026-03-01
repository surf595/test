import Link from "next/link";
import { ContactForm } from "@/components/contact-form";

export default function HomePage() {
  return (
    <div className="mx-auto grid max-w-6xl gap-12 py-12 container-padding lg:grid-cols-2">
      <section>
        <h1 className="text-4xl font-bold text-brand-900">Психотерапия с заботой о вашем темпе и безопасности</h1>
        <p className="mt-4 text-lg text-slate-700">
          Работаю со взрослыми и молодыми специалистами: тревога, выгорание, отношения, кризисы и поиск опоры.
        </p>
        <div className="mt-6 flex gap-3">
          <Link className="rounded-md bg-brand-600 px-4 py-2 text-white" href="/book">
            Записаться онлайн
          </Link>
          <Link className="rounded-md border border-brand-600 px-4 py-2 text-brand-700" href="/services">
            Посмотреть услуги
          </Link>
        </div>
      </section>
      <section aria-label="Контактная форма">
        <h2 className="mb-4 text-2xl font-semibold">Задать вопрос</h2>
        <ContactForm />
      </section>
    </div>
  );
}
