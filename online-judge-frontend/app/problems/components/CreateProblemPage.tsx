'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function CreateProblemPage() {
  const router = useRouter();
  const [title, setTitle] = useState('');
  const [slug, setSlug] = useState('');
  const [description, setDescription] = useState('');
  const [difficulty, setDifficulty] = useState('Средний');
  const [timeLimit, setTimeLimit] = useState('2');
  const [memoryLimit, setMemoryLimit] = useState('256');
  const [checkerType, setCheckerType] = useState('exact');
  const [isPublic, setIsPublic] = useState(false);
  const [examples, setExamples] = useState([{ input: '', output: '', explanation: '' }]);
  const [hiddenTests, setHiddenTests] = useState([{ input: '', output: '' }]);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Авто-генерация slug
  const generateSlug = (text: string) => {
    return text
      .toLowerCase()
      .trim()
      .replace(/\s+/g, '-')
      .replace(/[^а-яёa-z0-9-]/g, '');
  };

  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTitle = e.target.value;
    setTitle(newTitle);
    if (!slug || slug === generateSlug(title)) {
      setSlug(generateSlug(newTitle));
    }
  };

  // Примеры
  const addExample = () => {
    setExamples([...examples, { input: '', output: '', explanation: '' }]);
  };

  const removeExample = (idx: number) => {
    setExamples(examples.filter((_, i) => i !== idx));
  };

  const updateExample = (idx: number, field: string, value: string) => {
    const updated = [...examples];
    updated[idx] = { ...updated[idx], [field]: value };
    setExamples(updated);
  };

  // Тесты
  const addTest = () => {
    setHiddenTests([...hiddenTests, { input: '', output: '' }]);
  };

  const removeTest = (idx: number) => {
    setHiddenTests(hiddenTests.filter((_, i) => i !== idx));
  };

  const updateTest = (idx: number, field: string, value: string) => {
    const updated = [...hiddenTests];
    updated[idx] = { ...updated[idx], [field]: value };
    setHiddenTests(updated);
  };

  // Валидация
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!title.trim()) newErrors.title = 'Название обязательно';
    if (!slug.trim()) newErrors.slug = 'Slug обязателен';
    if (!description.trim()) newErrors.description = 'Описание обязательно';
    if (examples.length === 0) newErrors.examples = 'Добавьте хотя бы один пример';
    if (examples.some(ex => !ex.input.trim() || !ex.output.trim())) {
      newErrors.examples = 'Заполните все примеры полностью';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Отправка
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setIsSubmitting(true);

    try {
      const testCases = [
        ...examples.map(ex => ({
          input_data: ex.input,
          output_data: ex.output,
          is_sample: true
        })),
        ...hiddenTests.map(tc => ({
          input_data: tc.input,
          output_data: tc.output,
          is_sample: false
        }))
      ];

      const payload = {
        title: title.trim(),
        slug: slug.trim(),
        description: description.trim(),
        difficulty,
        checker_type: checkerType,
        time_limit: parseInt(timeLimit) * 1000,
        memory_limit: parseInt(memoryLimit),
        is_public: isPublic,
        examples: examples.map(ex => ({
          input_data: ex.input,
          output_data: ex.output
        })),
        test_cases: testCases
      };

      const response = await fetch('/api/teacher/problems', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const result = await response.json();
        alert(`✅ Задача создана: ${result.slug}`);
        router.push('/teacher/problems');
      } else {
        const error = await response.json();
        alert(`❌ Ошибка: ${error.detail}`);
      }
    } catch (err) {
      alert(`❌ Ошибка подключения: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-white to-slate-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link href="/teacher/problems" className="text-blue-600 hover:text-blue-700 mb-4 inline-block">
            ← Назад к задачам
          </Link>
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Создать новую задачу</h1>
          <p className="text-slate-600">Заполните все обязательные поля для создания задачи</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Основная информация */}
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <h2 className="text-xl font-semibold mb-4 text-slate-900">📝 Основная информация</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Название задачи *
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={handleTitleChange}
                  placeholder="Проверка простого числа"
                  className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                    errors.title ? 'border-red-500 ring-red-200' : 'border-slate-200 ring-blue-200'
                  }`}
                />
                {errors.title && <p className="text-red-600 text-sm mt-1">{errors.title}</p>}
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  URL slug (автогенерируется) *
                </label>
                <input
                  type="text"
                  value={slug}
                  onChange={(e) => setSlug(e.target.value)}
                  placeholder="check-prime-number"
                  className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                    errors.slug ? 'border-red-500 ring-red-200' : 'border-slate-200 ring-blue-200'
                  }`}
                />
                {errors.slug && <p className="text-red-600 text-sm mt-1">{errors.slug}</p>}
              </div>
            </div>

            <div className="mt-4">
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                Описание задачи *
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Дано число N. Определите, является ли оно простым..."
                rows={4}
                className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                  errors.description ? 'border-red-500 ring-red-200' : 'border-slate-200 ring-blue-200'
                }`}
              />
              {errors.description && <p className="text-red-600 text-sm mt-1">{errors.description}</p>}
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">Сложность</label>
                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-200"
                >
                  <option>Легкий</option>
                  <option>Средний</option>
                  <option>Сложный</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">Time limit (сек)</label>
                <input
                  type="number"
                  value={timeLimit}
                  onChange={(e) => setTimeLimit(e.target.value)}
                  min="1"
                  max="60"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-200"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">Memory (MB)</label>
                <input
                  type="number"
                  value={memoryLimit}
                  onChange={(e) => setMemoryLimit(e.target.value)}
                  min="64"
                  max="1024"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-200"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">Тип проверки</label>
                <select
                  value={checkerType}
                  onChange={(e) => setCheckerType(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-200"
                >
                  <option value="exact">Точное совпадение</option>
                  <option value="tokens">По токенам</option>
                </select>
              </div>
            </div>
          </div>

          {/* Примеры */}
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <h2 className="text-xl font-semibold mb-4 text-slate-900">📚 Примеры (видны студентам)</h2>

            {errors.examples && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4 text-red-700 text-sm">
                {errors.examples}
              </div>
            )}

            {examples.map((example, idx) => (
              <div key={idx} className="border border-slate-200 rounded-lg p-4 mb-3">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Input</label>
                    <textarea
                      value={example.input}
                      onChange={(e) => updateExample(idx, 'input', e.target.value)}
                      rows={3}
                      className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-200 font-mono text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Output</label>
                    <textarea
                      value={example.output}
                      onChange={(e) => updateExample(idx, 'output', e.target.value)}
                      rows={3}
                      className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-200 font-mono text-sm"
                    />
                  </div>
                </div>
                <textarea
                  value={example.explanation}
                  onChange={(e) => updateExample(idx, 'explanation', e.target.value)}
                  placeholder="Объяснение (опционально)"
                  rows={2}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-200 text-sm mt-3"
                />
                {examples.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeExample(idx)}
                    className="mt-2 text-red-600 hover:text-red-700 text-sm font-medium"
                  >
                    ✕ Удалить пример
                  </button>
                )}
              </div>
            ))}

            <button
              type="button"
              onClick={addExample}
              className="text-blue-600 hover:text-blue-700 font-medium mt-3"
            >
              + Добавить пример
            </button>
          </div>

          {/* Скрытые тесты */}
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <h2 className="text-xl font-semibold mb-4 text-slate-900">🔒 Скрытые тесты (только для проверки)</h2>

            {hiddenTests.map((test, idx) => (
              <div key={idx} className="border border-slate-200 rounded-lg p-4 mb-3 bg-slate-50">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Input</label>
                    <textarea
                      value={test.input}
                      onChange={(e) => updateTest(idx, 'input', e.target.value)}
                      rows={3}
                      className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-200 font-mono text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Output</label>
                    <textarea
                      value={test.output}
                      onChange={(e) => updateTest(idx, 'output', e.target.value)}
                      rows={3}
                      className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-200 font-mono text-sm"
                    />
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => removeTest(idx)}
                  className="mt-2 text-red-600 hover:text-red-700 text-sm font-medium"
                >
                  ✕ Удалить тест
                </button>
              </div>
            ))}

            <button
              type="button"
              onClick={addTest}
              className="text-blue-600 hover:text-blue-700 font-medium mt-3"
            >
              + Добавить скрытый тест
            </button>
          </div>

          {/* Публикация */}
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <h2 className="text-xl font-semibold mb-4 text-slate-900">🚀 Публикация</h2>

            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={isPublic}
                onChange={(e) => setIsPublic(e.target.checked)}
                className="w-5 h-5 border border-slate-300 rounded focus:ring-2 focus:ring-blue-500"
              />
              <div>
                <p className="font-semibold text-slate-900">
                  {isPublic ? '👁️ Задача опубликована' : '🔒 Задача скрыта'}
                </p>
                <p className="text-sm text-slate-600">
                  {isPublic
                    ? 'Студенты могут видеть и решать эту задачу'
                    : 'Задача доступна только вам'}
                </p>
              </div>
            </label>
          </div>

          {/* Кнопки действия */}
          <div className="flex gap-3 sticky bottom-0 bg-gradient-to-t from-white to-white/80 p-4 -mx-6">
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white font-semibold py-3 rounded-lg transition flex items-center justify-center gap-2"
            >
              {isSubmitting ? '⏳ Создание...' : '✅ Создать задачу'}
            </button>
            <Link
              href="/teacher/problems"
              className="px-6 bg-slate-200 hover:bg-slate-300 text-slate-900 font-semibold py-3 rounded-lg transition text-center"
            >
              Отмена
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}