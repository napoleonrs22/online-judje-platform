<!-- frontend/components/forms/FormInput.vue -->
<template>
  <div class="form-group">
    <label class="form-group__label" :for="id">{{ label }}</label>
    <input
      :id="id"
      v-model="model"
      :type="type"
      :placeholder="placeholder"
      class="form-group__input"
      :class="{ error: hasError }"
      :required="required"
      :disabled="disabled"
      :autocomplete="autocomplete"
    />
    <FormError v-if="hasError" :message="errorMessage" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import FormError from '~/components/forms/FormError.vue'

const props = defineProps<{
  modelValue: string
  label: string
  type?: string
  placeholder?: string
  required?: boolean
  disabled?: boolean
  autocomplete?: string
  error?: string
}>()

const emit = defineEmits(['update:modelValue'])

const model = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const id = computed(() => `input-${Math.random().toString(36).slice(2)}`)
const hasError = computed(() => !!props.error)
const errorMessage = computed(() => props.error || '')
</script>