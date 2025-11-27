// frontend/utils/validators.ts
export const validateEmail = (val: string) => val.includes('@') ? '' : 'Некорректный email'
export const validatePassword = (val: string) => val.length >= 6 ? '' : 'Минимум 6 символов'
// и т.д.