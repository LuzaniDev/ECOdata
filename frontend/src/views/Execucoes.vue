<template>
  <Layout>
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Execuções</h2>
        <button @click="load" class="btn-secondary text-sm">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
          Atualizar
        </button>
      </div>

      <div class="flex flex-wrap gap-3 items-center">
        <select v-model="filtroTipo" @change="load" class="input w-auto text-sm">
          <option value="">Todos os tipos</option>
          <option value="sellout">Sellout</option>
          <option value="estoque">Estoque</option>
          <option value="painel">Painel</option>
        </select>
        <select v-model="filtroStatus" @change="load" class="input w-auto text-sm">
          <option value="">Todos os status</option>
          <option value="success">Sucesso</option>
          <option value="failed">Falha</option>
          <option value="warning">Alerta</option>
          <option value="running">Executando</option>
        </select>
        <span class="text-sm text-gray-500">{{ total }} resultados</span>
      </div>

      <LoadingSpinner v-if="loading" />

      <div class="card overflow-hidden" v-else-if="items.length">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th class="text-left p-3">Tipo</th>
              <th class="text-left p-3">Status</th>
              <th class="text-left p-3">Arquivo</th>
              <th class="text-left p-3">Início</th>
              <th class="text-left p-3">Duração</th>
              <th class="text-left p-3">Ações</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
            <tr v-for="e in items" :key="e.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/30">
              <td class="p-3">
                <span class="badge-info text-xs">{{ e.tipo }}</span>
              </td>
              <td class="p-3">
                <span :class="statusClass(e.status)">{{ statusLabel(e.status) }}</span>
              </td>
              <td class="p-3 text-xs font-mono truncate max-w-40">
                <button v-if="e.file_path" @click="baixarArquivo(e.file_path.split('\\').pop())" class="text-primary-600 hover:underline text-left" title="Download">
                  {{ e.file_path.split('\\').pop() }}
                </button>
                <span v-else class="text-gray-400">-</span>
              </td>
              <td class="p-3 text-xs text-gray-500">{{ formatDate(e.started_at) }}</td>
              <td class="p-3 text-xs text-gray-500">{{ formatDuration(e.duration_ms) }}</td>
              <td class="p-3">
                <button @click="verDetalhes(e)" class="btn-secondary text-xs py-1 px-2">Detalhes</button>
                <button v-if="e.status === 'running'" @click="cancelar(e.id)" class="btn-danger text-xs py-1 px-2 ml-1">Cancelar</button>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="flex items-center justify-between p-3 border-t border-gray-200 dark:border-gray-700">
          <button :disabled="page <= 1" @click="page--; load()" class="btn-secondary text-xs py-1 px-2">Anterior</button>
          <span class="text-xs text-gray-500">Página {{ page }} de {{ totalPages }}</span>
          <button :disabled="page >= totalPages" @click="page++; load()" class="btn-secondary text-xs py-1 px-2">Próxima</button>
        </div>
      </div>

      <p v-else class="text-center py-12 text-gray-400">Nenhuma execução encontrada</p>

      <div v-if="detalhes.show" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="detalhes.show = false">
        <div class="card p-6 w-full max-w-2xl mx-4 max-h-[80vh] overflow-y-auto space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-bold">Detalhes da Execução</h3>
            <button @click="detalhes.show = false" class="text-gray-400 hover:text-gray-600 text-xl">&times;</button>
          </div>
          <div class="grid grid-cols-2 gap-3 text-sm">
            <div><span class="text-gray-500">ID:</span> {{ detalhes.item.id }}</div>
            <div><span class="text-gray-500">Tipo:</span> {{ detalhes.item.tipo }}</div>
            <div><span class="text-gray-500">Status:</span> <span :class="statusClass(detalhes.item.status)">{{ detalhes.item.status }}</span></div>
            <div><span class="text-gray-500">Duração:</span> {{ formatDuration(detalhes.item.duration_ms) }}</div>
            <div><span class="text-gray-500">Início:</span> {{ formatDate(detalhes.item.started_at) }}</div>
            <div><span class="text-gray-500">Fim:</span> {{ formatDate(detalhes.item.finished_at) }}</div>
            <div class="col-span-2" v-if="detalhes.item.file_path">
              <span class="text-gray-500">Arquivo:</span>
              <button @click="baixarArquivo(detalhes.item.file_path.split('\\').pop())" class="text-primary-600 hover:underline text-xs font-mono ml-1 text-left">{{ detalhes.item.file_path.split('\\').pop() }}</button>
            </div>
            <div class="col-span-2" v-if="detalhes.item.file_size">
              <span class="text-gray-500">Tamanho:</span> {{ formatBytes(detalhes.item.file_size) }}
            </div>
            <div class="col-span-2" v-if="detalhes.item.rows_count">
              <span class="text-gray-500">Linhas:</span> {{ detalhes.item.rows_count }}
            </div>
          </div>
          <div v-if="detalhes.item.empresa_utilizada" class="col-span-2">
            <span class="text-gray-500">Empresa:</span>
            <span class="ml-1">{{ detalhes.item.empresa_nome || detalhes.item.empresa_utilizada }}</span>
          </div>
          <div v-if="detalhes.item.available_companies && detalhes.item.available_companies.length" class="col-span-2">
            <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700 rounded-lg p-4 space-y-2">
              <div class="flex items-center gap-2 text-amber-700 dark:text-amber-400 font-medium text-sm">
                <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"/></svg>
                Nenhum dado encontrado na empresa <strong>{{ detalhes.item.empresa_utilizada }}</strong>
              </div>
              <p class="text-xs text-amber-600 dark:text-amber-500">Empresas com dados de venda disponíveis:</p>
              <div class="space-y-1.5">
                <div v-for="emp in detalhes.item.available_companies" :key="emp.codigo"
                  class="flex items-center justify-between bg-white dark:bg-amber-900/40 rounded-md px-3 py-2 text-sm border border-amber-100 dark:border-amber-800"
                >
                  <div class="flex items-center gap-2 min-w-0">
                    <span class="font-mono text-xs font-medium text-gray-700 dark:text-gray-300">{{ emp.codigo }}</span>
                    <span class="text-gray-500 dark:text-gray-400 truncate">{{ emp.nome }}</span>
                  </div>
                  <button @click="executarComEmpresa(emp.codigo)" class="btn-primary text-xs py-1 px-2.5 flex-shrink-0" :disabled="executandoEmpresa === emp.codigo">
                    <svg v-if="executandoEmpresa === emp.codigo" class="w-3 h-3 animate-spin inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                    Executar
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div v-if="detalhes.item.error_message" class="bg-red-50 dark:bg-red-900/20 p-3 rounded text-sm text-red-700 dark:text-red-400 font-mono whitespace-pre-wrap">
            {{ detalhes.item.error_message }}
          </div>
          <div v-if="detalhes.item.output_log" class="bg-gray-50 dark:bg-gray-900 p-3 rounded text-xs font-mono whitespace-pre-wrap max-h-40 overflow-y-auto">
            {{ detalhes.item.output_log }}
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import Layout from "@/components/Layout.vue";
import LoadingSpinner from "@/components/LoadingSpinner.vue";
import { apiGet, apiPost, downloadFile } from "@/composables/useApi";
import { useToast } from "@/composables/useToast";

