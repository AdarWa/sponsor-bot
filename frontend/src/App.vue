<script setup>
import { computed, onMounted, ref } from 'vue';
import { getProfile, login, register } from './services/api';

const mode = ref('login');
const email = ref('');
const password = ref('');
const fullName = ref('');
const status = ref('');
const statusType = ref('success');
const loading = ref(false);
const token = ref(window.localStorage.getItem('sb_access_token') ?? '');
const profile = ref(null);

const submitLabel = computed(() => (mode.value === 'login' ? 'Sign in' : 'Create account'));

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

const fetchProfile = async () => {
  if (!token.value) {
    profile.value = null;
    return;
  }
  try {
    profile.value = await getProfile(token.value);
  } catch (error) {
    token.value = '';
    window.localStorage.removeItem('sb_access_token');
    statusType.value = 'error';
    status.value = error.message ?? 'Session expired, please log in again.';
  }
};

const logout = () => {
  token.value = '';
  window.localStorage.removeItem('sb_access_token');
  profile.value = null;
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
      <button type="button" @click="logout">Log out</button>
    </div>
  </div>
</template>
