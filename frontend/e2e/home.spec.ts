import { test, expect } from '@playwright/test'

test.describe('Home and Auth flow', () => {
  test('home page redirects to login when not authenticated', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveURL(/.*login/)
    await expect(page.getByRole('heading', { name: /login/i })).toBeVisible({ timeout: 5000 })
  })

  test('register page is accessible', async ({ page }) => {
    await page.goto('/register')
    await expect(page.getByRole('heading', { name: /register|sign up/i })).toBeVisible({ timeout: 5000 })
  })

  test('login page has username and password fields', async ({ page }) => {
    await page.goto('/login')
    await expect(page.getByLabel(/username|email/i)).toBeVisible({ timeout: 5000 })
    await expect(page.getByLabel(/password/i)).toBeVisible({ timeout: 5000 })
  })
})
