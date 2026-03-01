<script setup>
import { onMounted, ref } from 'vue';

import { createSearchQuery, deleteSearchQuery, getSearchQueries, scrapeSearchQueries } from '../services/api';

const queries = ref([]);
const newQuery = ref('');
const status = ref('');
const statusType = ref('success');
const scraping = ref(false);

const loadQueries = async () => {
  try {
    queries.value = await getSearchQueries();
    status.value = '';
  } catch (error) {
    statusType.value = 'error';
    status.value = error.message ?? 'Unable to load search queries.';
  }
};

const addQuery = async () => {
  if (!newQuery.value.trim()) {
    return;
  }
  try {
    await createSearchQuery({ query: newQuery.value.trim() });
    statusType.value = 'success';
    status.value = 'Query added.';
    newQuery.value = '';
    await loadQueries();
  } catch (error) {
    statusType.value = 'error';
    status.value = error.message ?? 'Unable to add query.';
  }
};

const removeQuery = async (id) => {
  try {
    await deleteSearchQuery(id);
    statusType.value = 'success';
    status.value = 'Query removed.';
    await loadQueries();
  } catch (error) {
    statusType.value = 'error';
    status.value = error.message ?? 'Unable to remove query.';
  }
};

const scrapeQueries = async () => {
  status.value = '';
  scraping.value = true;
  try {
    const response = await scrapeSearchQueries();
    statusType.value = 'success';
    status.value = response.message ?? 'Search scrape triggered.';
  } catch (error) {
    statusType.value = 'error';
    status.value = error.message ?? 'Unable to start search scrape.';
  } finally {
    scraping.value = false;
  }
};

onMounted(loadQueries);
</script>

<template>
  <section class="dashboard-section">
    <div class="section-header">
      <div>
        <h3>Search scrape dashboard</h3>
        <p>Define Google search queries that discover new websites.</p>
      </div>
      <button type="button" class="button-secondary" @click="scrapeQueries" :disabled="scraping">
        {{ scraping ? 'Starting…' : 'Search & add websites' }}
      </button>
    </div>

    <div v-if="status" class="alert" :class="statusType">
      {{ status }}
    </div>

    <form class="section-form" @submit.prevent="addQuery">
      <input
        v-model="newQuery"
        type="text"
        placeholder='generous big tech companies that are also nice and stuff'
        required
      />
      <button type="submit">Add query</button>
    </form>

    <div v-if="queries.length" class="item-list">
      <div
        v-for="query in queries"
        :key="query.id"
        class="item-row"
      >
        <div class="item-details">
          <p class="item-primary">{{ query.query }}</p>
          <p class="item-meta">Added {{ new Date(query.created_at).toLocaleString() }}</p>
        </div>
        <button type="button" class="button-danger" @click="removeQuery(query.id)">
          Remove
        </button>
      </div>
    </div>
    <div v-else class="empty-state">
      No search queries yet.
    </div>
  </section>
</template>
