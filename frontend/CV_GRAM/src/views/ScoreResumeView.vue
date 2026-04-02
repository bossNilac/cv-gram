<script setup>
import { onUnmounted, ref } from 'vue'
import AppNav from '@/components/AppNav.vue'
import AppPageShell from '@/components/AppPageShell.vue'
import { resumeAPI } from '../../util/apis.js'

const selectedFile = ref(null)
const loading = ref(false)
const taskStatus = ref(null)
const scoreResult = ref(null)
const profileResult = ref(null)
const statusMsg = ref('')
const errorMsg = ref('')
let pollTimer = null

function onFileChange(event) {
  selectedFile.value = event.target.files?.[0] || null
}

function clearFile() {
  selectedFile.value = null
}

function ensureFile() {
  if (!selectedFile.value) {
    errorMsg.value = 'Select a PDF, DOC, or DOCX file first.'
    return false
  }

  return true
}

function resetMessages() {
  statusMsg.value = ''
  errorMsg.value = ''
}

async function runAction(action) {
  if (loading.value || !ensureFile()) {
    return
  }

  loading.value = true
  resetMessages()

  try {
    const result = await action(selectedFile.value)

    if (result?.score !== undefined) {
      scoreResult.value = result
    } else if (result?.profile) {
      profileResult.value = result.profile
    }

    statusMsg.value = 'Done.'
  } catch (error) {
    errorMsg.value = error.message || 'Request failed'
  } finally {
    loading.value = false
  }
}

async function startAdvancedScore() {
  if (loading.value || !ensureFile()) {
    return
  }

  loading.value = true
  resetMessages()
  taskStatus.value = null

  try {
    const response = await resumeAPI.startAdvancedScore(selectedFile.value)
    statusMsg.value = `Advanced review started. Task ID: ${response.proc_id}`
    await pollTask(response.proc_id)
  } catch (error) {
    errorMsg.value = error.message || 'Advanced scoring failed to start'
  } finally {
    loading.value = false
  }
}

async function pollTask(taskId) {
  if (!taskId) {
    return
  }

  if (pollTimer) {
    clearTimeout(pollTimer)
  }

  try {
    const status = await resumeAPI.getTaskStatus(taskId)
    taskStatus.value = status

    if (status.status === 'done') {
      scoreResult.value = await resumeAPI.getTaskResult(taskId)
      statusMsg.value = 'Advanced review finished.'
      return
    }

    if (status.status === 'failed') {
      errorMsg.value = 'Advanced scoring failed on the server.'
      return
    }

    pollTimer = window.setTimeout(() => pollTask(taskId), 2000)
  } catch (error) {
    errorMsg.value = error.message || 'Failed to poll task status'
  }
}

onUnmounted(() => {
  if (pollTimer) {
    clearTimeout(pollTimer)
  }
})
</script>

