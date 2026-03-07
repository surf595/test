import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

async function main() {
  await prisma.blogPost.upsert({
    where: { slug: "kak-podgotovitsya-k-pervoy-sessii" },
    update: {},
    create: {
      slug: "kak-podgotovitsya-k-pervoy-sessii",
      title: "Как подготовиться к первой психотерапевтической сессии",
      excerpt: "Практические шаги, которые помогут получить максимум пользы от первой встречи.",
      content: "Первая сессия — это безопасное пространство для знакомства, постановки целей и обсуждения ожиданий..."
    }
  });
}

main()
  .then(async () => {
    await prisma.$disconnect();
  })
  .catch(async (error) => {
    console.error(error);
    await prisma.$disconnect();
    process.exit(1);
  });
