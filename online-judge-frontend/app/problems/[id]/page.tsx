/** Страница задачи по id (общая для /problems/[id] и реэкспорта из /[locale]/problems/[id]). */
export default async function ProblemByIdPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <main className="p-8">
      <h1 className="text-xl font-semibold">Задача</h1>
      <p className="mt-2 text-gray-600">ID: {id}</p>
      <p className="mt-4 text-sm text-gray-500">
        Полная среда решения доступна в дашборде: раздел «Челленджи».
      </p>
    </main>
  );
}