<template>
  <AppPageShell title="CV Review." subtitle="Turn a raw CV into a ranked profile record, store the score, and generate a professional page that can later be found through search.">
    <AppNav />

    <section class="page-grid">
      <div class="info-card">
        <p class="section-kicker">Intake</p>
        <h2>CV upload</h2>
        <div class="form-stack">
          <div class="upload-card">
            <div>
              <p class="upload-label">CV file</p>
              <p class="muted">Upload a PDF, DOC, or DOCX to review the CV, save the score, or build a searchable profile page.</p>
            </div>

            <div class="upload-actions">
              <label class="secondary-button upload-trigger" for="resume-file-input">Choose file</label>
              <button v-if="selectedFile" class="danger-button" type="button" @click="clearFile">Remove file</button>
            </div>

            <input
              id="resume-file-input"
              class="sr-only-file-input"
              type="file"
              accept=".pdf,.doc,.docx"
              @change="onFileChange"
            />

            <div class="upload-summary">
              <strong>{{ selectedFile ? selectedFile.name : 'No file selected yet.' }}</strong>
              <span class="muted">
                {{ selectedFile ? `${Math.max(1, Math.round(selectedFile.size / 1024))} KB ready to upload` : 'Pick one file to unlock the actions below.' }}
              </span>
            </div>
          </div>

          <div class="button-row">
            <button class="primary-button" type="button" @click="runAction(resumeAPI.scoreResume)">
              {{ loading ? 'Working...' : 'Review CV' }}
            </button>
            <button class="secondary-button" type="button" @click="runAction(resumeAPI.saveResumeScore)">
              Save score
            </button>
            <button class="secondary-button" type="button" @click="startAdvancedScore">
              Run advanced review
            </button>
            <button class="secondary-button" type="button" @click="runAction(resumeAPI.generateProfile)">
              Generate profile
            </button>
          </div>
        </div>

        <div v-if="statusMsg" class="status-message success">{{ statusMsg }}</div>
        <div v-if="errorMsg" class="status-message error">{{ errorMsg }}</div>

        <div v-if="taskStatus" class="result-card">
          <p class="section-kicker">Processing</p>
          <h2>Advanced review status</h2>
          <p><strong>Task:</strong> {{ taskStatus.proc_id }}</p>
          <p><strong>Status:</strong> {{ taskStatus.status }}</p>
          <p><strong>Stage:</strong> {{ taskStatus.stage }}</p>
          <p><strong>Progress:</strong> {{ taskStatus.progress }}%</p>
        </div>
      </div>

      <div v-if="scoreResult" class="result-card">
        <p class="section-kicker">Ranking</p>
        <h2>CV assessment</h2>
        <div class="score-grid">
          <div class="score-pill">
            <span>Overall</span>
            <strong>{{ Math.round(scoreResult.score) }}</strong>
          </div>
          <div v-for="(value, key) in scoreResult.parsed?.components || {}" :key="key" class="score-pill">
            <span>{{ key }}</span>
            <strong>{{ Math.round(value) }}</strong>
          </div>
        </div>

        <div class="stack-list" style="margin-top: 1rem;">
          <div>
            <h3>Highlights</h3>
            <ul class="clean-list">
              <li v-for="item in scoreResult.parsed?.explanation?.highlights || []" :key="item">{{ item }}</li>
            </ul>
          </div>

          <div>
            <h3>Strengths</h3>
            <ul class="clean-list">
              <li v-for="item in scoreResult.parsed?.explanation?.notes?.strengths || []" :key="item">{{ item }}</li>
            </ul>
          </div>

          <div>
            <h3>Weaknesses</h3>
            <ul class="clean-list">
              <li v-for="item in scoreResult.parsed?.explanation?.notes?.weaknesses || []" :key="item">{{ item }}</li>
            </ul>
          </div>
        </div>
      </div>

      <div v-if="profileResult" class="result-card">
        <p class="section-kicker">Publishing</p>
        <h2>Generated profile</h2>
        <p><strong>Name:</strong> {{ profileResult.basics?.full_name || 'Unknown' }}</p>
        <p><strong>Headline:</strong> {{ profileResult.basics?.headline || 'No headline yet' }}</p>
        <p><strong>Location:</strong> {{ profileResult.basics?.location || 'No location yet' }}</p>
        <div class="inline-list" style="margin-top: 0.75rem;">
          <span v-for="skill in profileResult.skills || []" :key="skill">{{ skill }}</span>
        </div>
      </div>
    </section>
  </AppPageShell>
</template>

<style scoped>
.upload-card {
  display: grid;
  gap: 0.9rem;
  padding: 1rem;
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.95), rgba(255, 240, 245, 0.85));
  border: 1px solid var(--color-border);
}

.upload-label {
  color: var(--color-heading);
  font-weight: 600;
}

.upload-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.upload-trigger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.upload-summary {
  display: grid;
  gap: 0.15rem;
  padding: 0.85rem 1rem;
  border-radius: 18px;
  background: white;
  border: 1px dashed var(--color-border);
}

.upload-summary strong {
  color: var(--color-heading);
  word-break: break-word;
}

.sr-only-file-input {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
