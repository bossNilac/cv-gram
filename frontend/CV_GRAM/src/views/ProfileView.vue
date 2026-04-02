<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import AppNav from '@/components/AppNav.vue'
import AppPageShell from '@/components/AppPageShell.vue'
import { profileAPI } from '../../util/apis.js'
import { formatDateRange } from '@/utils/formatters.js'

const route = useRoute()
const loading = ref(true)
const errorMsg = ref('')
const record = ref(null)

const targetUserId = computed(() => route.params.userId || '')

function normalizeProfileJson(profileJson) {
  if (!profileJson) {
    return null
  }

  const parsed = typeof profileJson === 'string' ? JSON.parse(profileJson) : profileJson
  return parsed.profile || parsed
}

const profile = computed(() => {
  try {
    return normalizeProfileJson(record.value?.profile_json)
  } catch {
    return null
  }
})

async function loadProfile() {
  loading.value = true
  errorMsg.value = ''

  try {
    record.value = targetUserId.value
      ? await profileAPI.getUserProfile(targetUserId.value)
      : await profileAPI.getMyProfile()
  } catch (error) {
    errorMsg.value = error.message || 'Failed to load profile'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadProfile()
})

watch(targetUserId, () => {
  loadProfile()
})
</script>

<template>
  <AppPageShell title="Profile." subtitle="A structured CV record designed for review, ranking context, and discoverability inside the wider profile database.">
    <AppNav />

    <div v-if="loading" class="status-message success">Loading profile...</div>
    <div v-else-if="errorMsg" class="status-message error">{{ errorMsg }}</div>

    <section v-else class="page-grid">
      <div class="info-card">
        <p class="section-kicker">Ranking</p>
        <h2>Assessment summary</h2>
        <div class="score-grid">
          <div class="score-pill">
            <span>Overall</span>
            <strong>{{ Math.round(record.overall_score) }}</strong>
          </div>
          <div class="score-pill">
            <span>Projects</span>
            <strong>{{ Math.round(record.projects_score) }}</strong>
          </div>
          <div class="score-pill">
            <span>Experience</span>
            <strong>{{ Math.round(record.experience_score) }}</strong>
          </div>
          <div class="score-pill">
            <span>Education</span>
            <strong>{{ Math.round(record.education_score) }}</strong>
          </div>
          <div class="score-pill">
            <span>Skills</span>
            <strong>{{ Math.round(record.skills_score) }}</strong>
          </div>
        </div>
      </div>

      <div class="info-card">
        <p class="section-kicker">Identity</p>
        <h2>Profile overview</h2>
        <p><strong>Name:</strong> {{ profile?.basics?.full_name || 'Unknown' }}</p>
        <p><strong>Headline:</strong> {{ profile?.basics?.headline || 'No headline' }}</p>
        <p><strong>Email:</strong> {{ profile?.basics?.email || 'No email in profile JSON' }}</p>
        <p><strong>Location:</strong> {{ profile?.basics?.location || 'No location' }}</p>
        <p class="muted">{{ profile?.basics?.summary || 'No summary available.' }}</p>
      </div>

      <div class="info-card">
        <p class="section-kicker">Capabilities</p>
        <h2>Skill signals</h2>
        <div class="inline-list">
          <span v-for="skill in profile?.skills || []" :key="skill">{{ skill }}</span>
        </div>
        <p v-if="!(profile?.skills || []).length" class="muted">No skill list stored yet.</p>
      </div>

      <div class="info-card">
        <p class="section-kicker">Background</p>
        <h2>Experience history</h2>
        <div class="stack-list">
          <article v-for="item in profile?.experience || []" :key="`${item.company}-${item.title}`">
            <h3>{{ item.title }} @ {{ item.company }}</h3>
            <p class="muted">{{ formatDateRange(item.start_date, item.end_date) }}</p>
            <p>{{ item.description }}</p>
          </article>
        </div>
        <p v-if="!(profile?.experience || []).length" class="muted">No experience items available.</p>
      </div>

      <div class="info-card">
        <p class="section-kicker">Education</p>
        <h2>Academic record</h2>
        <div class="stack-list">
          <article v-for="item in profile?.education || []" :key="`${item.school}-${item.degree}`">
            <h3>{{ item.school }}</h3>
            <p>{{ item.degree }} {{ item.field_of_study ? `- ${item.field_of_study}` : '' }}</p>
            <p class="muted">{{ formatDateRange(item.start_date, item.end_date) }}</p>
          </article>
        </div>
      </div>

      <div class="info-card">
        <p class="section-kicker">Portfolio</p>
        <h2>Projects and proof</h2>
        <div class="stack-list">
          <article v-for="project in profile?.projects || []" :key="project.name">
            <h3>{{ project.name }}</h3>
            <p>{{ project.description }}</p>
            <div class="inline-list">
              <span v-for="tech in project.tech || []" :key="tech">{{ tech }}</span>
            </div>
          </article>
        </div>
      </div>

      <div class="info-card">
        <p class="section-kicker">Actions</p>
        <h2>Next steps</h2>
        <p class="muted">Refresh this profile from a newer CV or move back into search to compare profiles.</p>
        <div class="button-row">
          <RouterLink class="secondary-button" to="/score">Update from CV</RouterLink>
          <RouterLink class="secondary-button" to="/search">Search profiles</RouterLink>
        </div>
      </div>
    </section>
  </AppPageShell>
</template>
