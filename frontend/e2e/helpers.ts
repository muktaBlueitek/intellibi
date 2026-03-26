import type { APIRequestContext } from '@playwright/test'

const DEFAULT_API = 'http://localhost:8000/api/v1'

export function apiBaseUrl(): string {
  return process.env.PLAYWRIGHT_API_BASE_URL || DEFAULT_API
}

export function healthUrl(): string {
  const base = apiBaseUrl().replace(/\/$/, '')
  return `${base}/health`
}

export async function isBackendReachable(request: APIRequestContext): Promise<boolean> {
  try {
    const res = await request.get(healthUrl(), { timeout: 5000 })
    return res.ok()
  } catch {
    return false
  }
}

export async function loginForToken(
  request: APIRequestContext,
  username: string,
  password: string
): Promise<string> {
  const res = await request.post(`${apiBaseUrl().replace(/\/$/, '')}/auth/login`, {
    form: { username, password },
  })
  if (!res.ok()) {
    const body = await res.text()
    throw new Error(`Login failed ${res.status()}: ${body}`)
  }
  const json = (await res.json()) as { access_token: string }
  return json.access_token
}

export const E2E_ADMIN_USER = process.env.E2E_ADMIN_USER || 'admin'
export const E2E_ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD || 'admin123'
