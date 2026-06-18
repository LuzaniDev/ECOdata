<template>
  <Layout>
    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Dashboard</h2>
        <button @click="refresh" class="btn-secondary text-sm" :disabled="loading">
          <svg class="w-4 h-4" :class="{ 'animate-spin': loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          Atualizar
        </button>
      </div>

      <LoadingSpinner v-if="loading" />
      <template v-else>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div v-for="card in kpiCards" :key="card.label" class="card p-5 hover:shadow-md transition-shadow">
            <div class="flex items-center justify-between mb-3">
              <span class="text-xs font-semibold uppercase tracking-wider text-gray-500">{{ card.label }}</span>
              <span :class="'text-lg ' + card.iconColor">{{ card.icon }}</span>
            </div>
            <div class="flex items-baseline gap-2">
              <span class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ card.value }}</span>
              <span :class="['text-xs font-medium px-2 py-0.5 rounded-full', card.badgeClass]">{{ card.badge }}</span>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div class="card">
            <div class="p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 class="font-semibold text-gray-900 dark:text-gray-100">Agendamentos</h3>
            </div>
            <div class="p-4">
              <table class="w-full text-sm" v-if="schedules.length">
                <thead><tr class="text-left text-xs text-gray-500 uppercase">
                  <th class="pb-2 pr-4">Nome</th>
                  <th class="pb-2 pr-4">Tipo</th>
                  <th class="pb-2 text-right">Status</th>
                </tr></thead>
                <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
                  <tr v-for="s in schedules.slice(0, 5)" :key="s.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/30">
                    <td class="py-2.5 pr-4 font-medium truncate max-w-32">{{ s.name }}</td>
                    <td class="py-2.5 pr-4">
                      <span class="badge-info text-xs">{{ s.tipo }}</span>
                    </td>
                    <td class="py-2.5 text-right">
                      <span :class="s.enabled ? 'badge-success' : 'badge-error'">
                        {{ s.enabled ? 'Ativo' : 'Inativo' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
              <p v-else class="text-sm text-gray-400 text-center py-4">Nenhum agendamento</p>
            </div>
          </div>

          <div class="card">
            <div class="p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 class="font-semibold text-gray-900 dark:text-gray-100">Últimas Execuções</h3>
            </div>
            <div class="p-4">
              <table class="w-full text-sm" v-if="recentExecutions.length">
                <thead><tr class="text-left text-xs text-gray-500 uppercase">
                  <th class="pb-2 pr-4">Tipo</th>
                  <th class="pb-2 pr-4">Status</th>
                  <th class="pb-2 text-right">Data</th>
                </tr></thead>
                <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
                  <tr v-for="e in recentExecutions.slice(0, 5)" :key="e.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/30">
                    <td class="py-2.5 pr-4">
                      <span class="badge-info text-xs">{{ e.tipo }}</span>
                    </td>
                    <td class="py-2.5 pr-4">
                      <span :class="statusClass(e.status)">{{ e.status }}</span>
                    </td>
                    <td class="py-2.5 text-right text-xs text-gray-500">{{ formatDate(e.started_at) }}</td>
                  </tr>
                </tbody>
              </table>
              <p v-else class="text-sm text-gray-400 text-center py-4">Nenhuma execução</p>
            </div>
          </div>
        </div>
      </template>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import Layout from "@/components/Layout.vue";
import LoadingSpinner from "@/components/LoadingSpinner.vue";
import { apiGet } from "@/composables/useApi";

const loading = ref(true);
const schedules = ref<any[]>([]);
const recentExecutions = ref<any[]>([]);
const kpiCards = ref<any[]>([]);

function statusClass(status: string) {
  return {
    success: "badge-success",
    failed: "badge-error",
    running: "badge-warning",
    warning: "badge-warning",
  }[status] || "badge-info";
}

function formatDate(dateStr: string) {
  if (!dateStr) return "-";
  return new Date(dateStr).toLocaleString("pt-BR");
}

async function refresh() {
  loading.value = true;
  try {
    const [schedData, execData] = await Promise.all([
      apiGet("/api/scheduler"),
      apiGet("/api/auditoria", { per_page: 20 }),
    ]);
    schedules.value = schedData as any[];
    recentExecutions.value = (execData as any).items || [];

    const latest: Record<string, string> = {};
    for (const e of recentExecutions.value) {
      if (!latest[e.tipo] || new Date(e.started_at) > new Date(latest[e.tipo])) {
        latest[e.tipo] = new Date(e.started_at).toLocaleString("pt-BR");
      }
    }

    kpiCards.value = [
      {
        label: "Agendamentos Ativos",
        value: schedules.value.filter((s: any) => s.enabled).length,
        badge: `${schedules.value.length} total`,
        badgeClass: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
        icon: "⏰",
        iconColor: "text-blue-500",
      },
      {
        label: "Execuções Hoje",
        value: recentExecutions.value.filter((e: any) => {
          const today = new Date();
          const d = new Date(e.started_at);
          return d.toDateString() === today.toDateString();
        }).length,
        badge: `${recentExecutions.value.length} total`,
        badgeClass: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
        icon: "⚡",
        iconColor: "text-amber-500",
      },
      {
        label: "Última Execução",
        value: recentExecutions.value[0]?.tipo || "-",
        badge: recentExecutions.value[0]?.status || "-",
        badgeClass: recentExecutions.value[0]?.status === "success"
          ? "bg-green-100 text-green-700"
          : "bg-gray-100 text-gray-500",
        icon: "📊",
        iconColor: "text-purple-500",
      },
    ];
  } catch (e: any) {
    console.error(e);
  } finally {
    loading.value = false;
  }
}

onMounted(refresh);
</script>
