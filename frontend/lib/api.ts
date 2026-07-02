export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export type ApiError = { message: string; status?: number }

export function getToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('workflowops_token')
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = { ...(options.headers as Record<string, string> || {}) }
  if (!(options.body instanceof FormData)) headers['Content-Type'] = headers['Content-Type'] || 'application/json'
  if (token) headers.Authorization = `Bearer ${token}`
  const res = await fetch(`${API_URL}${path}`, { ...options, headers })
  if (!res.ok) {
    const text = await res.text()
    throw { message: text || res.statusText, status: res.status } satisfies ApiError
  }
  const contentType = res.headers.get('content-type') || ''
  if (contentType.includes('application/json')) return res.json() as Promise<T>
  return (await res.text()) as T
}

export async function login(email: string, password: string) {
  const result = await apiFetch<{ access_token: string; user: any }>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) })
  localStorage.setItem('workflowops_token', result.access_token)
  localStorage.setItem('workflowops_user', JSON.stringify(result.user))
  return result
}

export function logout() {
  localStorage.removeItem('workflowops_token')
  localStorage.removeItem('workflowops_user')
}
