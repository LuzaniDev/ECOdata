<template>
  <div class="flex h-screen bg-gray-50 dark:bg-gray-900">
    <aside class="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col flex-shrink-0">
      <div class="p-5 border-b border-gray-200 dark:border-gray-700">
        <h1 class="text-xl font-bold text-primary-600">ECOdata</h1>
        <p class="text-xs text-gray-400 mt-0.5">Tradefy Integration</p>
      </div>
      <nav class="flex-1 p-3 space-y-1 overflow-y-auto">
        <router-link
          v-for="item in nav"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all"
          :class="
            $route.path === item.path
              ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 font-semibold shadow-sm'
              : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700/50 hover:text-gray-900 dark:hover:text-gray-200'
          "
        >
          <span v-html="item.icon" class="w-5 h-5 flex items-center justify-center"></span>
          {{ item.label }}
        </router-link>
      </nav>
    </aside>
    <main class="flex-1 overflow-auto">
      <div class="p-6 max-w-7xl mx-auto">
        <slot />
      </div>
    </main>
    <Toast />

    <!-- Dark mode toggle -->
    <button
      @click="toggleDark"
      class="fixed bottom-3 left-3 z-[10000] w-8 h-8 rounded-full flex items-center justify-center shadow-md transition-all text-xs bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 text-gray-600 dark:text-yellow-400"
      :title="isDark ? 'Modo claro' : 'Modo escuro'"
    >
      <svg v-if="isDark" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
      <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>
    </button>

    <!-- Botao debug -->
    <button
      @click="toggleDebug"
      class="fixed bottom-3 right-3 z-[10000] w-8 h-8 rounded-full flex items-center justify-center shadow-md transition-all text-xs"
      :class="logado ? 'bg-blue-500 hover:bg-blue-600 text-white' : 'bg-gray-300 dark:bg-gray-600 hover:bg-gray-400 dark:hover:bg-gray-500 text-gray-500 dark:text-gray-300'"
      title="Logs de depuração"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
    </button>

    <!-- Painel debug recolhido -->
    <div v-if="mostrar && !expandido"
      class="fixed bottom-14 right-3 z-[10000] bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-2xl flex flex-col"
      :style="{ width: pw + 'px', height: ph + 'px' }"
    >
      <!-- header -->
      <div class="flex items-center justify-between px-3 py-2 border-b border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-700 flex-shrink-0 rounded-t-lg">
        <span class="font-semibold text-gray-600 dark:text-gray-300 text-xs flex items-center gap-1.5">
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
          Debug Logs
          <span class="text-gray-400 font-normal">({{ eventos.length }})</span>
        </span>
        <div class="flex items-center gap-0.5">
          <button @click="abrirJanela" class="text-gray-400 hover:text-blue-500 px-1.5 py-0.5 rounded text-xxs hover:bg-gray-200 dark:hover:bg-gray-600" title="Abrir em janela separada">Janela</button>
          <button @click="expandido = true" class="text-gray-400 hover:text-blue-500 px-1.5 py-0.5 rounded text-xxs hover:bg-gray-200 dark:hover:bg-gray-600" title="Expandir">Maximizar</button>
          <button @click="mostrar = false" class="text-gray-400 hover:text-gray-600 font-bold ml-1 px-1">&times;</button>
        </div>
      </div>
      <!-- conteudo -->
      <div class="flex-1 overflow-hidden flex flex-col">
        <div v-if="!logado" class="p-3 space-y-2">
          <p class="text-gray-500 text-xs">Login para ver debug logs:</p>
          <input v-model="loginUser" type="text" placeholder="Usuário" class="input w-full text-xs px-2 py-1.5" @keyup.enter="fazerLogin" />
          <input v-model="loginPass" type="password" placeholder="Senha" class="input w-full text-xs px-2 py-1.5" @keyup.enter="fazerLogin" />
          <p v-if="loginErro" class="text-red-500 text-xxs">{{ loginErro }}</p>
          <button @click="fazerLogin" class="btn-primary w-full text-xs py-1.5">Entrar</button>
        </div>
        <template v-else>
          <!-- filtros -->
          <div class="flex items-center gap-1 px-2 py-1 border-b border-gray-100 dark:border-gray-700/50 bg-gray-50/50 dark:bg-gray-800/50 flex-shrink-0">
            <select v-model="filtroTipo" class="text-xxs bg-transparent border border-gray-200 dark:border-gray-600 rounded px-1 py-0.5 text-gray-500 outline-none">
              <option value="">Todos</option>
              <option value="api_request">Requisição</option>
              <option value="api_response">Resposta</option>
              <option value="db_query">Query DB</option>
              <option value="generator_step">Generator</option>
              <option value="scheduler_cycle">Scheduler</option>
              <option value="error">Erro</option>
            </select>
            <input v-model="buscaTexto" placeholder="Buscar..." class="text-xxs bg-transparent border border-gray-200 dark:border-gray-600 rounded px-1 py-0.5 text-gray-500 outline-none flex-1 min-w-0" />
            <button @click="limparEventos" class="text-gray-400 hover:text-red-500 text-xxs px-1">&times;</button>
          </div>
          <!-- lista -->
          <div class="flex-1 overflow-y-auto font-mono debug-scroll" ref="listaRef">
            <div v-if="!itensFiltrados.length" class="text-gray-400 text-center py-6 text-xxs">Nenhum evento</div>
            <div v-for="ev in itensFiltrados" :key="ev.id" class="mb-px">
              <div class="flex items-start gap-1 px-2 py-0.5 rounded cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700/50"
                :class="[sel.has(ev.id) ? 'ring-1 ring-blue-400' : '', ev.type === 'error' ? 'bg-red-50 dark:bg-red-900/10' : '']"
                @click="altExpand(ev.id)"
              >
                <input type="checkbox" :checked="sel.has(ev.id)" @click.stop="altSel(ev.id)" class="mt-0.5 flex-shrink-0" />
                <span class="text-gray-400 w-12 flex-shrink-0">{{ fmtTime(ev.timestamp) }}</span>
                <span class="w-4 text-center flex-shrink-0">{{ icone(ev.type) }}</span>
                <span :class="corTipo(ev.type)" class="w-20 flex-shrink-0 truncate font-semibold">{{ ev.type }}</span>
                <span class="text-gray-400 flex-1 truncate">{{ resumo(ev) }}</span>
                <span v-if="ev.data?.duration_ms" class="text-gray-400 w-12 text-right flex-shrink-0">{{ ev.data.duration_ms }}ms</span>
              </div>
              <div v-if="expandidos.has(ev.id)" class="ml-9 mr-1 mb-1 p-2 bg-gray-50 dark:bg-gray-900/50 rounded text-xxs text-gray-500 overflow-x-auto max-h-40 overflow-y-auto">
                <div v-for="(v, k) in ev.data" :key="k" class="mb-0.5">
                  <span class="font-semibold text-gray-400">{{ k }}:</span>
                  <pre v-if="isLongo(v)" class="inline whitespace-pre-wrap ml-1">{{ fmtVal(v) }}</pre>
                  <span v-else class="text-gray-600 dark:text-gray-300 ml-1">{{ fmtVal(v) }}</span>
                </div>
              </div>
            </div>
          </div>
          <!-- footer -->
          <div class="flex items-center justify-between px-2 py-1 border-t border-gray-100 dark:border-gray-700/50 bg-gray-50/50 dark:bg-gray-800/50 flex-shrink-0 text-xxs text-gray-400">
            <span>{{ itensFiltrados.length }} eventos</span>
            <div class="flex gap-2">
              <button @click="selTodos" class="hover:text-gray-600">Sel todos</button>
              <button @click="sel = new Set()" class="hover:text-gray-600">Limpar</button>
              <button @click="exportarTxt" class="hover:text-green-600 font-semibold">Exportar TXT</button>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Painel expandido (maximizado) -->
    <div v-if="expandido"
      class="fixed inset-0 z-[10000] bg-black/40 flex items-center justify-center p-4"
      @click.self="expandido = false"
    >
      <div class="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-xl shadow-2xl flex flex-col" style="width:95vw;height:90vh;max-width:1600px">
        <div class="flex items-center justify-between px-4 py-2 border-b border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-700 flex-shrink-0 rounded-t-xl">
          <span class="font-semibold text-gray-600 dark:text-gray-300 text-sm flex items-center gap-1.5">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
            Debug Logs — Expandido
            <span class="text-gray-400 font-normal">({{ eventos.length }})</span>
          </span>
          <div class="flex items-center gap-1">
            <button @click="abrirJanela" class="text-gray-400 hover:text-blue-500 px-2 py-0.5 rounded text-xs hover:bg-gray-200 dark:hover:bg-gray-600">Janela</button>
            <button @click="exportarTxt" class="text-gray-400 hover:text-green-600 px-2 py-0.5 rounded text-xs hover:bg-gray-200 dark:hover:bg-gray-600">Exportar</button>
            <button @click="expandido = false" class="text-gray-400 hover:text-gray-600 font-bold ml-2 text-lg">&times;</button>
          </div>
        </div>
        <div v-if="!logado" class="flex-1 flex flex-col items-center justify-center p-6 space-y-3">
          <p class="text-gray-500 text-sm">Faça login para ver os logs de depuração:</p>
          <input v-model="loginUser" type="text" placeholder="Usuário" class="input max-w-xs text-sm px-2 py-1.5" @keyup.enter="fazerLogin" />
          <input v-model="loginPass" type="password" placeholder="Senha" class="input max-w-xs text-sm px-2 py-1.5" @keyup.enter="fazerLogin" />
          <p v-if="loginErro" class="text-red-500 text-xs">{{ loginErro }}</p>
          <button @click="fazerLogin" class="btn-primary text-sm py-1.5 px-6">Entrar</button>
        </div>
        <template v-else>
          <div class="flex items-center gap-1 px-3 py-1.5 border-b border-gray-100 dark:border-gray-700/50 bg-gray-50/50 dark:bg-gray-800/50 flex-shrink-0">
            <select v-model="filtroTipo" class="text-xs bg-transparent border border-gray-200 dark:border-gray-600 rounded px-1 py-0.5 text-gray-500 outline-none">
              <option value="">Todos</option>
              <option value="api_request">Requisição</option>
              <option value="api_response">Resposta</option>
              <option value="db_query">Query DB</option>
              <option value="generator_step">Generator</option>
              <option value="scheduler_cycle">Scheduler</option>
              <option value="error">Erro</option>
            </select>
            <input v-model="buscaTexto" placeholder="Buscar..." class="text-xs bg-transparent border border-gray-200 dark:border-gray-600 rounded px-1 py-0.5 text-gray-500 outline-none flex-1 min-w-0" />
            <button @click="limparEventos" class="text-gray-400 hover:text-red-500 text-xs px-1">Limpar</button>
          </div>
          <div class="flex-1 overflow-y-auto font-mono debug-scroll p-1" ref="listaExpandRef">
            <div v-if="!itensFiltrados.length" class="text-gray-400 text-center py-8 text-xs">Nenhum evento</div>
            <div v-for="ev in itensFiltrados" :key="ev.id" class="mb-px">
              <div class="flex items-start gap-1.5 px-2 py-1 rounded cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700/50"
                :class="[sel.has(ev.id) ? 'ring-1 ring-blue-400' : '', ev.type === 'error' ? 'bg-red-50 dark:bg-red-900/10' : '']"
                @click="altExpand(ev.id)"
              >
                <input type="checkbox" :checked="sel.has(ev.id)" @click.stop="altSel(ev.id)" class="mt-0.5 flex-shrink-0" />
                <span class="text-gray-400 w-14 flex-shrink-0">{{ fmtTime(ev.timestamp) }}</span>
                <span class="w-4 text-center flex-shrink-0">{{ icone(ev.type) }}</span>
                <span :class="corTipo(ev.type)" class="w-24 flex-shrink-0 truncate font-semibold">{{ ev.type }}</span>
                <span class="text-gray-500 w-16 flex-shrink-0 truncate text-xxs">{{ ev.source }}</span>
                <span class="text-gray-400 flex-1 truncate">{{ resumo(ev) }}</span>
                <span v-if="ev.data?.duration_ms" class="text-gray-400 w-14 text-right flex-shrink-0">{{ ev.data.duration_ms }}ms</span>
              </div>
              <div v-if="expandidos.has(ev.id)" class="ml-11 mr-2 mb-1 p-2 bg-gray-50 dark:bg-gray-900/50 rounded text-xs text-gray-500 overflow-x-auto max-h-52 overflow-y-auto">
                <div v-for="(v, k) in ev.data" :key="k" class="mb-0.5">
                  <span class="font-semibold text-gray-400">{{ k }}:</span>
                  <pre v-if="isLongo(v)" class="inline whitespace-pre-wrap ml-1">{{ fmtVal(v) }}</pre>
                  <span v-else class="text-gray-600 dark:text-gray-300 ml-1">{{ fmtVal(v) }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="flex items-center justify-between px-3 py-1.5 border-t border-gray-100 dark:border-gray-700/50 bg-gray-50/50 dark:bg-gray-800/50 flex-shrink-0 text-xs text-gray-400">
            <span>{{ itensFiltrados.length }} eventos ({{ eventos.length }} total)</span>
            <div class="flex gap-3">
              <button @click="selTodos" class="hover:text-gray-600">Sel todos</button>
              <button @click="sel = new Set()" class="hover:text-gray-600">Limpar</button>
              <button @click="exportarTxt" class="hover:text-green-600 font-semibold">Exportar TXT</button>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onUnmounted, computed, nextTick, onMounted } from "vue";
