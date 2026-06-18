<template>
  <div class="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
    <transition-group name="toast">
      <div
        v-for="t in toasts"
        :key="t.id"
        :class="[
          'px-4 py-3 rounded-lg shadow-lg text-sm font-medium flex items-center gap-2 animate-slide-in',
          bgClass(t.type),
        ]"
      >
        <span>{{ icon(t.type) }}</span>
        <span class="flex-1">{{ t.message }}</span>
        <button @click="remove(t.id)" class="ml-2 opacity-70 hover:opacity-100 text-lg leading-none">&times;</button>
      </div>
    </transition-group>
  </div>
</template>

<script setup lang="ts">
import { useToast } from "@/composables/useToast";

const { toasts, remove } = useToast();

function bgClass(type: string) {
  return {
    success: "bg-green-600 text-white",
    error: "bg-red-600 text-white",
    warning: "bg-yellow-500 text-white",
    info: "bg-blue-600 text-white",
  }[type] || "bg-gray-800 text-white";
}

function icon(type: string) {
  return {
    success: "✓",
    error: "✕",
    warning: "⚠",
    info: "ℹ",
  }[type] || "•";
}
</script>

<style scoped>
.toast-enter-active { animation: slideIn 0.3s ease-out; }
.toast-leave-active { animation: slideOut 0.3s ease-in; }
@keyframes slideIn {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}
@keyframes slideOut {
  from { transform: translateX(0); opacity: 1; }
  to { transform: translateX(100%); opacity: 0; }
}
</style>
