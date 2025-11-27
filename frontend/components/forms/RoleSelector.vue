<!-- frontend/components/forms/RoleSelector.vue -->
<template>
  <div class="role-selector">
    <p class="role-selector__label">Выберите роль</p>
    <div class="role-selector__options">
      <label class="role-option" :class="{ active: model === 'student' }">
        <input
          type="radio"
          v-model="model"
          value="student"
          :disabled="disabled"
        />
        <span>Студент</span>
      </label>
      <label class="role-option" :class="{ active: model === 'teacher' }">
        <input
          type="radio"
          v-model="model"
          value="teacher"
          :disabled="disabled"
        />
        <span>Преподаватель</span>
      </label>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  modelValue: string
  disabled?: boolean
}>()

const emit = defineEmits(['update:modelValue'])

const model = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})
</script>