import Toast from "@/components/Toast.vue";

const mostrar = ref(false);
const expandido = ref(false);
const logado = ref(false);
const loginUser = ref("admin");
const loginPass = ref("admin");
const loginErro = ref("");
const eventos = ref<any[]>([]);
const sel = ref<Set<number>>(new Set());
const expandidos = ref<Set<number>>(new Set());
const filtroTipo = ref("");
const buscaTexto = ref("");
const lastId = ref(0);
const pw = ref(450);
const ph = ref(400);
const listaRef = ref<HTMLElement | null>(null);
const listaExpandRef = ref<HTMLElement | null>(null);
let timer: ReturnType<typeof setInterval> | null = null;

const itensFiltrados = computed(() => {
  let r = eventos.value;
  if (filtroTipo.value) r = r.filter(e => e.type === filtroTipo.value);
  if (buscaTexto.value) {
    const q = buscaTexto.value.toLowerCase();
    r = r.filter(e =>
      (e.type || "").toLowerCase().includes(q) ||
      (e.source || "").toLowerCase().includes(q) ||
      JSON.stringify(e.data || "").toLowerCase().includes(q)
    );
  }
  return r;
});

function toggleDebug() {
  if (!logado.value) mostrar.value = true;
  else mostrar.value = !mostrar.value;
}

