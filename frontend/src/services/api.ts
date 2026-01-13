import axios, { AxiosError, AxiosResponse } from 'axios'
import { useAuthStore } from '../stores/authStore'

const API_BASE_URL = '/api/v1'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as any

    // Handle 401 errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const refreshToken = useAuthStore.getState().refreshToken
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          })

          const { access_token, refresh_token } = response.data.data
          useAuthStore.getState().login({
            accessToken: access_token,
            refreshToken: refresh_token,
            user: useAuthStore.getState().user!,
          })

          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        } catch (refreshError) {
          useAuthStore.getState().logout()
          window.location.href = '/login'
        }
      } else {
        useAuthStore.getState().logout()
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

// API response type
interface APIResponse<T> {
  code: number
  message: string
  data: T
}

// Auth API
export const authAPI = {
  login: (username: string, password: string) =>
    api.post<APIResponse<{
      access_token: string
      refresh_token: string
      user: any
    }>>('/auth/login', { username, password }),
  
  logout: () => api.post('/auth/logout'),
  
  me: () => api.get<APIResponse<any>>('/auth/me'),
}

// Task API
export const taskAPI = {
  list: (params?: any) => api.get<APIResponse<any>>('/tasks', { params }),
  
  get: (id: string) => api.get<APIResponse<any>>(`/tasks/${id}`),
  
  create: (data: any) => api.post<APIResponse<any>>('/tasks', data),
  
  update: (id: string, data: any) => api.put<APIResponse<any>>(`/tasks/${id}`, data),
  
  delete: (id: string) => api.delete(`/tasks/${id}`),
  
  action: (id: string, action: string) =>
    api.post<APIResponse<any>>(`/tasks/${id}/actions`, { action }),
  
  getExecutions: (id: string) =>
    api.get<APIResponse<any>>(`/tasks/${id}/executions`),
  
  getResults: (taskId: string, executionId: string) =>
    api.get<APIResponse<any>>(`/tasks/${taskId}/executions/${executionId}/results`),
}

// Environment API
export const environmentAPI = {
  list: (params?: any) => api.get<APIResponse<any>>('/environments', { params }),
  
  get: (id: string) => api.get<APIResponse<any>>(`/environments/${id}`),
  
  create: (data: any) => api.post<APIResponse<any>>('/environments', data),
  
  update: (id: string, data: any) => api.put<APIResponse<any>>(`/environments/${id}`, data),
  
  delete: (id: string) => api.delete(`/environments/${id}`),
  
  action: (id: string, action: string) =>
    api.post<APIResponse<any>>(`/environments/${id}/actions`, { action }),
  
  reserve: (id: string, data: any) =>
    api.post<APIResponse<any>>(`/environments/${id}/reserve`, data),
  
  // Hosts
  listHosts: (params?: any) => api.get<APIResponse<any>>('/environments/hosts', { params }),
  
  createHost: (data: any) => api.post<APIResponse<any>>('/environments/hosts', data),
  
  // Devices
  listDevices: (params?: any) => api.get<APIResponse<any>>('/environments/devices', { params }),
  
  createDevice: (data: any) => api.post<APIResponse<any>>('/environments/devices', data),
}

// Test Suite API
export const testSuiteAPI = {
  list: (params?: any) => api.get<APIResponse<any>>('/test-suites', { params }),
  
  get: (id: string) => api.get<APIResponse<any>>(`/test-suites/${id}`),
  
  create: (data: any) => api.post<APIResponse<any>>('/test-suites', data),
  
  update: (id: string, data: any) => api.put<APIResponse<any>>(`/test-suites/${id}`, data),
  
  delete: (id: string) => api.delete(`/test-suites/${id}`),
  
  sync: (id: string) => api.post<APIResponse<any>>(`/test-suites/${id}/sync`),
  
  // Test Cases
  listCases: (suiteId: string, params?: any) =>
    api.get<APIResponse<any>>(`/test-suites/${suiteId}/cases`, { params }),
  
  createCase: (data: any) => api.post<APIResponse<any>>('/test-suites/cases', data),
  
  updateCase: (id: string, data: any) =>
    api.put<APIResponse<any>>(`/test-suites/cases/${id}`, data),
  
  deleteCase: (id: string) => api.delete(`/test-suites/cases/${id}`),
}

// Report API
export const reportAPI = {
  list: (params?: any) => api.get<APIResponse<any>>('/reports', { params }),
  
  get: (id: string) => api.get<APIResponse<any>>(`/reports/${id}`),
  
  getStatistics: (params?: any) =>
    api.get<APIResponse<any>>('/reports/statistics', { params }),
  
  export: (id: string, format: string) =>
    api.get(`/reports/${id}/export`, { params: { format }, responseType: 'blob' }),
}

// Project API
export const projectAPI = {
  list: (params?: any) => api.get<APIResponse<any>>('/projects', { params }),
  
  get: (id: string) => api.get<APIResponse<any>>(`/projects/${id}`),
  
  create: (data: any) => api.post<APIResponse<any>>('/projects', data),
  
  update: (id: string, data: any) => api.put<APIResponse<any>>(`/projects/${id}`, data),
  
  delete: (id: string) => api.delete(`/projects/${id}`),
}

// Integration API
export const integrationAPI = {
  listConfigs: (params?: any) =>
    api.get<APIResponse<any>>('/integrations/configs', { params }),
  
  createConfig: (data: any) =>
    api.post<APIResponse<any>>('/integrations/configs', data),
  
  syncALM: (data: any) => api.post<APIResponse<any>>('/integrations/alm/sync', data),
  
  listArtifactVersions: (params?: any) =>
    api.get<APIResponse<any>>('/integrations/artifact/versions', { params }),
}

export default api
