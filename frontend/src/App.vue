<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';

import EmailScrapeDashboard from './views/EmailScrapeDashboard.vue';
import EmailSendDashboard from './views/EmailSendDashboard.vue';
import SearchScrapeDashboard from './views/SearchScrapeDashboard.vue';

const dashboards = [
  { id: 'email-scrape', label: 'Email scrape', component: EmailScrapeDashboard },
  { id: 'search-scrape', label: 'Search scrape', component: SearchScrapeDashboard },
  { id: 'email-send', label: 'Email send', component: EmailSendDashboard }
];
const dashboardMap = dashboards.reduce(
  (map, entry) => {
    map[entry.id] = entry.component;
    return map;
  },
  {}
);
const activeDashboard = ref(dashboards[0].id);
const currentDashboardComponent = computed(() => dashboardMap[activeDashboard.value]);

const extractDashboardFromPath = () => {
  if (typeof window === 'undefined') {
    return null;
  }
  const match = window.location.pathname.match(/^\/dashboard\/([^/]+)$/);
  if (match && dashboardMap[match[1]]) {
    return match[1];
  }
  return null;
};

const updateHistoryPath = (path) => {
  if (typeof window === 'undefined') {
    return;
  }
  if (window.location.pathname !== path) {
    window.history.replaceState({}, '', path);
  }
};

const goToDashboard = (id) => {
  if (!dashboardMap[id]) {
    return;
  }
  activeDashboard.value = id;
  updateHistoryPath(`/dashboard/${id}`);
};

const ensureDashboardRoute = () => {
  if (typeof window === 'undefined') {
    return;
  }
  const path = window.location.pathname;
  const currentId = extractDashboardFromPath();
  if (currentId) {
    activeDashboard.value = currentId;
  } else if (path.startsWith('/dashboard')) {
    updateHistoryPath(`/dashboard/${activeDashboard.value}`);
  }
};

const handlePopState = () => {
  const currentId = extractDashboardFromPath();
  if (currentId) {
    activeDashboard.value = currentId;
  } else {
    updateHistoryPath(`/dashboard/${activeDashboard.value}`);
  }
};

watch(activeDashboard, (value, oldValue) => {
  if (value !== oldValue) {
    updateHistoryPath(`/dashboard/${value}`);
  }
});

onMounted(() => {
  const pathDashboard = extractDashboardFromPath();
  if (pathDashboard) {
    activeDashboard.value = pathDashboard;
  }
  if (typeof window !== 'undefined') {
    window.addEventListener('popstate', handlePopState);
  }
  ensureDashboardRoute();
});

onUnmounted(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('popstate', handlePopState);
  }
});
</script>

<template>
  <div class="card">
    <h1>Dashboard</h1>

    <div class="dashboard">
      <nav class="dashboard-nav">
        <button
          v-for="entry in dashboards"
          :key="entry.id"
          type="button"
          class="dashboard-link"
          :class="{ active: activeDashboard === entry.id }"
          @click="goToDashboard(entry.id)"
        >
          {{ entry.label }}
        </button>
      </nav>

      <component :is="currentDashboardComponent" />
    </div>
  </div>
</template>
