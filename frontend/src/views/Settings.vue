<template>
  <Layout>
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Configurações</h2>
        <button @click="salvar" :disabled="salvando" class="btn-primary text-sm">
          <svg v-if="salvando" class="w-4 h-4 animate-spin inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
          Salvar
        </button>
      </div>

      <LoadingSpinner v-if="loading" />

      <div v-else-if="mensagem" class="px-4 py-3 rounded-lg text-sm" :class="mensagemTipo === 'erro' ? 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400' : 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400'">
        {{ mensagem }}
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="card">
          <div class="p-4 border-b border-gray-200 dark:border-gray-700">
            <h3 class="font-semibold text-gray-900 dark:text-gray-100">Banco de Dados</h3>
          </div>
          <div class="p-4 space-y-3">
            <label class="block">
              <span class="text-xs text-gray-500">Host</span>
              <input v-model="form.DB_HOST" class="input w-full text-sm mt-0.5" placeholder="localhost" />
            </label>
            <label class="block">
              <span class="text-xs text-gray-500">Caminho do Banco</span>
              <input v-model="form.DB_PATH" class="input w-full text-sm mt-0.5" placeholder="C:\Ecosis\dados\ECODADOS.ECO" />
            </label>
            <label class="block">
              <span class="text-xs text-gray-500">Usuário</span>
              <input v-model="form.DB_USER" class="input w-full text-sm mt-0.5" placeholder="SYSDBA" />
            </label>
            <label class="block">
              <span class="text-xs text-gray-500">Senha</span>
              <input v-model="form.DB_PASSWORD" type="password" class="input w-full text-sm mt-0.5" placeholder="Senha do Firebird" />
            </label>
            <button @click="testarConexao" :disabled="testando" class="btn-secondary text-xs mt-1">
              <svg v-if="testando" class="w-3 h-3 animate-spin inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
              Testar Conexão
            </button>
          </div>
        </div>

        <div class="card">
          <div class="p-4 border-b border-gray-200 dark:border-gray-700">
            <h3 class="font-semibold text-gray-900 dark:text-gray-100">Empresa</h3>
          </div>
          <div class="p-4 space-y-3">
            <label class="block">
              <span class="text-xs text-gray-500">Código da Empresa</span>
              <input v-model="form.CODIGO_EMPRESA" class="input w-full text-sm mt-0.5" placeholder="01" />
              <span class="text-xxs text-gray-400">Use 02 para EXTENSA SINOP (82877 pedidos)</span>
            </label>
            <label class="block">
              <span class="text-xs text-gray-500">CNPJ do Distribuidor</span>
              <input v-model="form.CNPJ_DISTRIBUIDOR" class="input w-full text-sm mt-0.5" placeholder="Opcional" />
            </label>
          </div>
        </div>

        <div class="card md:col-span-2">
          <div class="p-4 border-b border-gray-200 dark:border-gray-700">
            <h3 class="font-semibold text-gray-900 dark:text-gray-100">SFTP</h3>
          </div>
          <div class="p-4 grid grid-cols-1 md:grid-cols-2 gap-3">
            <label class="block">
              <span class="text-xs text-gray-500">Host</span>
              <input v-model="form.SFTP_HOST" class="input w-full text-sm mt-0.5" placeholder="ex: sftp.exemplo.com" />
            </label>
            <label class="block">
              <span class="text-xs text-gray-500">Porta</span>
              <input v-model="form.SFTP_PORT" class="input w-full text-sm mt-0.5" placeholder="2222" />
            </label>
            <label class="block">
              <span class="text-xs text-gray-500">Usuário</span>
              <input v-model="form.SFTP_USER" class="input w-full text-sm mt-0.5" />
            </label>
            <label class="block">
              <span class="text-xs text-gray-500">Senha</span>
              <input v-model="form.SFTP_PASSWORD" type="password" class="input w-full text-sm mt-0.5" />
            </label>
            <label class="block md:col-span-2">
              <span class="text-xs text-gray-500">Diretório Remoto</span>
              <input v-model="form.SFTP_REMOTE_DIR" class="input w-full text-sm mt-0.5" placeholder="/" />
            </label>
            <button @click="testarSFTP" :disabled="testandoSFTP" class="btn-secondary text-xs">
              <svg v-if="testandoSFTP" class="w-3 h-3 animate-spin inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
              Testar SFTP
            </button>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from "vue";
import Layout from "@/components/Layout.vue";
import LoadingSpinner from "@/components/LoadingSpinner.vue";
import { apiGet, apiPost, apiPut } from "@/composables/useApi";

const loading = ref(true);
const salvando = ref(false);
const testando = ref(false);
const testandoSFTP = ref(false);
const mensagem = ref("");
const mensagemTipo = ref("");

const form = reactive({
  DB_HOST: "",
  DB_PATH: "",
  DB_USER: "",
  DB_PASSWORD: "",
  CODIGO_EMPRESA: "01",
  CNPJ_DISTRIBUIDOR: "",
  SFTP_HOST: "",
  SFTP_PORT: "2222",
  SFTP_USER: "",
  SFTP_PASSWORD: "",
  SFTP_REMOTE_DIR: "/",
});

async function carregar() {
  try {
    const data = await apiGet("/api/config/env");
    Object.assign(form, data);
  } catch {
    mensagem.value = "Erro ao carregar configurações";
    mensagemTipo.value = "erro";
  } finally {
    loading.value = false;
  }
}

async function salvar() {
  salvando.value = true;
  mensagem.value = "";
  try {
    await apiPut("/api/config/env", form);
    mensagem.value = "Configurações salvas com sucesso! Reinicie o servidor para aplicar.";
    mensagemTipo.value = "sucesso";
  } catch (e: any) {
    mensagem.value = e.message || "Erro ao salvar";
    mensagemTipo.value = "erro";
  } finally {
    salvando.value = false;
  }
}

async function testarConexao() {
  testando.value = true;
  mensagem.value = "";
  try {
    const data = await apiPost("/api/config/test-db", {
      host: form.DB_HOST,
      path: form.DB_PATH,
      user: form.DB_USER,
      password: form.DB_PASSWORD,
    });
    mensagem.value = data.status === "ok" ? "Conexão OK!" : "Falha: " + (data.error || "Erro desconhecido");
    mensagemTipo.value = data.status === "ok" ? "sucesso" : "erro";
  } catch {
    mensagem.value = "Erro ao testar conexão";
    mensagemTipo.value = "erro";
  } finally {
    testando.value = false;
  }
}

async function testarSFTP() {
  testandoSFTP.value = true;
  mensagem.value = "";
  try {
    const data = await apiPost("/api/config/test-sftp", {
      host: form.SFTP_HOST,
      port: parseInt(form.SFTP_PORT) || 2222,
      user: form.SFTP_USER,
      password: form.SFTP_PASSWORD,
    });
    mensagem.value = data.status === "ok" ? "SFTP OK!" : "Falha: " + (data.error || "Erro desconhecido");
    mensagemTipo.value = data.status === "ok" ? "sucesso" : "erro";
  } catch {
    mensagem.value = "Erro ao testar SFTP";
    mensagemTipo.value = "erro";
  } finally {
    testandoSFTP.value = false;
  }
}

onMounted(carregar);
</script>