import Link from "next/link";
import { prisma } from "@/lib/prisma";

export default async function BlogPage() {
  const posts = await prisma.blogPost.findMany({
    where: { isPublished: true },
    orderBy: { publishedAt: "desc" }
  });

  if (posts.length === 0) {
    return (
      <div className="mx-auto max-w-4xl py-12 container-padding">
        <h1 className="text-3xl font-bold text-brand-900">Блог</h1>
        <p className="mt-4 text-slate-600">Статьи скоро появятся. Подпишитесь на обновления через форму на главной.</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl py-12 container-padding">
      <h1 className="text-3xl font-bold text-brand-900">Блог</h1>
      <div className="mt-6 space-y-4">
        {posts.map((post) => (
          <article className="rounded-xl bg-white p-5 shadow-sm" key={post.id}>
            <h2 className="text-xl font-semibold">
              <Link href={`/blog/${post.slug}`}>{post.title}</Link>
            </h2>
            <p className="mt-2 text-sm text-slate-500">{new Date(post.publishedAt).toLocaleDateString("ru-RU")}</p>
            <p className="mt-3 text-slate-700">{post.excerpt}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
