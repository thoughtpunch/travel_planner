import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";

const routes: RouteRecordRaw[] = [
  { path: "/", component: () => import("./pages/Dashboard.vue") },
  {
    path: "/trips/:id",
    component: () => import("./pages/TripWorkspace.vue"),
    props: true,
    children: [
      { path: "", redirect: { name: "trip-overview" } },
      { name: "trip-overview", path: "overview", component: () => import("./pages/TripOverview.vue"), props: true },
      { name: "trip-wizard", path: "wizard", component: () => import("./pages/TripWizard.vue"), props: true },
      { name: "trip-runs", path: "runs", component: () => import("./pages/TripRuns.vue"), props: true },
      { name: "trip-shortlist", path: "shortlist", component: () => import("./pages/TripShortlist.vue"), props: true },
      { name: "trip-notes", path: "notes", component: () => import("./pages/TripNotes.vue"), props: true },
    ],
  },
  {
    name: "run-results",
    path: "/trips/:id/runs/:runId",
    component: () => import("./pages/RunResults.vue"),
    props: true,
  },
  { path: "/settings", component: () => import("./pages/Settings.vue") },
  { path: "/wizard", component: () => import("./pages/StandaloneWizard.vue") },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});