function fazerLogin() {
  loginErro.value = "";
  if (loginUser.value === "admin" && loginPass.value === "admin") {
    logado.value = true;
    iniciarPoll();
  } else {
    loginErro.value = "Credenciais inválidas";
  }
}

async function buscarEventos() {
  try {
    const r = await fetch(`/api/debug/events?since_id=${lastId.value}&limit=200`);
    if (!r.ok) return;
    const data = await r.json();
    if (data.events?.length) {
      eventos.value.push(...data.events);
      if (eventos.value.length > 2000) eventos.value = eventos.value.slice(-1000);
    }
    lastId.value = data.last_id || lastId.value;
    await nextTick();
    if (listaRef.value) listaRef.value.scrollTop = listaRef.value.scrollHeight;
    if (listaExpandRef.value) listaExpandRef.value.scrollTop = listaExpandRef.value.scrollHeight;
  } catch {}
}

function iniciarPoll() {
  buscarEventos();
  if (!timer) timer = setInterval(buscarEventos, 2000);
}

function pararPoll() {
  if (timer) { clearInterval(timer); timer = null; }
}

const isDark = ref(false);

onMounted(() => {
  isDark.value = document.documentElement.classList.contains("dark");
});

function toggleDark() {
  isDark.value = !isDark.value;
  document.documentElement.classList.toggle("dark", isDark.value);
  localStorage.setItem("darkMode", String(isDark.value));
}

