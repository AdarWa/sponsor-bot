<script setup>
import { computed, onMounted, onUnmounted, provide, ref, watch } from 'vue';

import EmailScrapeDashboard from './views/EmailScrapeDashboard.vue';
import EmailSendDashboard from './views/EmailSendDashboard.vue';
import SearchScrapeDashboard from './views/SearchScrapeDashboard.vue';
import { deleteUser, getProfile, listUsers, login, register, verifyUser } from './services/api';

const mode = ref('login');
const email = ref('');
const password = ref('');
const fullName = ref('');
const status = ref('');
const statusType = ref('success');
const loading = ref(false);
const token = ref(window.localStorage.getItem('sb_access_token') ?? '');
const profile = ref(null);
const adminUsers = ref([]);
const adminStatus = ref('');
const adminStatusType = ref('success');
const verifyingUserId = ref(null);
const deletingUserId = ref(null);
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

provide('authToken', token);

const submitLabel = computed(() => (mode.value === 'login' ? 'Sign in' : 'Create account'));
const pageTitle = computed(() => (token.value ? 'Dashboard' : mode.value === 'login' ? 'Welcome back' : 'Create your account'));
const isAdmin = computed(() => Boolean(profile.value?.is_superuser));
const isVerified = computed(() => Boolean(profile.value?.is_verified));
const pendingUsers = computed(() => adminUsers.value.filter((user) => !user.is_verified));

const handleSubmit = async () => {
  status.value = '';
  loading.value = true;
  try {
    if (mode.value === 'register') {
      await register({
        email: email.value,
        password: password.value,
        full_name: fullName.value || null
      });
      statusType.value = 'success';
      status.value = 'Account created! You can now log in.';
      mode.value = 'login';
      return;
    }

    const tokens = await login(email.value, password.value);
    token.value = tokens.access_token;
    window.localStorage.setItem('sb_access_token', token.value);
    status.value = '';
    await fetchProfile();
  } catch (error) {
    statusType.value = 'error';
    status.value = error.message ?? 'Unable to complete the request.';
  } finally {
    loading.value = false;
  }
};

const fetchAdminUsers = async () => {
  if (!token.value || !isAdmin.value) {
    adminUsers.value = [];
    return;
  }
  try {
    adminUsers.value = await listUsers(token.value);
    adminStatus.value = '';
  } catch (error) {
    adminStatusType.value = 'error';
    adminStatus.value = error.message ?? 'Unable to load users.';
  }
};

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
  if (isVerified.value) {
    updateHistoryPath(`/dashboard/${id}`);
  }
};

const ensureDashboardRoute = () => {
  if (typeof window === 'undefined') {
    return;
  }
  const path = window.location.pathname;
  const currentId = extractDashboardFromPath();
  if (isVerified.value) {
    if (currentId) {
      activeDashboard.value = currentId;
    } else {
      updateHistoryPath(`/dashboard/${activeDashboard.value}`);
    }
  } else if (path.startsWith('/dashboard')) {
    updateHistoryPath('/');
  }
};

const fetchProfile = async () => {
  if (!token.value) {
    profile.value = null;
    adminUsers.value = [];
    ensureDashboardRoute();
    return;
  }
  try {
    profile.value = await getProfile(token.value);
    await fetchAdminUsers();
    ensureDashboardRoute();
  } catch (error) {
    token.value = '';
    window.localStorage.removeItem('sb_access_token');
    profile.value = null;
    adminUsers.value = [];
    ensureDashboardRoute();
    statusType.value = 'error';
    status.value = error.message ?? 'Session expired, please log in again.';
  }
};

const verifyAccount = async (userId) => {
  if (!token.value) {
    return;
  }
  adminStatus.value = '';
  verifyingUserId.value = userId;
  try {
    await verifyUser(userId, token.value);
    adminStatusType.value = 'success';
    adminStatus.value = 'User verified successfully.';
    await fetchAdminUsers();
  } catch (error) {
    adminStatusType.value = 'error';
    adminStatus.value = error.message ?? 'Unable to verify user.';
  } finally {
    verifyingUserId.value = null;
  }
};

