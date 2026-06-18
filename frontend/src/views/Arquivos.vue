<template>
  <Layout>
    <div class="flex gap-0" style="height: calc(100vh - 5rem);">
      <div class="flex-1 min-w-0 overflow-auto p-6">
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Arquivos</h2>
            <button @click="load" class="btn-secondary text-sm">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
              Atualizar
            </button>
          </div>

          <LoadingSpinner v-if="loading" />

          <div class="card overflow-hidden" v-else-if="files.length">
            <table class="w-full text-sm">
              <thead class="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th class="text-left p-3">Nome</th>
                  <th class="text-left p-3">Tamanho</th>
                  <th class="text-left p-3">Modificado</th>
                  <th class="text-left p-3">Ações</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
                <tr v-for="f in files" :key="f.name"
                  class="hover:bg-gray-50 dark:hover:bg-gray-700/30"
                  :class="{ 'bg-primary-50 dark:bg-primary-900/20': editingFile === f.name }"
                >
                  <td class="p-3 font-mono text-xs">{{ f.name }}</td>
                  <td class="p-3 text-xs text-gray-500">{{ formatBytes(f.size) }}</td>
                  <td class="p-3 text-xs text-gray-500">{{ formatDate(f.modified) }}</td>
                  <td class="p-3 flex gap-1">
                    <a :href="'/api/files/download/' + f.name" class="btn-primary text-xs py-1 px-2 inline-flex items-center gap-1" download>
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
                      Download
                    </a>
                    <button @click="visualizarArquivo(f.name)" class="btn-secondary text-xs py-1 px-2 inline-flex items-center gap-1">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                      Visualizar
                    </button>
                    <button @click="editarArquivo(f.name)" class="btn-secondary text-xs py-1 px-2 inline-flex items-center gap-1">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                      Editar
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
            <div class="p-3 border-t border-gray-200 dark:border-gray-700 text-xs text-gray-400 text-center">
              {{ files.length }} arquivo(s) encontrado(s)
            </div>
          </div>

          <div v-else class="card p-8 text-center">
            <p class="text-gray-400 mb-2">Nenhum arquivo gerado</p>
            <p class="text-sm text-gray-500">Execute um agendamento para gerar arquivos</p>
          </div>
        </div>
      </div>

      <Transition name="slide">
        <div v-if="editingFile" class="w-[60vw] min-w-[500px] max-w-[1000px] border-l border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex flex-col overflow-hidden" style="height: 100%;">
          <SpreadsheetEditor :filename="editingFile" :readonly="previewMode" @close="editingFile = ''" @saved="onSaved" />
        </div>
      </Transition>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import Layout from "@/components/Layout.vue";
import LoadingSpinner from "@/components/LoadingSpinner.vue";
import SpreadsheetEditor from "@/components/SpreadsheetEditor.vue";
import { apiGet } from "@/composables/useApi";

const loading = ref(true);
const files = ref<any[]>([]);
const editingFile = ref("");
const previewMode = ref(false);

function formatBytes(bytes: number) {
  if (!bytes) return "-";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(timestamp: number) {
  if (!timestamp) return "-";
  return new Date(timestamp * 1000).toLocaleString("pt-BR");
}

function visualizarArquivo(name: string) {
  previewMode.value = true;
  editingFile.value = name;
}

function editarArquivo(name: string) {
  previewMode.value = false;
  editingFile.value = editingFile.value === name ? "" : name;
}

function onSaved() {
  load();
}

async function load() {
  loading.value = true;
  try {
    const data: any = await apiGet("/api/files");
    files.value = data.items || [];
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<style scoped>
.slide-enter-active, .slide-leave-active {
  transition: all 0.2s ease-out;
}
.slide-enter-from, .slide-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>
