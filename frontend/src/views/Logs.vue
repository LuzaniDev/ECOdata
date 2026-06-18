<template>
  <Layout>
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Logs</h2>
        <div class="flex items-center gap-2">
          <select v-model="filtroTipo" class="input w-auto text-sm">
            <option value="">Todos os tipos</option>
            <option value="api_request">Requisições</option>
            <option value="api_response">Respostas</option>
            <option value="db_query">Queries DB</option>
            <option value="generator_step">Generator</option>
            <option value="scheduler_cycle">Scheduler</option>
            <option value="error">Erros</option>
            <option value="info">Info</option>
          </select>
          <button @click="load" class="btn-secondary text-sm">Atualizar</button>
        </div>
      </div>

      <div class="flex items-center gap-4 text-xs text-gray-500">
        <span>{{ logs.length }} eventos de sistema</span>
        <span>{{ debugEvents.length }} eventos de depuração</span>
        <label class="flex items-center gap-1 cursor-pointer">
          <input type="checkbox" v-model="mostrarDebug" class="rounded" />
          <span>Mostrar debug</span>
        </label>
        <label class="flex items-center gap-1 cursor-pointer">
          <input type="checkbox" v-model="autoRefresh" class="rounded" />
          <span>Auto-refresh</span>
        </label>
      </div>

      <LoadingSpinner v-if="loading" />

      <div class="card overflow-hidden" v-else-if="itens.length">
        <div class="font-mono text-xs">
          <div v-for="item in itens" :key="item.id"
            class="flex items-start px-3 py-2 border-b border-gray-100 dark:border-gray-700/50 last:border-0 hover:bg-gray-50 dark:hover:bg-gray-700/20"
            :class="itemBgClass(item)"
          >
            <span class="text-gray-400 w-16 flex-shrink-0">{{ formatTime(item) }}</span>
            <span class="w-[18px] text-center flex-shrink-0">{{ itemIcon(item) }}</span>
            <span :class="itemTextClass(item)" class="w-24 flex-shrink-0 font-bold uppercase truncate">{{ item.level || item.type }}</span>
            <span class="text-gray-500 w-20 flex-shrink-0 truncate">{{ item.source || "" }}</span>
            <span v-if="item.duration_ms !== undefined" class="text-gray-400 w-14 flex-shrink-0 text-right">{{ item.duration_ms }}ms</span>
            <span class="text-gray-700 dark:text-gray-300 break-all flex-1">{{ item.message }}</span>
          </div>
        </div>
      </div>

      <p v-else class="text-center py-12 text-gray-400">Nenhum evento encontrado</p>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from "vue";
import Layout from "@/components/Layout.vue";
import LoadingSpinner from "@/components/LoadingSpinner.vue";

const loading = ref(true);
const logs = ref<any[]>([]);
const debugEvents = ref<any[]>([]);
const filtroTipo = ref("");
const autoRefresh = ref(true);
const mostrarDebug = ref(false);
let intervalId: ReturnType<typeof setInterval> | null = null;

const itens = computed(() => {
  let items = logs.value.map((l: any) => ({ ...l, _tipo: "log" }));
  if (mostrarDebug.value) {
    const deb = debugEvents.value.map((e: any) => ({
      id: "d" + e.id,
      level: e.type,
      type: e.type,
      source: e.source,
      created_at: e.timestamp,
      message: eSummary(e),
      duration_ms: e.data?.duration_ms,
      _tipo: "debug",
    }));
    items = [...items, ...deb];
  }
  if (filtroTipo.value) {
    items = items.filter(i => (i.level || i.type) === filtroTipo.value);
  }
  items.sort((a, b) => new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime());
  return items.slice(0, 500);
});

function eSummary(ev: any) {
  const d = ev.data || {};
  switch (ev.type) {
    case "api_request": return `${d.method} ${d.path}`;
    case "api_response": return `${d.status} ${d.path} (${d.duration_ms}ms)`;
    case "db_query": return (d.sql || "").substring(0, 120);
    case "generator_step": return `${d.step}${d.tipo ? " [" + d.tipo + "]" : ""}`;
    case "scheduler_cycle": return d.action || "";
    case "error": return d.message || "";
    default: return d.message || "";
  }
}

function itemIcon(item: any) {
  const icons: Record<string, string> = {
    api_request: "→", api_response: "←", db_query: "🗄",
    generator_step: "⚙", scheduler_cycle: "⏰", error: "✖",
    INFO: "ℹ", WARNING: "⚠", ERROR: "✖", SUCCESS: "✓",
  };
  return icons[item.level || item.type] || "•";
}

function itemTextClass(item: any) {
  const t = item.level || item.type;
  if (t === "ERROR" || t === "error") return "text-red-500";
  if (t === "WARNING") return "text-yellow-500";
  if (t === "SUCCESS" || t === "generator_step") return "text-green-600";
  if (t === "api_request") return "text-blue-500";
  if (t === "api_response") return "text-teal-500";
  if (t === "db_query") return "text-purple-500";
  if (t === "scheduler_cycle") return "text-orange-500";
  if (t === "INFO") return "text-blue-600";
  return "text-gray-600";
}

function itemBgClass(item: any) {
  const t = item.level || item.type;
  return t === "ERROR" || t === "error" ? "bg-red-50 dark:bg-red-900/10" : "";
}

function formatTime(item: any) {
  const ts = item.created_at || item.timestamp;
  if (!ts) return "--:--:--";
  try { return new Date(ts).toLocaleTimeString("pt-BR"); } catch { return ts; }
}

async function load() {
  loading.value = true;
  try {
    const [logData, debugData] = await Promise.all([
      fetch(`/api/logs?limit=200${filtroTipo.value ? "&level=" + filtroTipo.value : ""}`).then(r => r.json()).catch(() => ({ items: [] })),
      mostrarDebug.value ? fetch("/api/debug/events?limit=200").then(r => r.json()).catch(() => ({ events: [] })) : { events: [] },
    ]);
    logs.value = logData.items || [];
    debugEvents.value = debugData.events || [];
  } catch {}
  loading.value = false;
}

onMounted(() => {
  load();
  intervalId = setInterval(() => {
    if (autoRefresh.value) load();
  }, 10000);
});

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId);
});
</script>