import { notFound } from "next/navigation";
import { prisma } from "@/lib/prisma";

export default async function BlogPostPage({ params }: { params: { slug: string } }) {
  const post = await prisma.blogPost.findUnique({ where: { slug: params.slug } });

  if (!post || !post.isPublished) {
    notFound();
  }

  return (
    <article className="mx-auto max-w-3xl py-12 container-padding">
      <h1 className="text-3xl font-bold text-brand-900">{post.title}</h1>
      <p className="mt-2 text-sm text-slate-500">{new Date(post.publishedAt).toLocaleDateString("ru-RU")}</p>
      <div className="prose mt-6 max-w-none text-slate-700">
        <p>{post.content}</p>
      </div>
    </article>
  );
}
