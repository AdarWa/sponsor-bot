<script setup>
import { inject, onMounted, ref, watch } from 'vue';

import { addEmail, deleteEmail, getEmailTemplate, getEmails, sendEmailCampaign, updateEmailTemplate } from '../services/api';

const authToken = inject('authToken');

const subject = ref('');
const body = ref('');
const status = ref('');
const statusType = ref('success');
const saving = ref(false);
const sending = ref(false);
const emails = ref([]);
const newEmail = ref('');
const emailListStatus = ref('');
const emailListStatusType = ref('success');

const resetState = () => {
  subject.value = '';
  body.value = '';
  status.value = '';
  statusType.value = 'success';
  saving.value = false;
  sending.value = false;
  emails.value = [];
  newEmail.value = '';
  emailListStatus.value = '';
  emailListStatusType.value = 'success';
};

const loadTemplate = async () => {
  if (!authToken?.value) {
    resetState();
    return;
  }
  try {
    const template = await getEmailTemplate(authToken.value);
    subject.value = template.subject;
    body.value = template.body;
    status.value = '';
  } catch (error) {
    statusType.value = 'error';
    status.value = error.message ?? 'Unable to load email template.';
  }
};

const saveTemplate = async () => {
  if (!authToken?.value) {
    return;
  }
  saving.value = true;
  try {
    await updateEmailTemplate({ subject: subject.value, body: body.value }, authToken.value);
    statusType.value = 'success';
    status.value = 'Template saved.';
  } catch (error) {
    statusType.value = 'error';
    status.value = error.message ?? 'Unable to save template.';
  } finally {
    saving.value = false;
  }
};

const sendEmails = async () => {
  if (!authToken?.value) {
    return;
  }
  status.value = '';
  sending.value = true;
  try {
    const response = await sendEmailCampaign(authToken.value);
    statusType.value = 'success';
    status.value = response.message ?? 'Email sending triggered.';
  } catch (error) {
    statusType.value = 'error';
    status.value = error.message ?? 'Unable to send emails.';
  } finally {
    sending.value = false;
  }
};

const loadEmails = async () => {
  if (!authToken?.value) {
    emails.value = [];
    return;
  }
  try {
    emails.value = await getEmails(authToken.value);
    emailListStatus.value = '';
  } catch (error) {
    emailListStatusType.value = 'error';
    emailListStatus.value = error.message ?? 'Unable to load emails.';
  }
};

const addEmailRecord = async () => {
  if (!authToken?.value || !newEmail.value.trim()) {
    return;
  }
  try {
    await addEmail({ email: newEmail.value.trim() }, authToken.value);
    emailListStatusType.value = 'success';
    emailListStatus.value = 'Email added.';
    newEmail.value = '';
    await loadEmails();
  } catch (error) {
    emailListStatusType.value = 'error';
    emailListStatus.value = error.message ?? 'Unable to add email.';
  }
};

const removeEmail = async (id) => {
  if (!authToken?.value) {
    return;
  }
  try {
    await deleteEmail(id, authToken.value);
    emailListStatusType.value = 'success';
    emailListStatus.value = 'Email removed.';
    await loadEmails();
  } catch (error) {
    emailListStatusType.value = 'error';
    emailListStatus.value = error.message ?? 'Unable to remove email.';
  }
};

onMounted(() => {
  loadTemplate();
  loadEmails();
});
watch(
  () => authToken?.value,
  (value) => {
    if (value) {
      loadTemplate();
      loadEmails();
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
        <h3>Email send dashboard</h3>
        <p>Configure your outreach template and trigger email delivery.</p>
      </div>
    </div>

    <div v-if="status" class="alert" :class="statusType">
      {{ status }}
    </div>

    <div class="email-records">
      <h4>Recipient emails</h4>
      <p class="section-description">Add individual emails or remove ones you no longer want to contact.</p>

      <div v-if="emailListStatus" class="alert" :class="emailListStatusType">
        {{ emailListStatus }}
      </div>

      <form class="section-form" @submit.prevent="addEmailRecord">
        <input
          v-model="newEmail"
          type="email"
          placeholder="contact@example.com"
          required
        />
        <button type="submit">Add email</button>
      </form>

      <div v-if="emails.length" class="item-list">
        <div
          v-for="record in emails"
          :key="record.id"
          class="item-row"
        >
          <div>
            <p class="item-primary">{{ record.email }}</p>
            <p class="item-meta">Added {{ new Date(record.created_at).toLocaleString() }}</p>
          </div>
          <button type="button" class="button-danger" @click="removeEmail(record.id)">
            Remove
          </button>
        </div>
      </div>
      <div v-else class="empty-state">
        No emails yet. Add one above to build your outreach list.
      </div>
    </div>

    <div class="form-control">
      <label for="template-subject">Subject</label>
      <input
        id="template-subject"
        v-model="subject"
        type="text"
        required
      />
    </div>

    <div class="form-control">
      <label for="template-body">Body</label>
      <textarea
        id="template-body"
        v-model="body"
        rows="5"
        required
      ></textarea>
    </div>

    <div class="section-actions">
      <button type="button" @click="saveTemplate" :disabled="saving">
        {{ saving ? 'Saving…' : 'Save template' }}
      </button>
      <button type="button" class="button-danger" @click="sendEmails" :disabled="sending">
        {{ sending ? 'Sending…' : 'Send campaign' }}
      </button>
    </div>
  </section>
</template>
