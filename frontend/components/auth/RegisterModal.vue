<!-- components/auth/RegisterModal.vue -->
<template>
  <div class="modal-overlay" @click="close">
    <div class="modal" @click.stop>
      <!-- Закрытие -->
      <button class="modal__close" @click="close" aria-label="Закрыть">×</button>

      <!-- Заголовок -->
      <h2 class="modal__title">Регистрация аккаунта</h2>

      <!-- Форма -->
      <form @submit.prevent="handleRegister" class="modal__form">
        <!-- Выбор роли -->
        <div class="role-selector">
          <p class="role-selector__label">Выберите роль</p>
          <div class="role-selector__options">
            <label class="role-option" :class="{ active: form.role === 'student' }">
              <input
                type="radio"
                v-model="form.role"
                value="student"
                :disabled="auth.isLoading"
              />
              <span>Студент</span>
            </label>
            <label class="role-option" :class="{ active: form.role === 'teacher' }">
              <input
                type="radio"
                v-model="form.role"
                value="teacher"
                :disabled="auth.isLoading"
              />
              <span>Преподаватель</span>
            </label>
          </div>
        </div>

        <!-- Username -->
        <div class="form-group">
          <label class="form-group__label">Придумайте имя пользователя</label>
          <input
            v-model="form.username"
            type="text"
            class="form-group__input"
            required
            :disabled="auth.isLoading"
            autocomplete="username"
          />
        </div>

        <!-- Email -->
        <div class="form-group">
          <label class="form-group__label">Введите электронную почту</label>
          <input
            v-model="form.email"
            type="email"
            class="form-group__input"
            required
            :disabled="auth.isLoading"
            autocomplete="email"
          />
        </div>

        <!-- Полное имя -->
        <div class="form-group">
          <label class="form-group__label">Введите полное имя</label>
          <input
            v-model="form.full_name"
            type="text"
            class="form-group__input"
            required
            :disabled="auth.isLoading"
            autocomplete="name"
          />
        </div>

        <!-- Пароль -->
        <div class="form-group">
          <label class="form-group__label">Придумайте пароль</label>
          <input
            v-model="form.password"
            type="password"
            class="form-group__input"
            required
            :disabled="auth.isLoading"
            autocomplete="new-password"
          />
        </div>

        <!-- Повтор пароля -->
        <div class="form-group">
          <label class="form-group__label">Повторите пароль</label>
          <input
            v-model="form.password2"
            type="password"
            class="form-group__input"
            :class="{ error: passwordMismatch }"
            required
            :disabled="auth.isLoading"
            autocomplete="new-password"
          />
        </div>

        <!-- Ошибка пароля -->
        <div v-if="passwordMismatch" class="modal__error">
          Пароли не совпадают!
        </div>

        <!-- Ошибка сервера -->
        <div v-if="auth.error" class="modal__error">
          {{ auth.error }}
        </div>

        <!-- Ссылка на вход -->
        <div class="modal__links">
          <button
            type="button"
            @click="switchToLogin"
            class="modal__link"
            :disabled="auth.isLoading"
          >
            Забыли пароль? Нет аккаунта? Зарегистрироваться
          </button>
        </div>

        <!-- Кнопка регистрации -->
        <button
          type="submit"
          class="btn btn--primary modal__submit"
          :disabled="auth.isLoading || passwordMismatch"
        >
          {{ auth.isLoading ? 'Вход...' : 'Вход' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '~/stores/auth'

const emit = defineEmits<{
  close: []
  'open-login': []
}>()

const auth = useAuthStore()
const form = ref({
  username: '',
  email: '',
  full_name: '',
  password: '',
  password2: '',
  role: 'student' as 'student' | 'teacher'
})

const passwordMismatch = computed(
  () => form.value.password && form.value.password2 && form.value.password !== form.value.password2
)

const handleRegister = async () => {
  if (passwordMismatch.value) return

  try {
    await auth.register({ ...form.value })
    emit('close')
  } catch (e) {
    // Ошибка уже в auth.error
  }
}

const switchToLogin = () => {
  emit('open-login')
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
  overflow-y: auto;
  padding: 20px 0;
}

.modal {
  background: white;
  border-radius: 12px;
  padding: 2.5rem 2rem;
  width: 95%;
  max-width: 400px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  position: relative;
  margin: auto;

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
    gap: 0.8rem;
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
    font-size: 0.75rem;
    margin: 0.5rem 0 1rem;
  }

  &__link {
    background: none;
    border: none;
    color: #6f42c1;
    cursor: pointer;
    text-decoration: none;
    font-size: 0.75rem;
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
  gap: 0.3rem;

  &__label {
    font-size: 0.75rem;
    font-weight: 600;
    color: #333;
  }

  &__input {
    padding: 8px 10px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 0.85rem;
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

    &.error {
      border-color: #c33;
      background: #fff5f5;
    }
  }
}

.role-selector {
  &__label {
    font-size: 0.75rem;
    font-weight: 600;
    color: #333;
    margin-bottom: 0.5rem;
  }

  &__options {
    display: flex;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
  }
}

.role-option {
  flex: 1;
  position: relative;
  cursor: pointer;

  input {
    position: absolute;
    opacity: 0;
    width: 0;
    height: 0;
  }

  span {
    display: block;
    padding: 8px 12px;
    border: 1.5px solid #ddd;
    border-radius: 6px;
    text-align: center;
    font-size: 0.8rem;
    font-weight: 600;
    transition: all 0.2s;
    color: #333;
  }

  &.active span {
    border-color: #6f42c1;
    background: #f0ebf8;
    color: #6f42c1;
  }

  input:disabled ~ span {
    opacity: 0.5;
    cursor: not-allowed;
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