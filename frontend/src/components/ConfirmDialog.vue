<template>
  <div v-if="show" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="$emit('cancel')">
    <div class="card p-6 w-full max-w-md mx-4 space-y-4">
      <h3 class="text-lg font-bold">{{ title || "Confirmar" }}</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400">{{ message }}</p>
      <div class="flex gap-2 justify-end">
        <button @click="$emit('cancel')" class="btn-secondary">Cancelar</button>
        <button @click="$emit('confirm')" :class="danger ? 'btn-danger' : 'btn-primary'">Confirmar</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ show: boolean; title?: string; message?: string; danger?: boolean }>();
defineEmits<{ confirm: []; cancel: [] }>();
</script>
