'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import SideMenu from '../components/SideMenu';
import HeaderProblems from '../components/HeaderProblems';

export default function CreateProblemPage() {
  const router = useRouter();
  const [title, setTitle] = useState('');
  const [slug, setSlug] = useState('');
  const [difficulty, setDifficulty] = useState('Легкий');
  const [description, setDescription] = useState('');
  const [timeLimit, setTimeLimit] = useState('1');
  const [memoryLimit, setMemoryLimit] = useState('256');
  const [checkerType, setCheckerType] = useState('exact');
  const [isPublic, setIsPublic] = useState(true);
  const [examples, setExamples] = useState([{ input_data: '', output_data: '' }]);
  const [testCases, setTestCases] = useState<Array<{ input_data: string; output_data: string }>>([]);
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
    // Обновляем slug только если он был автогенерирован
    if (!slug || slug === generateSlug(title)) {
      setSlug(generateSlug(newTitle));
    }
  };

  // Валидация
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!title.trim()) newErrors.title = 'Название обязательно';
    if (!slug.trim()) newErrors.slug = 'Slug обязателен';
    if (!description.trim()) newErrors.description = 'Описание обязательно';
    if (examples.length === 0) newErrors.examples = 'Добавьте хотя бы один пример';
    if (examples.some(ex => !ex.input_data.trim() || !ex.output_data.trim())) {
      newErrors.examples = 'Заполните все примеры полностью';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Примеры
  const addExample = () => {
    setExamples([...examples, { input_data: '', output_data: '' }]);
  };

  const removeExample = (idx: number) => {
    if (examples.length > 1) {
      setExamples(examples.filter((_, i) => i !== idx));
    }
  };

  const updateExample = (idx: number, field: string, value: string) => {
    const updated = [...examples];
    updated[idx] = { ...updated[idx], [field]: value };
    setExamples(updated);
  };

  // Тесты
  const addTestCase = () => {
    setTestCases([...testCases, { input_data: '', output_data: '' }]);
  };

  const removeTestCase = (idx: number) => {
    setTestCases(testCases.filter((_, i) => i !== idx));
  };

  const updateTestCase = (idx: number, field: string, value: string) => {
    const updated = [...testCases];
    updated[idx] = { ...updated[idx], [field]: value };
    setTestCases(updated);
  };

  // Отправка на API
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setIsSubmitting(true);

    try {
      // ✅ ИСПРАВЛЕНИЕ: Используем правильный backend URL
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
      const ENDPOINT = `${API_URL}/teacher/problems`;

      // Формируем payload согласно API документации
      const testCasesPayload = [
        // Примеры (is_sample: true)
        ...examples.map(ex => ({
          input_data: ex.input_data,
          output_data: ex.output_data,
          is_sample: true
        })),
        // Скрытые тесты (is_sample: false)
        ...testCases.map(tc => ({
          input_data: tc.input_data,
          output_data: tc.output_data,
          is_sample: false
        }))
      ];

      const payload = {
        title: title.trim(),
        slug: slug.trim(),
        description: description.trim(),
        difficulty,
        checker_type: checkerType,
        examples: examples,
        test_cases: testCasesPayload,
        is_public: isPublic
      };

      console.log('📤 Отправляем на:', ENDPOINT);
      console.log('📋 Payload:', payload);

      // Получаем токен из localStorage
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

      if (!token) {
        alert('❌ Ошибка: токен авторизации не найден. Пожалуйста, авторизуйтесь.');
        return;
      }

      const response = await fetch(ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      console.log('📊 Response status:', response.status);

      // Попытка получить JSON, иначе текст
      let data;
      try {
        data = await response.json();
      } catch (parseError) {
        const text = await response.text();
        console.error('❌ Не удалось разобрать JSON. Ответ:', text);
        throw new Error(`Сервер вернул ошибку: ${text.substring(0, 100)}`);
      }

      console.log('📦 Response data:', data);

      if (response.ok) {
        alert(`✅ Задача "${data.title}" создана успешно!\nID: ${data.problem_id}`);
        router.push('/problems');
      } else {
        console.error('❌ API Error:', data);
        alert(`❌ Ошибка: ${data.detail || data.message || 'Неизвестная ошибка'}`);
      }
    } catch (err) {
      console.error('❌ Fetch Error:', err);
      if (err instanceof Error) {
        alert(`❌ Ошибка: ${err.message}`);
      } else {
        alert('❌ Произошла неизвестная ошибка');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-white">
      {/* Меню */}
      <SideMenu />

      {/* Основная область */}
      <div className="flex-1 flex flex-col ml-64 min-w-0">
        <HeaderProblems />

        {/* Форма - ТОЧНО как в Figma */}
        <div className="flex-1 overflow-y-auto bg-white p-8">
          <div className="grid grid-cols-2 gap-8">
            {/* ========== ЛЕВАЯ ЧАСТЬ - ФОРМА (из Figma) ========== */}
            <div className="flex flex-col gap-5">
              <h1 className="text-xl font-semibold text-stone-950">Создать новую задачу</h1>

              <form onSubmit={handleSubmit} className="space-y-5">
                {/* Название задачи */}
                <div>
                  <div className="text-neutral-600/50 text-base font-normal mb-1">
                    Например: Факториал числа
                  </div>
                  <div className="text-stone-950 text-base font-semibold mb-2">
                    Название задачи *
                  </div>
                  <input
                    type="text"
                    value={title}
                    onChange={handleTitleChange}
                    placeholder="Например: Факториал числа"
                    className={`w-full h-10 px-3 py-2 bg-zinc-100 border-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 transition ${
                      errors.title ? 'border-red-500' : 'border-zinc-300'
                    }`}
                  />
                  {errors.title && <p className="text-red-600 text-sm mt-1">{errors.title}</p>}
                </div>

                {/* Slug */}
                <div>
                  <div className="text-stone-950 text-base font-semibold mb-2">
                    URL slug *
                  </div>
                  <input
                    type="text"
                    value={slug}
                    onChange={(e) => setSlug(e.target.value)}
                    placeholder="автогенерируется из названия"
                    className={`w-full h-10 px-3 py-2 bg-zinc-100 border-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 transition text-sm ${
                      errors.slug ? 'border-red-500' : 'border-zinc-300'
                    }`}
                  />
                  {errors.slug && <p className="text-red-600 text-sm mt-1">{errors.slug}</p>}
                  <p className="text-xs text-neutral-600 mt-1">Уникальный ID для URL (например: check-prime-number)</p>
                </div>

                {/* Сложность (как в Figma) */}
                <div>
                  <div className="text-stone-950 text-base font-semibold mb-3">
                    Сложность
                  </div>
                  <div className="space-y-2">
                    {[
                      { value: 'Легкий', icon: '🟢' },
                      { value: 'Средний', icon: '🟡' },
                      { value: 'Сложный', icon: '🔴' }
                    ].map((level) => (
                      <div key={level.value} className="flex items-center">
                        <div className="w-full h-10 bg-zinc-100 border-l-2 border-r-2 border-t border-b border-zinc-300 rounded-lg flex items-center px-3">
                          <label className="flex items-center gap-2 cursor-pointer flex-1">
                            <input
                              type="radio"
                              name="difficulty"
                              value={level.value}
                              checked={difficulty === level.value}
                              onChange={(e) => setDifficulty(e.target.value)}
                              className="w-4 h-4"
                            />
                            <span className="text-stone-950 text-base font-normal">
                              {level.icon} {level.value}
                            </span>
                          </label>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Описание задачи */}
                <div>
                  <div className="text-stone-950 text-base font-semibold mb-2">
                    Описание задачи *
                  </div>
                  <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Подробное описание, условия, примеры..."
                    rows={7}
                    className={`w-full px-3 py-2 bg-zinc-100 border-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 transition resize-none ${
                      errors.description ? 'border-red-500' : 'border-zinc-300'
                    }`}
                  />
                  {errors.description && <p className="text-red-600 text-sm mt-1">{errors.description}</p>}
                </div>

                {/* Time Limit и Memory Limit */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-neutral-600 text-base font-normal mb-2">
                      Time limit (сек)
                    </div>
                    <input
                      type="number"
                      value={timeLimit}
                      onChange={(e) => setTimeLimit(e.target.value)}
                      min="1"
                      max="300"
                      className="w-full h-10 px-3 py-2 bg-zinc-100 border-2 border-zinc-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
                    />
                  </div>
                  <div>
                    <div className="text-neutral-600 text-base font-normal mb-2">
                      Memory limit (MB)
                    </div>
                    <input
                      type="number"
                      value={memoryLimit}
                      onChange={(e) => setMemoryLimit(e.target.value)}
                      min="64"
                      max="2048"
                      className="w-full h-10 px-3 py-2 bg-zinc-100 border-2 border-zinc-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
                    />
                  </div>
                </div>

                {/* Опции */}
                <div className="space-y-2 pt-2 border-t border-zinc-300">
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={isPublic}
                      onChange={(e) => setIsPublic(e.target.checked)}
                      className="w-4 h-4"
                    />
                    <span className="text-stone-950 text-sm">
                      {isPublic ? '👁️ Задача опубликована' : '🔒 Задача скрыта'}
                    </span>
                  </label>
                </div>
              </form>
            </div>

            {/* ========== ПРАВАЯ ЧАСТЬ - ПРИМЕРЫ (из Figma) ========== */}
            <div className="flex flex-col gap-4">
              <h2 className="text-xl font-semibold text-stone-950">Примеры</h2>

              {errors.examples && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
                  {errors.examples}
                </div>
              )}

              {/* Примеры */}
              <div className="space-y-3 max-h-[400px] overflow-y-auto">
                {examples.map((example, idx) => (
                  <div key={idx} className="bg-zinc-100 rounded-lg outline outline-2 outline-offset-[-2px] outline-zinc-300 px-5 py-4">
                    <div className="flex justify-between items-center mb-3">
                      <div className="text-stone-950 text-base font-semibold">
                        Пример {idx + 1}
                      </div>
                      {examples.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeExample(idx)}
                          className="text-red-600 hover:text-red-700 text-sm font-semibold"
                        >
                          ✕
                        </button>
                      )}
                    </div>

                    <div className="space-y-3">
                      <div>
                        <div className="text-neutral-600 text-base font-normal mb-1">
                          Input:
                        </div>
                        <textarea
                          value={example.input_data}
                          onChange={(e) => updateExample(idx, 'input_data', e.target.value)}
                          rows={4}
                          className="w-full bg-zinc-100 rounded-lg border-2 border-zinc-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400 font-mono text-sm"
                        />
                      </div>

                      <div>
                        <div className="text-neutral-600 text-base font-normal mb-1">
                          Output
                        </div>
                        <textarea
                          value={example.output_data}
                          onChange={(e) => updateExample(idx, 'output_data', e.target.value)}
                          rows={3}
                          className="w-full bg-zinc-100 rounded-lg border-2 border-zinc-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400 font-mono text-sm"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Кнопка добавить решение */}
              <button
                type="button"
                onClick={addExample}
                className="w-full py-2.5 border-2 border-dashed border-neutral-600/50 rounded-lg text-neutral-600 text-base font-semibold hover:bg-slate-50 hover:border-neutral-600 transition flex items-center justify-center gap-1"
              >
                + Добавить решение
              </button>

              {/* Скрытые тесты (опционально) */}
              <div className="mt-4 pt-4 border-t border-zinc-300">
                <h3 className="text-sm font-semibold text-stone-950 mb-3">Скрытые тесты (опционально)</h3>

                <div className="space-y-2 max-h-[150px] overflow-y-auto">
                  {testCases.map((tc, idx) => (
                    <div key={idx} className="bg-slate-50 rounded border border-zinc-300 p-2 text-sm">
                      <div className="flex justify-between items-center mb-1">
                        <span className="font-medium text-slate-700">Тест {idx + 1}</span>
                        <button
                          type="button"
                          onClick={() => removeTestCase(idx)}
                          className="text-red-600 hover:text-red-700 text-xs"
                        >
                          ✕
                        </button>
                      </div>
                      <textarea
                        value={tc.input_data}
                        onChange={(e) => updateTestCase(idx, 'input_data', e.target.value)}
                        placeholder="Input"
                        rows={1}
                        className="w-full px-2 py-1 border border-zinc-300 rounded text-xs font-mono mb-1 resize-none"
                      />
                      <textarea
                        value={tc.output_data}
                        onChange={(e) => updateTestCase(idx, 'output_data', e.target.value)}
                        placeholder="Output"
                        rows={1}
                        className="w-full px-2 py-1 border border-zinc-300 rounded text-xs font-mono resize-none"
                      />
                    </div>
                  ))}
                </div>

                <button
                  type="button"
                  onClick={addTestCase}
                  className="w-full mt-2 py-1.5 text-blue-600 hover:text-blue-700 font-medium text-sm"
                >
                  + Добавить тест
                </button>
              </div>

              {/* Кнопка создать задачу */}
              <button
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="w-full py-2.5 bg-blue-900 hover:bg-blue-950 disabled:bg-slate-400 text-white text-base font-semibold rounded-lg transition flex items-center justify-center gap-2 mt-4"
              >
                📝 {isSubmitting ? 'Создание...' : 'Создать задачу'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}