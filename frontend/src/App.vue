<script setup>
import { computed, onMounted, ref } from 'vue';
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

const submitLabel = computed(() => (mode.value === 'login' ? 'Sign in' : 'Create account'));
const isAdmin = computed(() => Boolean(profile.value?.is_superuser));
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

const fetchProfile = async () => {
  if (!token.value) {
    profile.value = null;
    adminUsers.value = [];
    return;
  }
  try {
    profile.value = await getProfile(token.value);
    await fetchAdminUsers();
  } catch (error) {
    token.value = '';
    window.localStorage.removeItem('sb_access_token');
    profile.value = null;
    adminUsers.value = [];
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

const logout = () => {
  token.value = '';
  window.localStorage.removeItem('sb_access_token');
  profile.value = null;
  adminUsers.value = [];
  adminStatus.value = '';
  verifyingUserId.value = null;
  deletingUserId.value = null;
};

onMounted(fetchProfile);
</script>

<template>
  <div class="card">
    <div class="tabs">
      <div
        class="tab"
        :class="{ active: mode === 'login' }"
        @click="mode = 'login'"
      >
        Login
      </div>
      <div
        class="tab"
        :class="{ active: mode === 'register' }"
        @click="mode = 'register'"
      >
        Register
      </div>
    </div>

    <h1>{{ mode === 'login' ? 'Welcome back' : 'Create your account' }}</h1>

    <div v-if="status" class="alert" :class="statusType">
      {{ status }}
    </div>

    <form v-if="!token" @submit.prevent="handleSubmit">
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
      <p class="alert success">Authenticated via fastapi-users JWT backend.</p>
      <h2>{{ profile?.full_name || profile?.email }}</h2>
      <p>{{ profile?.email }}</p>
      <p>Status: {{ profile?.is_active ? 'Active' : 'Inactive' }}</p>
      <p>Verification: {{ profile?.is_verified ? 'Verified' : 'Pending' }}</p>
      <button type="button" @click="logout">Log out</button>

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
