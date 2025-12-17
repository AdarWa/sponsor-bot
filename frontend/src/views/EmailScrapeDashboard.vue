<script setup>
import { inject, onMounted, ref, watch } from 'vue';

import { createWebsite, deleteWebsite, getWebsites, scrapeWebsites } from '../services/api';

const authToken = inject('authToken');

const websites = ref([]);
const newWebsite = ref('');
const status = ref('');
const statusType = ref('success');
const scraping = ref(false);

const resetState = () => {
  websites.value = [];
  newWebsite.value = '';
  statusType.value = 'success';
  status.value = '';
  scraping.value = false;
};

const loadWebsites = async () => {
  if (!authToken?.value) {
    resetState();
    return;
  }
  try {
    websites.value = await getWebsites(authToken.value);
    status.value = '';
  } catch (error) {
    statusType.value = 'error';
    status.value = error.message ?? 'Unable to load websites.';
  }
};

const addWebsite = async () => {
  if (!authToken?.value || !newWebsite.value.trim()) {
    return;
  }
  try {
    await createWebsite({ url: newWebsite.value.trim() }, authToken.value);
    statusType.value = 'success';
    status.value = 'Website added.';
    newWebsite.value = '';
    await loadWebsites();
  } catch (error) {
    statusType.value = 'error';
    status.value = error.message ?? 'Unable to add website.';
  }
};

const removeWebsite = async (id) => {
  if (!authToken?.value) {
    return;
  }
  try {
    await deleteWebsite(id, authToken.value);
    statusType.value = 'success';
    status.value = 'Website removed.';
    await loadWebsites();
  } catch (error) {
    statusType.value = 'error';
    status.value = error.message ?? 'Unable to remove website.';
  }
};

const scrapeAll = async () => {
  if (!authToken?.value) {
    return;
  }
  status.value = '';
  scraping.value = true;
  try {
    const response = await scrapeWebsites(authToken.value);
    statusType.value = 'success';
    status.value = response.message ?? 'Scrape triggered.';
  } catch (error) {
    statusType.value = 'error';
    status.value = error.message ?? 'Unable to start scrape.';
  } finally {
    scraping.value = false;
  }
};

onMounted(loadWebsites);
watch(
  () => authToken?.value,
  (value) => {
    if (value) {
      loadWebsites();
    } else {
      resetState();
    }
  }
);
</script>

<template>
  <section class="dashboard-section">
    <div class="section-header">
      <div>
        <h3>Email scrape dashboard</h3>
        <p>Add websites to crawl for contact information.</p>
      </div>
      <button type="button" class="button-secondary" @click="scrapeAll" :disabled="scraping">
        {{ scraping ? 'Starting…' : 'Scrape all websites' }}
      </button>
    </div>

    <div v-if="status" class="alert" :class="statusType">
      {{ status }}
    </div>

    <form class="section-form" @submit.prevent="addWebsite">
      <input
        v-model="newWebsite"
        type="url"
        placeholder="https://example.com"
        required
      />
      <button type="submit">Add website</button>
    </form>

    <div v-if="websites.length" class="item-list">
      <div
        v-for="site in websites"
        :key="site.id"
        class="item-row"
      >
        <div class="item-details">
          <p class="item-primary">{{ site.url }}</p>
          <p class="item-meta">Added {{ new Date(site.created_at).toLocaleString() }}</p>
        </div>
        <button type="button" class="button-danger" @click="removeWebsite(site.id)">
          Remove
        </button>
      </div>
    </div>
    <div v-else class="empty-state">
      No websites yet.
    </div>
  </section>
</template>
