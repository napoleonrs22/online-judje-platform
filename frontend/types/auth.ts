// frontend/types/auth.ts
export interface AuthForm {
  email: string
  password: string
}

export interface RegisterForm extends AuthForm {
  role: 'student' | 'teacher'
  username: string
  full_name: string
  password2: string
}