const deleteAccount = async (userId) => {
  if (!token.value) {
    return;
  }
  const confirmed = window.confirm('Delete this user? This action cannot be undone.');
  if (!confirmed) {
    return;
  }
  adminStatus.value = '';
  deletingUserId.value = userId;
  try {
    await deleteUser(userId, token.value);
    adminStatusType.value = 'success';
    adminStatus.value = 'User deleted successfully.';
    await fetchAdminUsers();
  } catch (error) {
    adminStatusType.value = 'error';
    adminStatus.value = error.message ?? 'Unable to delete user.';
  } finally {
    deletingUserId.value = null;
  }
};

const handlePopState = () => {
  if (!isVerified.value) {
    if (typeof window !== 'undefined' && window.location.pathname.startsWith('/dashboard')) {
      updateHistoryPath('/');
    }
    return;
  }
  const currentId = extractDashboardFromPath();
  if (currentId) {
    activeDashboard.value = currentId;
  } else {
    updateHistoryPath(`/dashboard/${activeDashboard.value}`);
  }
};

const logout = () => {
  token.value = '';
  window.localStorage.removeItem('sb_access_token');
  profile.value = null;
  adminUsers.value = [];
  adminStatus.value = '';
  verifyingUserId.value = null;
  deletingUserId.value = null;
  ensureDashboardRoute();
};

watch(isVerified, () => ensureDashboardRoute());
watch(activeDashboard, (value, oldValue) => {
  if (value !== oldValue && isVerified.value) {
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
  fetchProfile();
});

onUnmounted(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('popstate', handlePopState);
  }
});
</script>

<template>
  <div class="card">
    <div v-if="!token" class="tabs">
      <div class="tab" :class="{ active: mode === 'login' }" @click="mode = 'login'">
        Login
      </div>
      <div class="tab" :class="{ active: mode === 'register' }" @click="mode = 'register'">
        Register
      </div>
    </div>

    <h1>{{ pageTitle }}</h1>

    <div v-if="status" class="alert" :class="statusType">
      {{ status }}
    </div>

    <form v-if="!token" class="auth-form" @submit.prevent="handleSubmit">
      <div class="form-control">
        <label for="email">Email</label>
        <input
          id="email"
          v-model="email"
          name="email"
          type="email"
          autocomplete="email"
          required
        />
      </div>

      <div class="form-control" v-if="mode === 'register'">
        <label for="fullName">Full name</label>
        <input
          id="fullName"
          v-model="fullName"
          name="fullName"
          type="text"
          autocomplete="name"
        />
      </div>

      <div class="form-control">
        <label for="password">Password</label>
        <input
          id="password"
          v-model="password"
          name="password"
          type="password"
          autocomplete="current-password"
          minlength="8"
          required
        />
      </div>

      <button type="submit" :disabled="loading">
        {{ loading ? 'Please wait…' : submitLabel }}
      </button>
    </form>

    <div v-else class="profile-card">
      <h2>Good {{ new Date().getHours() < 12 ? 'morning' : new Date().getHours() < 18 ? 'afternoon' : 'evening' }}, {{ profile?.full_name.split(' ')[0] || profile?.email }}</h2>
      <button type="button" @click="logout">Log out</button>

      <div v-if="!isVerified" class="alert warning">
        Your account must be verified before you can access the scraping and email dashboards.
      </div>

      <div v-else class="dashboard">
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

      <section v-if="isAdmin" class="admin-panel">
        <div class="admin-panel__header">
          <div>
            <h3>Admin panel</h3>
            <p>Approve user accounts by marking them as verified.</p>
          </div>
          <span class="badge">Superuser</span>
        </div>

        <div v-if="adminStatus" class="alert" :class="adminStatusType">
          {{ adminStatus }}
        </div>

        <div v-if="pendingUsers.length === 0" class="empty-state">
          All registered users are verified. 🎉
        </div>
        <div v-else class="user-list">
          <div
            v-for="user in pendingUsers"
            :key="user.id"
            class="user-row"
          >
            <div>
              <p class="user-name">{{ user.full_name || user.email }}</p>
              <p class="user-email">{{ user.email }}</p>
            </div>
            <div class="user-actions">
              <button
                type="button"
                @click="verifyAccount(user.id)"
                :disabled="verifyingUserId === user.id || deletingUserId === user.id"
              >
                {{ verifyingUserId === user.id ? 'Verifying…' : 'Verify' }}
              </button>
              <button
                type="button"
                class="button-danger"
                @click="deleteAccount(user.id)"
                :disabled="verifyingUserId === user.id || deletingUserId === user.id"
              >
                {{ deletingUserId === user.id ? 'Deleting…' : 'Delete' }}
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>
