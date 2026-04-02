<script setup>
import { onMounted, ref } from 'vue'
import AppNav from '@/components/AppNav.vue'
import AppPageShell from '@/components/AppPageShell.vue'
import { authAPI, profileAPI } from '../../util/apis.js'
import { formatDateTime } from '@/utils/formatters.js'

const loading = ref(true)
const errorMsg = ref('')
const me = ref(null)
const scores = ref(null)
const sessions = ref([])

async function loadDashboard() {
  loading.value = true
  errorMsg.value = ''

  try {
    const [meData, scoresData, sessionsData] = await Promise.all([
      authAPI.getMe(),
      profileAPI.getMyScores().catch(() => null),
      authAPI.getSessions().catch(() => []),
    ])

    me.value = meData
    scores.value = scoresData
    sessions.value = Array.isArray(sessionsData) ? sessionsData : []
  } catch (error) {
    errorMsg.value = error.message || 'Failed to load dashboard'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDashboard()
})
</script>

<template>
  <AppPageShell
    title="Workspace."
    subtitle="A personal workspace for reviewing CVs, saving structured records, and searching profiles by the signals that matter."
  >
    <AppNav />

    <div v-if="loading" class="status-message success">Loading your dashboard...</div>
    <div v-else-if="errorMsg" class="status-message error">{{ errorMsg }}</div>

    <div v-else class="page-grid">
      <section class="info-card">
        <p class="section-kicker">Account</p>
        <h2>Account overview</h2>
        <p><strong>Email:</strong> {{ me?.email }}</p>
        <p><strong>Verified:</strong> {{ me?.is_active ? 'Yes' : 'No' }}</p>
        <p><strong>Created:</strong> {{ formatDateTime(me?.created_at) }}</p>
        <p><strong>Updated:</strong> {{ formatDateTime(me?.updated_at) }}</p>
      </section>

      <section class="info-card">
        <p class="section-kicker">Scoring</p>
        <h2>Your latest CV snapshot</h2>
        <div v-if="scores" class="score-grid">
          <div class="score-pill">
            <span>Overall</span>
            <strong>{{ Math.round(scores.overall_score) }}</strong>
          </div>
          <div class="score-pill">
            <span>Projects</span>
            <strong>{{ Math.round(scores.projects_score) }}</strong>
          </div>
          <div class="score-pill">
            <span>Experience</span>
            <strong>{{ Math.round(scores.experience_score) }}</strong>
          </div>
          <div class="score-pill">
            <span>Education</span>
            <strong>{{ Math.round(scores.education_score) }}</strong>
          </div>
          <div class="score-pill">
            <span>Skills</span>
            <strong>{{ Math.round(scores.skills_score) }}</strong>
          </div>
        </div>
        <p v-else class="muted">No saved score yet. Review a CV first to create a reusable profile record.</p>
      </section>

      <section class="info-card">
        <p class="section-kicker">Storage</p>
        <h2>Profile database status</h2>
        <p><strong>Active sessions:</strong> {{ sessions.length }}</p>
        <p class="muted">Each saved score and generated profile becomes easier to revisit later or surface in profile search.</p>
      </section>

      <section class="info-card">
        <p class="section-kicker">Workflow</p>
        <h2>What this workspace supports</h2>
        <ul class="clean-list">
          <li>Review incoming CVs and assign a structured score.</li>
          <li>Store structured profile records for later access.</li>
          <li>Generate profile-style CV pages from uploaded documents.</li>
          <li>Search profiles by score thresholds and text signals.</li>
        </ul>
      </section>
    </div>
  </AppPageShell>
</template>
