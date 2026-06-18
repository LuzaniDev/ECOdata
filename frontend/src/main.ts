import { createApp } from "vue";
import { createRouter, createWebHashHistory } from "vue-router";
import App from "./App.vue";
import "./style.css";

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: "/", redirect: "/scheduler" },
    {
      path: "/dashboard",
      name: "Dashboard",
      component: () => import("@/views/Dashboard.vue"),
    },
    {
      path: "/scheduler",
      name: "Scheduler",
      component: () => import("@/views/Scheduler.vue"),
    },
    {
      path: "/executions",
      name: "Execucoes",
      component: () => import("@/views/Execucoes.vue"),
    },
    {
      path: "/files",
      name: "Arquivos",
      component: () => import("@/views/Arquivos.vue"),
    },
    {
      path: "/logs",
      name: "Logs",
      component: () => import("@/views/Logs.vue"),
    },
    {
      path: "/settings",
      name: "Settings",
      component: () => import("@/views/Settings.vue"),
    },
    {
      path: "/backup",
      name: "Backup",
      component: () => import("@/views/Backup.vue"),
    },
  ],
});

createApp(App).use(router).mount("#app");