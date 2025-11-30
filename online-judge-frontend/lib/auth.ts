// lib/auth.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  full_name: string;
  role: 'student' | 'teacher';
}

export interface LoginData {
  email: string;
  password: string;
}

export interface AuthResponse {
  id: string;
  username: string;
  email: string;
  role: string;
  full_name: string;
  rating: number;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export class AuthError extends Error {
  constructor(
    public statusCode: number,
    public message: string,
    public details?: unknown
  ) {
    super(message);
    this.name = 'AuthError';
  }
}

/**
 * Регистрация пользователя
 */
export async function register(data: RegisterData): Promise<AuthResponse> {
  try {
    const payload = {
      email: data.email,
      username: data.username,
      password: data.password,
      full_name: data.full_name,
      role: data.role,
    };

    console.log('Sending register payload:', payload);

    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    console.log('Register response status:', response.status);

    if (!response.ok) {
      const error = await response.json();
      console.error('Register error response:', error);
      throw new AuthError(
        response.status,
        'Ошибка при регистрации',
        error.detail
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof AuthError) {
      throw error;
    }
    console.error('Register fetch error:', error);
    throw new AuthError(500, 'Ошибка сети при регистрации', error);
  }
}

/**
 * Вход пользователя
 */
export async function login(data: LoginData): Promise<TokenResponse> {
  try {
    const payload = {
      email: data.email,
      password: data.password,
    };

    console.log('Sending login payload:', payload);

    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    console.log('Login response status:', response.status);

    if (!response.ok) {
      const error = await response.json();
      console.error('Login error response:', error);
      throw new AuthError(
        response.status,
        'Неверные учетные данные',
        error.detail
      );
    }

    const tokenData: TokenResponse = await response.json();

    // Сохраняем токен в localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', tokenData.access_token);
      localStorage.setItem('token_type', tokenData.token_type);
    }

    return tokenData;
  } catch (error) {
    if (error instanceof AuthError) {
      throw error;
    }
    console.error('Login fetch error:', error);
    throw new AuthError(500, 'Ошибка сети при входе', error);
  }
}

/**
 * Выход пользователя
 */
export function logout(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('access_token');
    localStorage.removeItem('token_type');
  }
}

/**
 * Получить сохраненный токен
 */
export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

/**
 * Проверить авторизацию
 */
export function isAuthenticated(): boolean {
  return getToken() !== null;
}