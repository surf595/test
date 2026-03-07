# Therapy Practice Web App (Next.js 14)

Production-ready site for a private psychotherapy practice with online booking, authentication, contact intake, blog, and SEO.

## Tech stack

- Next.js 14 + React + TypeScript
- Tailwind CSS
- Prisma + PostgreSQL
- NextAuth (Credentials)

## Project structure

- `app/` — pages, API routes, SEO files
- `components/` — UI + form components
- `lib/` — auth, prisma client, validation, seo metadata
- `prisma/` — schema and seed script

## Local run

1. Install dependencies:
   ```bash
   npm install
   ```
2. Configure env:
   ```bash
   cp .env.example .env
   ```
3. Generate client and run migrations:
   ```bash
   npm run db:generate
   npm run db:migrate
   npm run db:seed
   ```
4. Start app:
   ```bash
   npm run dev
   ```

## Deployment (Vercel + managed PostgreSQL)

1. Create PostgreSQL DB (Neon/Supabase/RDS).
2. Set `DATABASE_URL`, `NEXTAUTH_URL`, `NEXTAUTH_SECRET`, `NEXT_PUBLIC_SITE_URL` in hosting provider.
3. Build command: `npm run build`.
4. Start command: `npm run start`.
5. Run migrations in CI/CD before deployment cutover.

## Security and performance

- Input validation via Zod in all write APIs.
- Password hashing with bcrypt (cost 12).
- Secure response headers in `middleware.ts`.
- Typed server components + minimal client components.
- Dynamic sitemap and robots for SEO.
