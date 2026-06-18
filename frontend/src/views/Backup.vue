<template>
  <Layout>
    <div class="space-y-4">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Backup</h2>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="card p-6">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 dark:text-gray-100">Banco de Dados</h3>
              <p class="text-xs text-gray-500">Faça download do banco SQLite completo</p>
            </div>
          </div>
          <a href="/api/backup/download" class="btn-primary text-sm w-full justify-center" download>
            Baixar Backup (.db)
          </a>
        </div>

        <div class="card p-6">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center text-green-600">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"/></svg>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 dark:text-gray-100">Arquivos Gerados</h3>
              <p class="text-xs text-gray-500">Acesse a pasta de arquivos gerados</p>
            </div>
          </div>
          <router-link to="/files" class="btn-secondary text-sm w-full justify-center">
            Ver Arquivos
          </router-link>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import Layout from "@/components/Layout.vue";
</script>