function fmtTime(ts: string) {
  if (!ts) return "--:--:--";
  try { return new Date(ts).toLocaleTimeString('pt-BR'); } catch { return ts; }
}

function icone(type: string) {
  const icons: Record<string, string> = { api_request: "→", api_response: "←", db_query: "🗄", generator_step: "⚙", scheduler_cycle: "⏰", error: "✖" };
  return icons[type] || "•";
}

function corTipo(type: string) {
  const cores: Record<string, string> = { api_request: "text-blue-500", api_response: "text-teal-500", db_query: "text-purple-500", generator_step: "text-green-600", scheduler_cycle: "text-orange-500", error: "text-red-500" };
  return cores[type] || "text-gray-500";
}

function resumo(ev: any) {
  const d = ev.data || {};
  switch (ev.type) {
    case "api_request": return `${d.method || ""} ${d.path || ""}`;
    case "api_response": return `${d.status || ""} ${d.path || ""}`;
    case "db_query": return (d.sql || "").substring(0, 100);
    case "generator_step": return `${d.step || ""}${d.tipo ? " [" + d.tipo + "]" : ""}`;
    case "scheduler_cycle": return d.action || "";
    case "error": return d.message || "";
    default: return d.message || "";
  }
}

function isLongo(val: any) {
  if (typeof val === "string") return val.length > 80;
  if (typeof val === "object") return true;
  return false;
}

