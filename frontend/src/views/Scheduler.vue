<template>
  <Layout>
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-2xl font-bold">Agendamentos</h2>
        <button @click="showForm = true" class="btn-primary">Novo Agendamento</button>
      </div>

      <div class="flex gap-2">
        <input v-model="search" class="input max-w-xs" placeholder="Buscar..." />
        <button @click="load" class="btn-secondary">Filtrar</button>
      </div>

      <div v-if="loading" class="text-center py-4">Carregando...</div>
      <div v-else-if="error" class="text-red-500 text-center py-4">{{ error }}</div>

      <div class="card overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th class="text-left p-3">Nome</th>
              <th class="text-left p-3">Tipo</th>
              <th class="text-left p-3">Cron</th>
              <th class="text-left p-3">SFTP</th>
              <th class="text-left p-3">Status</th>
              <th class="text-left p-3">Última Execução</th>
              <th class="text-left p-3">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in schedules" :key="s.id" class="border-t border-gray-200 dark:border-gray-700">
              <td class="p-3">{{ s.name }}</td>
              <td class="p-3"><span class="badge-info">{{ s.tipo }}</span></td>
              <td class="p-3 font-mono text-xs">{{ s.cron_expression || '-' }}</td>
              <td class="p-3">{{ s.send_sftp ? 'Sim' : 'Não' }}</td>
              <td class="p-3">
                <span :class="s.enabled ? 'badge-success' : 'badge-error'">{{ s.enabled ? 'Ativo' : 'Inativo' }}</span>
              </td>
              <td class="p-3 text-xs">{{ s.last_run ? new Date(s.last_run).toLocaleString() : '-' }}</td>
              <td class="p-3 flex gap-1">
                <button @click="toggle(s.id)" class="btn-secondary text-xs py-1 px-2">{{ s.enabled ? 'Desativar' : 'Ativar' }}</button>
                <button @click="runNow(s.id)" :disabled="runningId === s.id" class="btn-primary text-xs py-1 px-2 disabled:opacity-50">
                  {{ runningId === s.id ? 'Executando...' : 'Executar' }}
                </button>
                <button @click="confirmDelete(s.id)" class="btn-danger text-xs py-1 px-2">Excluir</button>
              </td>
            </tr>
            <tr v-if="!schedules.length"><td colspan="7" class="p-6 text-center text-gray-500">Nenhum agendamento</td></tr>
          </tbody>
        </table>
      </div>

      <div v-if="showResult" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showResult = false">
        <div class="card p-6 w-full max-w-lg mx-4">
          <h3 class="text-lg font-bold mb-4">Resultado da Execução</h3>
          <div :class="resultStatus === 'success' ? 'text-green-600' : resultStatus === 'warning' ? 'text-yellow-600' : 'text-red-600'" class="mb-4">
            Status: {{ resultStatus }}
          </div>
          <div v-if="resultMessage" class="text-sm text-gray-600 mb-4">{{ resultMessage }}</div>
          <button @click="showResult = false" class="btn-primary">Fechar</button>
        </div>
      </div>

      <div v-if="showForm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showForm = false">
        <div class="card p-6 w-full max-w-lg mx-4 space-y-4">
          <h3 class="text-lg font-bold">Novo Agendamento</h3>
          <div><label class="block text-sm font-medium mb-1">Nome</label><input v-model="form.name" class="input" required /></div>
          <div><label class="block text-sm font-medium mb-1">Tipo</label>
            <select v-model="form.tipo" class="select">
              <option value="sellout">SELLOUT</option>
              <option value="estoque">ESTOQUE</option>
              <option value="painel">PAINEL</option>
            </select>
          </div>
          <div><label class="block text-sm font-medium mb-1">Expressão Cron</label><input v-model="form.cron_expression" class="input" placeholder="0 6 * * *" /></div>
          <div class="flex items-center gap-2"><input v-model="form.send_sftp" type="checkbox" id="sftp" /><label for="sftp">Enviar SFTP</label></div>
          <div class="flex gap-2 justify-end">
            <button @click="showForm = false" class="btn-secondary">Cancelar</button>
            <button @click="create" class="btn-primary">Salvar</button>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import Layout from "@/components/Layout.vue";
import { apiGet, apiPost, apiDelete } from "@/composables/useApi";

const schedules = ref<any[]>([]);
const search = ref("");
const showForm = ref(false);
const loading = ref(false);
const error = ref(null);
const runningId = ref<number | null>(null);
const showResult = ref(false);
const resultStatus = ref("");
const resultMessage = ref("");

const form = ref({ name: "", tipo: "sellout", cron_expression: "", send_sftp: true });

async function load() {
  loading.value = true;
  error.value = null;
  try {
    schedules.value = await apiGet("/api/scheduler", { search: search.value || undefined });
  } catch (e: any) {
    error.value = e?.message || String(e);
  } finally {
    loading.value = false;
  }
}

async function toggle(id: number) {
  try {
    await apiPost(`/api/scheduler/${id}/toggle`);
    await load();
  } catch (e: any) {
    alert("Erro: " + (e?.message || String(e)));
  }
}

async function runNow(id: number) {
  runningId.value = id;
  resultStatus.value = "";
  resultMessage.value = "";
  try {
    const response: any = await apiPost(`/api/scheduler/${id}/run`);
    resultStatus.value = response.status || "unknown";
    resultMessage.value = response.message || "";
    showResult.value = true;
    await load();
  } catch (e: any) {
    resultStatus.value = "error";
    resultMessage.value = e?.message || String(e);
    showResult.value = true;
  } finally {
    runningId.value = null;
  }
}

async function create() {
  try {
    await apiPost("/api/scheduler", form.value);
    showForm.value = false;
    await load();
  } catch (e: any) {
    alert("Erro: " + (e?.message || String(e)));
  }
}

async function confirmDelete(id: number) {
  if (confirm("Excluir agendamento?")) {
    try {
      await apiDelete(`/api/scheduler/${id}`);
      await load();
    } catch (e: any) {
      alert("Erro: " + (e?.message || String(e)));
    }
  }
}

onMounted(load);
</script>