export function Footer() {
  return (
    <footer className="mt-16 border-t border-brand-100 bg-white">
      <div className="mx-auto max-w-6xl py-8 text-sm text-slate-600 container-padding">
        <p>© {new Date().getFullYear()} Анна Миронова. Все права защищены.</p>
      </div>
    </footer>
  );
}
