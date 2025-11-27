// frontend/composables/useForm.ts
import { ref } from 'vue'
import type { Ref } from 'vue'
export default function useForm<T extends Record<string, any>>(
  form: Ref<T>,
  rules: Partial<Record<keyof T, (val: any, form: T) => string>>
) {
  const errors = ref<Partial<Record<keyof T, string>>>({})

  const validate = () => {
    let valid = true
    for (const key in rules) {
      const error = rules[key]!(form.value[key], form.value)
      errors.value[key] = error
      if (error) valid = false
    }
    return valid
  }

  return { errors, validate }
}