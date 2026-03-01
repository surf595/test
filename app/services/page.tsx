const services = [
  { title: "Индивидуальная терапия", price: "8 000 ₽ / 50 мин", desc: "Долгосрочная работа с тревогой, самооценкой и отношениями." },
  { title: "Кризисные консультации", price: "9 500 ₽ / 60 мин", desc: "Поддержка в острых жизненных ситуациях и принятии решений." },
  { title: "Пакет 4 сессии", price: "30 000 ₽", desc: "Структурированный старт для системной терапевтической работы." }
];

export default function ServicesPage() {
  return (
    <div className="mx-auto max-w-5xl py-12 container-padding">
      <h1 className="text-3xl font-bold text-brand-900">Услуги</h1>
      <div className="mt-8 grid gap-4 md:grid-cols-3">
        {services.map((service) => (
          <article className="rounded-xl bg-white p-5 shadow-sm" key={service.title}>
            <h2 className="text-xl font-semibold">{service.title}</h2>
            <p className="mt-2 text-brand-700">{service.price}</p>
            <p className="mt-3 text-sm text-slate-600">{service.desc}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
