<template>
  <div class="spreadsheet-editor flex flex-col h-full">
    <div class="flex items-center justify-between p-3 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
      <div class="flex items-center gap-2 min-w-0">
        <svg class="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
        <span v-if="!readonly" class="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">Editando: {{ filename }}</span>
        <span v-else class="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">Visualizando: {{ filename }}</span>
      </div>
      <div class="flex items-center gap-2 flex-shrink-0">
        <button @click="$emit('close')" class="btn-secondary text-xs py-1 px-2" title="Fechar">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
    </div>

    <div class="flex-1 overflow-auto">
      <table class="w-full border-collapse text-xs" ref="tableRef">
        <thead>
          <tr class="sticky top-0 z-10">
            <th class="bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 px-2 py-1.5 text-left font-semibold text-gray-500 dark:text-gray-400 w-10 text-center">#</th>
            <th v-for="(col, ci) in localColumns" :key="ci"
              class="bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 px-2 py-1.5 text-left font-semibold text-gray-500 dark:text-gray-400 min-w-24 whitespace-nowrap"
            >
              <input
                :value="col"
                @change="updateColumn(ci, ($event.target as HTMLInputElement).value)"
                :readonly="readonly"
                class="w-full bg-transparent border-none outline-none focus:bg-white dark:focus:bg-gray-600 px-1 rounded font-semibold text-gray-600 dark:text-gray-300"
                :class="{ 'cursor-default': readonly }"
              />
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, ri) in localRows" :key="ri" class="hover:bg-blue-50 dark:hover:bg-blue-900/20">
            <td class="border border-gray-300 dark:border-gray-600 px-2 py-1 text-center text-gray-400 bg-gray-50 dark:bg-gray-800/50 select-none">{{ ri + 1 }}</td>
            <td v-for="(col, ci) in localColumns" :key="ci"
              class="border border-gray-300 dark:border-gray-600 px-0 py-0"
            >
              <input
                :value="row[ci] ?? ''"
                @change="updateCell(ri, ci, ($event.target as HTMLInputElement).value)"
                :readonly="readonly"
                class="w-full h-full px-2 py-1 bg-transparent border-none outline-none min-w-16"
                :class="readonly ? 'cursor-default text-gray-600 dark:text-gray-400' : 'focus:bg-yellow-100 dark:focus:bg-yellow-900/30 focus:ring-1 focus:ring-blue-400'"
                :title="col + ': ' + (row[ci] ?? '')"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="flex items-center justify-between p-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
      <span class="text-xs text-gray-400">{{ localRows.length }} linha(s) &middot; {{ localColumns.length }} coluna(s)</span>
      <div v-if="!readonly" class="flex gap-2">
        <button @click="revert" class="btn-secondary text-xs py-1 px-3" :disabled="!modified">
          <svg class="w-3 h-3 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
          Desfazer
        </button>
        <button @click="save" class="btn-primary text-xs py-1 px-3" :disabled="saving || !modified">
          <svg v-if="saving" class="w-3 h-3 inline mr-1 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
          <svg v-else class="w-3 h-3 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
          Salvar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { apiGet, apiPut } from "@/composables/useApi";
import { useToast } from "@/composables/useToast";

const { success, error: showError } = useToast();

const props = defineProps<{
  filename: string;
  readonly?: boolean;
}>();

const emit = defineEmits<{
  close: [];
  saved: [];
}>();

const localColumns = ref<string[]>([]);
const localRows = ref<string[][]>([]);
const originalColumns = ref<string[]>([]);
const originalRows = ref<string[][]>([]);
const modified = ref(false);
const saving = ref(false);

function updateColumn(ci: number, value: string) {
  if (props.readonly) return;
  localColumns.value[ci] = value;
  modified.value = true;
}

function updateCell(ri: number, ci: number, value: string) {
  if (props.readonly) return;
  localRows.value[ri][ci] = value;
  modified.value = true;
}

function revert() {
  localColumns.value = JSON.parse(JSON.stringify(originalColumns.value));
  localRows.value = JSON.parse(JSON.stringify(originalRows.value));
  modified.value = false;
}

async function load() {
  try {
    const data = await apiGet<any>(`/api/files/${encodeURIComponent(props.filename)}/data`);
    localColumns.value = data.columns || [];
    localRows.value = data.rows || [];
    originalColumns.value = JSON.parse(JSON.stringify(localColumns.value));
    originalRows.value = JSON.parse(JSON.stringify(localRows.value));
    modified.value = false;
  } catch (e: any) {
    showError("Erro ao carregar dados: " + (e.message || ""));
  }
}

async function save() {
  saving.value = true;
  try {
    await apiPut(`/api/files/${encodeURIComponent(props.filename)}/data`, {
      columns: localColumns.value,
      rows: localRows.value,
    });
    originalColumns.value = JSON.parse(JSON.stringify(localColumns.value));
    originalRows.value = JSON.parse(JSON.stringify(localRows.value));
    modified.value = false;
    success("Arquivo salvo com sucesso!");
    emit("saved");
  } catch (e: any) {
    showError("Erro ao salvar: " + (e.message || ""));
  } finally {
    saving.value = false;
  }
}

watch(() => props.filename, () => {
  if (props.filename) load();
}, { immediate: true });
</script>