const { success, error: showError } = useToast();

const loading = ref(true);
const items = ref<any[]>([]);
const total = ref(0);
const page = ref(1);
const perPage = 10;
const filtroTipo = ref("");
const filtroStatus = ref("");
const detalhes = ref({ show: false, item: {} as any });

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / perPage)));

function statusClass(s: string) {
  return {
    success: "badge-success",
    failed: "badge-error",
    running: "badge-warning",
    warning: "badge-warning",
    cancelled: "badge-error",
  }[s] || "badge-info";
}

function statusLabel(s: string) {
  return {
    success: "Sucesso",
    failed: "Falha",
    running: "Executando",
    warning: "Alerta",
    cancelled: "Cancelado",
  }[s] || s;
}

function formatDate(d: string) {
  if (!d) return "-";
  return new Date(d).toLocaleString("pt-BR");
}

function formatDuration(ms: number) {
  if (!ms) return "-";
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

function formatBytes(bytes: number) {
  if (!bytes) return "-";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

async function load() {
  loading.value = true;
  try {
    const params: Record<string, any> = { page: page.value, per_page: perPage };
    if (filtroTipo.value) params.tipo = filtroTipo.value;
    if (filtroStatus.value) params.status = filtroStatus.value;
    const data: any = await apiGet("/api/auditoria", params);
    items.value = data.items || [];
    total.value = data.total || 0;
  } catch (e: any) {
    showError("Erro ao carregar execuções");
  } finally {
    loading.value = false;
  }
}

async function verDetalhes(e: any) {
  try {
    const data: any = await apiGet(`/api/auditoria/${e.id}`);
    detalhes.value = { show: true, item: data };
  } catch {
    showError("Erro ao carregar detalhes");
  }
}

const executandoEmpresa = ref("");

async function executarComEmpresa(codigo: string) {
  executandoEmpresa.value = codigo;
  try {
    const data = await apiPost<any>(`/api/scheduler/run-tipo?tipo=sellout&empresa=${codigo}&send_sftp=false`);
    success(`Executado sellout com empresa ${codigo}`);
    detalhes.value.show = false;
    await load();
  } catch (e: any) {
    showError(e?.message || "Erro ao executar");
  } finally {
    executandoEmpresa.value = "";
  }
}

async function baixarArquivo(name: string) {
  try {
    await downloadFile(`/api/files/download/${name}`, name);
  } catch (e: any) {
    showError("Erro ao baixar arquivo");
  }
}

async function cancelar(id: number) {
  if (!confirm("Cancelar esta execução?")) return;
  try {
    await apiPost(`/api/auditoria/${id}/cancel`);
    success("Execução cancelada");
    await load();
  } catch (e: any) {
    showError(e?.message || "Erro ao cancelar");
  }
}

onMounted(load);
</script>
