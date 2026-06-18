<template>
  <div class="flex items-center justify-center py-12">
    <div class="flex flex-col items-center gap-3">
      <div class="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
      <p class="text-sm text-gray-500">{{ message || "Carregando..." }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ message?: string }>();
</script>
