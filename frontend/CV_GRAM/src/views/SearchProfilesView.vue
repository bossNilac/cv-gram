<script setup>
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import AppNav from '@/components/AppNav.vue'
import AppPageShell from '@/components/AppPageShell.vue'
import { profileAPI } from '../../util/apis.js'

const filters = ref({
  q_name: '',
  q_location: '',
  q_experience: '',
  q_education: '',
  overall_min: '',
  skills_min: '',
  experience_min: '',
})

const loading = ref(false)
const errorMsg = ref('')
const results = ref([])

const hasTextSearch = computed(() =>
  [filters.value.q_name, filters.value.q_location, filters.value.q_experience, filters.value.q_education]
    .some((value) => String(value || '').trim().length > 0),
)

function parseProfileJson(profileJson) {
  if (!profileJson) {
    return null
  }

  try {
    const parsed = typeof profileJson === 'string' ? JSON.parse(profileJson) : profileJson
    return parsed.profile || parsed
  } catch {
    return null
  }
}

async function searchProfiles() {
  loading.value = true
  errorMsg.value = ''

  try {
    const response = await profileAPI.search(filters.value)
    results.value = Array.isArray(response) ? response : []
  } catch (error) {
    errorMsg.value = error.message || 'Search failed'
  } finally {
    loading.value = false
  }
}

function displayRank(rank) {
  const numericRank = Number(rank)
  return numericRank > 0 ? numericRank.toFixed(2) : 'N/A'
}
</script>

<template>
  <AppPageShell title="Search." subtitle="Search ranked profiles by score thresholds, background text, and profile signals to surface the right people faster.">
    <AppNav />

    <section class="search-layout">
      <form class="info-card form-stack search-filters" @submit.prevent="searchProfiles">
        <p class="section-kicker">Query</p>
        <h2>Search filters</h2>
        <label class="field-label">
          Name
          <input v-model="filters.q_name" class="text-input" placeholder="Name" type="text" />
        </label>
        <label class="field-label">
          Location
          <input v-model="filters.q_location" class="text-input" placeholder="City or region" type="text" />
        </label>
        <label class="field-label">
          Experience text
          <input v-model="filters.q_experience" class="text-input" placeholder="Python, backend, data..." type="text" />
        </label>
        <label class="field-label">
          Education text
          <input v-model="filters.q_education" class="text-input" placeholder="Computer science, MBA..." type="text" />
        </label>
        <label class="field-label">
          Min overall score
          <input v-model="filters.overall_min" class="text-input" placeholder="70" type="number" />
        </label>
        <label class="field-label">
          Min skills score
          <input v-model="filters.skills_min" class="text-input" placeholder="60" type="number" />
        </label>
        <label class="field-label">
          Min experience score
          <input v-model="filters.experience_min" class="text-input" placeholder="60" type="number" />
        </label>
        <div class="button-row">
          <button class="primary-button" type="submit">{{ loading ? 'Searching...' : 'Search profiles' }}</button>
        </div>
      </form>

      <section class="search-results">
        <div class="results-toolbar">
          <p class="muted">
            {{ results.length }} {{ results.length === 1 ? 'result' : 'results' }}
            <span v-if="hasTextSearch"> ranked by match strength when available.</span>
            <span v-else"> sorted by the backend search output. Add text filters for a meaningful relevance rank.</span>
          </p>
        </div>

        <div v-if="errorMsg" class="status-message error">{{ errorMsg }}</div>
        <div v-if="loading" class="status-message success">Searching profiles...</div>

        <article v-for="(item, index) in results" :key="item.user_id" class="list-card search-result-card">
          <div class="result-header">
            <div>
              <p class="section-kicker">Profile</p>
              <h2>{{ parseProfileJson(item.profile_json)?.basics?.full_name || item.user_id }}</h2>
            </div>
            <RouterLink class="result-link" :to="`/profile/${item.user_id}`">Open profile</RouterLink>
          </div>
          <p>{{ parseProfileJson(item.profile_json)?.basics?.headline || 'No headline available' }}</p>
          <p class="muted">{{ parseProfileJson(item.profile_json)?.basics?.location || 'No location' }}</p>

          <div class="score-grid result-metrics">
            <div class="score-pill">
              <span>Overall</span>
              <strong>{{ Math.round(item.overall_score) }}</strong>
            </div>
            <div class="score-pill">
              <span>{{ hasTextSearch ? 'Relevance' : 'Position' }}</span>
              <strong>{{ hasTextSearch ? displayRank(item.rank) : index + 1 }}</strong>
            </div>
          </div>

          <div class="inline-list">
            <span v-for="skill in (parseProfileJson(item.profile_json)?.skills || []).slice(0, 6)" :key="skill">
              {{ skill }}
            </span>
          </div>
        </article>

        <p v-if="!loading && results.length === 0" class="muted">No results yet. Run a search first.</p>
      </section>
    </section>
  </AppPageShell>
</template>

<style scoped>
.search-layout {
  display: grid;
  grid-template-columns: minmax(280px, 340px) minmax(0, 1fr);
  gap: 1rem;
  align-items: start;
}

.search-filters {
  position: sticky;
  top: 1rem;
}

.search-results {
  min-width: 0;
  max-height: 72vh;
  overflow: auto;
  padding-right: 0.25rem;
  display: grid;
  gap: 0.85rem;
}

.results-toolbar {
  padding: 0.2rem 0.2rem 0 0.2rem;
}

.search-result-card {
  min-width: 0;
}

.result-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.35rem;
}

.result-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
  padding: 0.55rem 0.9rem;
  border-radius: 999px;
  background: var(--color-accent);
  color: white;
  font-size: 0.92rem;
}

.result-metrics {
  margin: 0.8rem 0;
}

@media (max-width: 900px) {
  .search-layout {
    grid-template-columns: 1fr;
  }

  .search-filters {
    position: static;
  }

  .search-results {
    max-height: none;
    overflow: visible;
    padding-right: 0;
  }

  .result-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
