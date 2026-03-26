import { test, expect } from '@playwright/test'
import path from 'path'
import {
  apiBaseUrl,
  E2E_ADMIN_PASSWORD,
  E2E_ADMIN_USER,
  isBackendReachable,
  loginForToken,
} from './helpers'

test.describe('Core product flows', () => {
  test.beforeEach(async ({ request }) => {
    const up = await isBackendReachable(request)
    test.skip(!up, `Backend not reachable at ${apiBaseUrl()} (start API and ensure admin user exists)`)
  })

  test('login, create dashboard, add widget via API, see widget on dashboard', async ({
    page,
    request,
  }) => {
    await page.goto('/login')
    await page.getByLabel('Username').fill(E2E_ADMIN_USER)
    await page.getByLabel('Password').fill(E2E_ADMIN_PASSWORD)
    await page.getByRole('button', { name: 'Login' }).click()
    await expect(page).not.toHaveURL(/\/login/, { timeout: 15000 })

    await page.goto('/dashboards')
    await expect(page.getByRole('heading', { name: 'My Dashboards' })).toBeVisible()

    await page.getByRole('button', { name: '+ Create Dashboard' }).click()
    await expect(page.getByRole('heading', { name: 'Create New Dashboard' })).toBeVisible()

    const dashName = `E2E Dashboard ${Date.now()}`
    await page.getByPlaceholder('Enter dashboard name').fill(dashName)
    await page.getByRole('button', { name: 'Create' }).click()

    await expect(page).toHaveURL(/\/dashboards\/\d+/$/, { timeout: 15000 })
    await expect(page.getByRole('heading', { level: 1, name: dashName })).toBeVisible()

    const match = page.url().match(/\/dashboards\/(\d+)/)
    const dashboardId = match ? Number(match[1]) : NaN
    expect(dashboardId).toBeGreaterThan(0)

    const token = await loginForToken(request, E2E_ADMIN_USER, E2E_ADMIN_PASSWORD)
    const widgetRes = await request.post(`${apiBaseUrl().replace(/\/$/, '')}/widgets/`, {
      headers: { Authorization: `Bearer ${token}` },
      data: {
        dashboard_id: dashboardId,
        name: 'E2E text widget',
        type: 'text',
        description: 'Smoke test widget',
        position_x: 0,
        position_y: 0,
        width: 4,
        height: 3,
      },
    })
    expect(widgetRes.ok()).toBeTruthy()

    await page.reload()
    await expect(page.getByText('E2E text widget')).toBeVisible({ timeout: 15000 })
  })

  test('data sources: upload CSV fixture', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel('Username').fill(E2E_ADMIN_USER)
    await page.getByLabel('Password').fill(E2E_ADMIN_PASSWORD)
    await page.getByRole('button', { name: 'Login' }).click()
    await expect(page).not.toHaveURL(/\/login/, { timeout: 15000 })

    await page.goto('/datasources')
    await expect(page.getByRole('heading', { name: 'Data Sources' })).toBeVisible()

    await page.getByRole('button', { name: '+ Upload File' }).click()
    await expect(page.getByRole('heading', { name: 'Upload File' })).toBeVisible()

    const filePath = path.join(__dirname, 'fixtures', 'sample.csv')
    await page.locator('input[type="file"]').setInputFiles(filePath)
    await expect(page.getByText('sample.csv')).toBeVisible({ timeout: 20000 })

    await page.getByRole('button', { name: 'Upload' }).click()
    await expect(page.getByRole('heading', { name: 'Data Sources' })).toBeVisible({ timeout: 30000 })
    await expect(page.getByText('sample.csv').first()).toBeVisible()
  })

  test('chatbot: load page and send a message', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel('Username').fill(E2E_ADMIN_USER)
    await page.getByLabel('Password').fill(E2E_ADMIN_PASSWORD)
    await page.getByRole('button', { name: 'Login' }).click()
    await expect(page).not.toHaveURL(/\/login/, { timeout: 15000 })

    await page.goto('/chatbot')
    await expect(page.getByRole('heading', { name: 'AI Chatbot' })).toBeVisible()

    await page.getByRole('textbox', { name: 'Message' }).fill('Hello from E2E')
    await page.getByRole('button', { name: 'Send' }).click()

    await expect(page.getByRole('button', { name: 'Send' })).toBeDisabled({ timeout: 2000 })
    await expect(page.getByRole('button', { name: 'Send' })).toBeEnabled({ timeout: 60000 })
  })
})
