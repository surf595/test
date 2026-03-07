import Link from "next/link";

const links = [
  { href: "/services", label: "Услуги" },
  { href: "/about", label: "Обо мне" },
  { href: "/blog", label: "Блог" },
  { href: "/book", label: "Запись" }
];

export function Navigation() {
  return (
    <header className="border-b border-brand-100 bg-white/90 backdrop-blur">
      <nav className="mx-auto flex max-w-6xl items-center justify-between py-4 container-padding">
        <Link className="text-lg font-semibold text-brand-900" href="/">
          Анна Миронова
        </Link>
        <ul className="flex gap-4 text-sm font-medium text-slate-700">
          {links.map((link) => (
            <li key={link.href}>
              <Link className="transition hover:text-brand-700" href={link.href}>
                {link.label}
              </Link>
            </li>
          ))}
          <li>
            <Link className="rounded-md bg-brand-600 px-3 py-1.5 text-white hover:bg-brand-700" href="/auth/login">
              Войти
            </Link>
          </li>
        </ul>
      </nav>
    </header>
  );
}
