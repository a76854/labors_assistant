<script setup lang="ts">
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'

const props = withDefaults(
  defineProps<{
    type?: string | null
    size?: number | string
  }>(),
  { type: '', size: 16 },
)

const iconName = computed(() => {
  switch (props.type) {
    case 'wage_arrears':
      return 'cash'
    case 'labor_contract':
      return 'document'
    case 'work_injury':
      return 'medkit'
    case 'other':
      return 'help'
    default:
      return 'scale'
  }
})
</script>

<template>
  <AppIcon :name="iconName" :size="size" />
</template>
