<!-- components/auth/LoginModal.vue -->
<template>
  <div class="modal-overlay" @click="close">
    <div class="modal" @click.stop>
      <!-- Закрытие -->
      <button class="modal__close" @click="close" aria-label="Закрыть">×</button>

      <!-- Заголовок -->
      <h2 class="modal__title">Авторизация в аккаунт</h2>

      <!-- Форма -->
      <form @submit.prevent="handleLogin" class="modal__form">
        <!-- Email/Username -->
        <div class="form-group">
          <label class="form-group__label">Введите логин</label>
          <input
            v-model="form.email"
            type="text"
            placeholder="admin@example.com"
            class="form-group__input"
            required
            :disabled="auth.isLoading"
            autocomplete="username"
          />
        </div>

        <!-- Пароль -->
        <div class="form-group">
          <label class="form-group__label">Введите пароль</label>
          <input
            v-model="form.password"
            type="password"
            placeholder="••••••••"
            class="form-group__input"
            required
            :disabled="auth.isLoading"
            autocomplete="current-password"
          />
        </div>

        <!-- Ошибка -->
        <div v-if="auth.error" class="modal__error">
          {{ auth.error }}
        </div>

        <!-- Ссылки забыли пароль и регистрация -->
        <div class="modal__links">
          <button type="button" class="modal__link">Забыли пароль?</button>
          <button
            type="button"
            @click="switchToRegister"
            class="modal__link"
            :disabled="auth.isLoading"
          >
            Нет аккаунта? Зарегистрироваться
          </button>
        </div>

        <!-- Кнопка входа -->
        <button
          type="submit"
          class="btn btn--primary modal__submit"
          :disabled="auth.isLoading"
        >
          {{ auth.isLoading ? 'Вход...' : 'Вход' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '~/stores/auth'

const emit = defineEmits<{
  close: []
  'open-register': []
}>()

const auth = useAuthStore()
const form = ref({
  email: '',
  password: ''
})

const handleLogin = async () => {
  try {
    await auth.login(form.value.email, form.value.password)
    emit('close')
  } catch (e) {
    // Ошибка уже в auth.error
  }
}

const switchToRegister = () => {
  emit('open-register')
}

const close = () => emit('close')
</script>

<style scoped lang="scss">
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(2px);
}

.modal {
  background: white;
  border-radius: 12px;
  padding: 2.5rem 2rem;
  width: 95%;
  max-width: 400px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  position: relative;

  &__close {
    position: absolute;
    top: 0.75rem;
    right: 0.75rem;
    background: none;
    border: none;
    font-size: 1.8rem;
    color: #999;
    cursor: pointer;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;

    &:hover {
      color: #333;
    }
  }

  &__title {
    text-align: center;
    font-size: 1.5rem;
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 1.5rem;
  }

  &__form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  &__error {
    background: #fee;
    border: 1px solid #fcc;
    border-radius: 6px;
    padding: 10px 12px;
    font-size: 0.85rem;
    color: #c33;
  }

  &__links {
    display: flex;
    justify-content: space-between;
    font-size: 0.8rem;
    margin: 0.5rem 0 1rem;
  }

  &__link {
    background: none;
    border: none;
    color: #6f42c1;
    cursor: pointer;
    text-decoration: none;
    font-size: 0.8rem;
    transition: color 0.2s;

    &:hover:not(:disabled) {
      color: #5a32a3;
      text-decoration: underline;
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }

  &__submit {
    width: 100%;
    padding: 10px;
    font-size: 0.95rem;
    margin-top: 0.5rem;
  }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;

  &__label {
    font-size: 0.8rem;
    font-weight: 600;
    color: #333;
  }

  &__input {
    padding: 10px 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 0.9rem;
    transition: all 0.2s;
    font-family: inherit;

    &:focus {
      outline: none;
      border-color: #6f42c1;
      box-shadow: 0 0 0 2px rgba(111, 66, 193, 0.1);
    }

    &:disabled {
      background: #f5f5f5;
      color: #999;
      cursor: not-allowed;
    }
  }
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
  border: none;
  font-size: 0.95rem;

  &--primary {
    background: #6f42c1;
    color: white;

    &:hover:not(:disabled) {
      background: #5a32a3;
    }

    &:disabled {
      background: #999;
      cursor: not-allowed;
    }
  }
}
</style>