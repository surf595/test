import type { Metadata } from "next";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

export const baseMetadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "Психотерапевт Анна Миронова | Частная практика",
    template: "%s | Анна Миронова"
  },
  description:
    "Частная психотерапевтическая практика: индивидуальные консультации, поддержка в кризисах и долгосрочная терапия.",
  openGraph: {
    title: "Психотерапевт Анна Миронова",
    description:
      "Индивидуальная психотерапия для взрослых и молодых специалистов. Онлайн-запись и блог с практическими материалами.",
    type: "website",
    locale: "ru_RU",
    url: siteUrl
  },
  alternates: {
    canonical: "/"
  }
};
