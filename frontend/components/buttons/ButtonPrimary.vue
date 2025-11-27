<template>
  <component
    :is="tag"
    :to="to"
    :type="buttonType"
    :disabled="disabled"
    class="btn btn--primary"
    @click="$emit('click')"
  >
    <slot />
  </component>
</template>

<script setup lang="ts">
const props = defineProps<{
  to?: string
  type?: string
  disabled?: boolean
}>()

defineEmits(['click'])

const tag = computed(() => (props.to ? 'NuxtLink' : 'button'))
const buttonType = computed(() => props.to ? undefined : (props.type || 'button'))
</script>