function fmtVal(val: any) {
  if (val == null) return "";
  if (typeof val === "object") return JSON.stringify(val, null, 2);
  return String(val);
}

function altSel(id: number) {
  const s = new Set(sel.value);
  if (s.has(id)) s.delete(id); else s.add(id);
  sel.value = s;
}

function selTodos() {
  if (sel.value.size === itensFiltrados.value.length) sel.value = new Set();
  else sel.value = new Set(itensFiltrados.value.map(e => e.id));
}

function altExpand(id: number) {
  const s = new Set(expandidos.value);
  if (s.has(id)) s.delete(id); else s.add(id);
  expandidos.value = s;
}

function limparEventos() {
  eventos.value = [];
  lastId.value = 0;
  sel.value = new Set();
  expandidos.value = new Set();
  fetch("/api/debug/events/clear", { method: "POST" }).catch(() => {});
}

function exportarTxt() {
  const ids = sel.value;
  const lista = ids.size ? eventos.value.filter(e => ids.has(e.id)) : eventos.value;
  if (!lista.length) return;
  const linhas: string[] = [
    "=== DEBUG LOGS EXPORT ===",
    `Exportado em: ${new Date().toLocaleString('pt-BR')}`,
    `Total: ${lista.length}`,
    "=".repeat(60), "",
  ];
  for (const ev of lista) {
    linhas.push(`[${ev.timestamp}] [${ev.type}] [${ev.source}]`);
    for (const [k, v] of Object.entries(ev.data || {})) {
      if (v != null) linhas.push(`  ${k}: ${typeof v === 'object' ? JSON.stringify(v, null, 2) : v}`);
    }
    linhas.push("");
  }
  const blob = new Blob([linhas.join("\n")], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `debug_${Date.now()}.txt`;
  a.click();
  URL.revokeObjectURL(url);
}

function abrirJanela() {
  const w = window.open("", "debug_ecodata", "width=800,height=600,scrollbars=yes,resizable=yes");
  if (!w) { alert("Pop-up bloqueado. Permita pop-ups para este site."); return; }
  w.document.write(`<!DOCTYPE html><html><head><meta charset="utf-8"><title>Debug ECOdata</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:monospace; font-size:12px; background:#1a1a2e; color:#ccc; padding:8px; }
h2 { color:#888; margin-bottom:8px; font-size:14px; }
.ctrl { display:flex; gap:6px; margin-bottom:8px; flex-wrap:wrap; }
.ctrl select, .ctrl input { background:#16213e; color:#ccc; border:1px solid #333; border-radius:3px; padding:3px 6px; font-size:11px; }
.ctrl button { background:#0f3460; color:#ccc; border:none; border-radius:3px; padding:3px 8px; cursor:pointer; font-size:11px; }
.ctrl button:hover { background:#1a5276; }
.ev { display:flex; gap:6px; padding:2px 4px; border-bottom:1px solid #222; cursor:pointer; }
.ev:hover { background:#16213e; }
.ev.sel { outline:1px solid #4fc3f7; }
.t { color:#555; width:70px; flex-shrink:0; }
.i { width:20px; text-align:center; flex-shrink:0; }
.ty { width:100px; flex-shrink:0; font-weight:bold; }
.ty0 { color:#4fc3f7; }
.ty1 { color:#26a69a; }
.ty2 { color:#ab47bc; }
.ty3 { color:#66bb6a; }
.ty4 { color:#ffa726; }
.ty5 { color:#ef5350; }
.msg { flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:#aaa; }
.dur { width:60px; text-align:right; flex-shrink:0; color:#555; }
.det { margin-left:96px; padding:6px; background:#16213e; border-radius:4px; font-size:11px; color:#999; margin-bottom:4px; }
.det b { color:#777; }
pre { display:inline; white-space:pre-wrap; word-break:break-all; }
.cb { flex-shrink:0; }
#lista { height:calc(100vh - 120px); overflow-y:auto; }
::-webkit-scrollbar { width:5px; }
::-webkit-scrollbar-thumb { background:#333; border-radius:3px; }
</style></head><body>
<h2>🐞 Debug ECOdata</h2>
<div class="ctrl">
<select id="filtro"><option value="">Todos</option><option value="api_request">Req</option><option value="api_response">Resp</option><option value="db_query">DB</option><option value="generator_step">Gen</option><option value="scheduler_cycle">Sch</option><option value="error">Erro</option></select>
<input id="busca" placeholder="Buscar..." />
<button id="selTodos">Sel todos</button>
<button id="limparSel">Limpar</button>
<button id="exportar">Exportar TXT</button>
</div>
<div id="lista"></div>
<script>
const ST = window.sessionStorage || {};
let eventos = [];
let lastId = 0;
let selSet = new Set();
let expandSet = new Set();
let filtro = "";
let busca = "";

function carregar() {
  fetch('/api/debug/events?since_id='+lastId+'&limit=200').then(r=>r.json()).then(d=>{
    if(d.events&&d.events.length){eventos.push(...d.events);if(eventos.length>2000)eventos=eventos.slice(-1000);}
    lastId=d.last_id||lastId; render();
  }).catch(()=>{});
}
setInterval(carregar,2000);

function render(){
  let lista=document.getElementById('lista');
  let r=eventos;
  if(filtro)r=r.filter(e=>e.type===filtro);
  if(busca){let q=busca.toLowerCase();r=r.filter(e=>(e.type||'').toLowerCase().includes(q)||JSON.stringify(e.data||'').toLowerCase().includes(q));}
  let html='';
  if(!r.length)html='<div style="text-align:center;padding:40px;color:#555">Nenhum evento</div>';
  for(let ev of r){
    let sel=selSet.has(ev.id)?' sel':'';
    let bg=ev.type==='error'?' style="background:rgba(239,83,80,0.08)"':'';
    let icone={api_request:'→',api_response:'←',db_query:'🗄',generator_step:'⚙',scheduler_cycle:'⏰',error:'✖'}[ev.type]||'•';
    let tyCls={api_request:'ty0',api_response:'ty1',db_query:'ty2',generator_step:'ty3',scheduler_cycle:'ty4',error:'ty5'}[ev.type]||'';
    let msg=resumo(ev);
    let dur=ev.data&&ev.data.duration_ms?ev.data.duration_ms+'ms':'';
    let ts=ev.timestamp?new Date(ev.timestamp).toLocaleTimeString('pt-BR'):'';
    let det='';
    if(expandSet.has(ev.id)){
      det='<div class="det">';
      for(let[k,v]of Object.entries(ev.data||{})){
        let val=typeof v==='object'?JSON.stringify(v,null,2):v;
        det+='<b>'+k+':</b> '+(val&&val.length>80?'<pre>'+val+'</pre>':val)+'<br>';
      }
      det+='</div>';
    }
    html+= '<div class="ev'+sel+'" onclick="toggleSel('+ev.id+')" ondblclick="toggleExp('+ev.id+')"'+bg+'>'
      +'<input class="cb" type="checkbox" '+(selSet.has(ev.id)?'checked':'')+' onclick="event.stopPropagation();toggleSel('+ev.id+')"/>'
      +'<span class="t">'+ts+'</span><span class="i">'+icone+'</span><span class="ty '+tyCls+'">'+ev.type+'</span>'
      +'<span class="msg">'+msg+'</span>'
      +(dur?'<span class="dur">'+dur+'</span>':'')
      +'</div>'+det;
  }
  lista.innerHTML=html;
}
function resumo(ev){
  let d=ev.data||{};
  switch(ev.type){
    case'api_request':return (d.method||'')+' '+(d.path||'');
    case'api_response':return (d.status||'')+' '+(d.path||'');
    case'db_query':return (d.sql||'').substring(0,100);
    case'generator_step':return (d.step||'')+(d.tipo?' ['+d.tipo+']':'');
    case'scheduler_cycle':return d.action||'';
    case'error':return d.message||'';
    default:return d.message||'';
  }
}
function toggleSel(id){selSet.has(id)?selSet.delete(id):selSet.add(id);render();}
function toggleExp(id){expandSet.has(id)?expandSet.delete(id):expandSet.add(id);render();}
document.getElementById('selTodos').onclick=()=>{if(selSet.size===r.length)selSet.clear();else eventos.forEach(e=>selSet.add(e.id));render();};
document.getElementById('limparSel').onclick=()=>{selSet.clear();render();};
document.getElementById('exportar').onclick=()=>{
  let ids=selSet;let lista=ids.size?eventos.filter(e=>ids.has(e.id)):eventos;
  let txt='=== DEBUG LOGS EXPORT ===\\nExportado em: '+new Date().toLocaleString('pt-BR')+'\\nTotal: '+lista.length+'\\n'+'='.repeat(60)+'\\n\\n';
  for(let ev of lista){
    txt+='['+ev.timestamp+'] ['+ev.type+'] ['+(ev.source||'')+']\\n';
    for(let[k,v]of Object.entries(ev.data||{})){if(v!=null)txt+='  '+k+': '+(typeof v==='object'?JSON.stringify(v,null,2):v)+'\\n';}
    txt+='\\n';
  }
  let a=document.createElement('a');a.href=URL.createObjectURL(new Blob([txt],{type:'text/plain;charset=utf-8'}));a.download='debug_'+Date.now()+'.txt';a.click();
};
document.getElementById('filtro').onchange=function(){filtro=this.value;render();};
document.getElementById('busca').oninput=function(){busca=this.value;render();};
carregar();
<\/script></body></html>`);
  w.document.close();
}

watch(mostrar, (v) => { if (v) iniciarPoll(); else if (!expandido.value) pararPoll(); });
watch(expandido, (v) => { if (v) iniciarPoll(); else if (!mostrar.value) pararPoll(); });

onUnmounted(() => pararPoll());

const nav = [
  { path: "/dashboard", label: "Dashboard", icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>' },
  { path: "/scheduler", label: "Agendamentos", icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>' },
  { path: "/executions", label: "Execuções", icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/></svg>' },
  { path: "/files", label: "Arquivos", icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"/></svg>' },
  { path: "/logs", label: "Logs", icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>' },
  { path: "/settings", label: "Configurações", icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>' },
  { path: "/backup", label: "Backup", icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"/></svg>' },
];
</script>

<style scoped>
.debug-scroll::-webkit-scrollbar { width: 4px; height: 4px; }
.debug-scroll::-webkit-scrollbar-thumb { background: #bbb; border-radius: 2px; }
.debug-scroll::-webkit-scrollbar-track { background: transparent; }
pre { white-space: pre-wrap; word-break: break-all; font-family: inherit; font-size: inherit; margin: 0; }
</style>
