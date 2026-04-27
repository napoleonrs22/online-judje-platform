import { Card } from "@/shared/ui/card";
import { useTranslations } from "next-intl";

const practiceSets = [
  { title: "Arrays Fundamentals", difficulty: "Easy", tasks: 10 },
  { title: "Binary Search Patterns", difficulty: "Medium", tasks: 8 },
  { title: "Graph Traversal", difficulty: "Hard", tasks: 6 },
];

export default function DashboardPracticePage() {
  const t = useTranslations("DashboardPractice");

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
          {t("title")}
        </h2>
        <p className="mt-1 text-slate-500">
          {t("subtitle")}
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        {practiceSets.map((set) => (
          <Card key={set.title} className="space-y-3 hover:-translate-y-0.5">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
              {set.title}
            </h3>
            <p className="text-sm text-slate-500">
              {t("difficulty")}:{" "}
              <span className="font-medium text-slate-700 dark:text-slate-200">{set.difficulty}</span>
            </p>
            <p className="text-sm text-slate-500">{t("tasks")}: {set.tasks}</p>
          </Card>
        ))}
      </div>
    </div>
  );
}
