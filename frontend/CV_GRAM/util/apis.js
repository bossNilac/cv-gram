import router from '@/router/index.js'

const defaultApiBase = import.meta.env.DEV
  ? `${window.location.protocol}//${window.location.hostname}:8000`
  : window.location.origin

const API_BASE = import.meta.env.VITE_API_BASE || defaultApiBase

function buildUrl(endpoint) {
  return `${API_BASE}${endpoint}`
}

function toQueryString(params = {}) {
  const searchParams = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value === '' || value === null || value === undefined) {
      return
    }

    searchParams.set(key, value)
  })

  const query = searchParams.toString()
  return query ? `?${query}` : ''
}

async function readResponse(response) {
  if (response.status === 204) {
    return null
  }

  const contentType = response.headers.get('content-type') || ''

  if (contentType.includes('application/json')) {
    return response.json()
  }

  const text = await response.text()
  return text ? { message: text } : null
}

async function apiRequest(endpoint, options = {}) {
  const { headers = {}, body, skipAuthRedirect = false, ...rest } = options
  const isFormData = body instanceof FormData
  const requestHeaders = new Headers(headers)

  if (!isFormData && body !== undefined && !requestHeaders.has('Content-Type')) {
    requestHeaders.set('Content-Type', 'application/json')
  }

  if (!requestHeaders.has('Accept')) {
    requestHeaders.set('Accept', 'application/json')
  }

  const response = await fetch(buildUrl(endpoint), {
    credentials: 'include',
    ...rest,
    headers: requestHeaders,
    body,
  })

  const payload = await readResponse(response)

  if (!response.ok) {
    const message =
      payload?.detail || payload?.message || `Request failed with status ${response.status}`

    if (response.status === 401 && !skipAuthRedirect) {
      await router.push('/login')
    }

    throw new Error(message)
  }

  return payload
}

function createFileFormData(file) {
  const formData = new FormData()
  formData.append('file', file)
  return formData
}

export const authAPI = {
  async login(email, password) {
    await apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
      skipAuthRedirect: true,
    })

    await router.push('/dashboard')
  },

  async register(email, password) {
    return apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
      skipAuthRedirect: true,
    })
  },

  async forgotPassword(email) {
    return apiRequest('/auth/password/forgot', {
      method: 'POST',
      body: JSON.stringify({ email }),
      skipAuthRedirect: true,
    })
  },

  async resetPassword(token, newPassword) {
    return apiRequest('/auth/password/reset', {
      method: 'POST',
      body: JSON.stringify({ token, new_password: newPassword }),
      skipAuthRedirect: true,
    })
  },

  async verifyEmail(token) {
    return apiRequest('/auth/verify-mail', {
      method: 'POST',
      body: JSON.stringify({ token }),
      skipAuthRedirect: true,
    })
  },

  async getMe() {
    return apiRequest('/auth/me', { method: 'POST' })
  },

  async logout() {
    await apiRequest('/auth/logout', { method: 'POST' })
    await router.push('/')
  },

  async logoutAll() {
    await apiRequest('/auth/logout_all', { method: 'POST' })
    await router.push('/login')
  },

  async getSessions() {
    return apiRequest('/auth/sessions')
  },

  async deleteSession(sessionId) {
    return apiRequest(`/auth/sessions/${sessionId}`, {
      method: 'DELETE',
    })
  },
}

export const resumeAPI = {
  async getHealth() {
    return apiRequest('/parser/health')
  },

  async getAdvancedHealth() {
    return apiRequest('/parser/adv/health')
  },

  async scoreResume(file) {
    return apiRequest('/parser/resume/score', {
      method: 'POST',
      body: createFileFormData(file),
    })
  },

  async saveResumeScore(file) {
    return apiRequest('/parser/resume/score', {
      method: 'PUT',
      body: createFileFormData(file),
    })
  },

  async startAdvancedScore(file) {
    return apiRequest('/parser/resume/adv/score_async', {
      method: 'POST',
      body: createFileFormData(file),
    })
  },

  async getTaskStatus(taskId) {
    return apiRequest(`/parser/resume/task_status/${taskId}`)
  },

  async getTaskResult(taskId) {
    return apiRequest(`/parser/resume/result/${taskId}`)
  },

  async generateProfile(file) {
    return apiRequest('/parser/resume/cv', {
      method: 'POST',
      body: createFileFormData(file),
    })
  },
}

export const profileAPI = {
  async getMyScores() {
    return apiRequest('/profiles/resume-scores')
  },

  async getUserScores(userId) {
    return apiRequest(`/profiles/resume-scores/${userId}`)
  },

  async getMyProfile() {
    return apiRequest('/profiles/me')
  },

  async getUserProfile(userId) {
    return apiRequest(`/profiles/user/${userId}`)
  },

  async search(params = {}) {
    return apiRequest(`/profiles/search/${toQueryString(params)}`)
  },
}

export { API_BASE, apiRequest }
