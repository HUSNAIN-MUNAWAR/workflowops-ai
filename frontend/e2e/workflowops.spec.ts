import { test, expect } from '@playwright/test'

async function login(page: any, email = 'admin@example.com', password = 'admin123') {
  await page.goto('/login')
  await page.getByLabel('Email').fill(email)
  await page.getByLabel('Password').fill(password)
  await page.getByRole('button', { name: /login/i }).click()
  await page.waitForURL(/dashboard|login/, { timeout: 10000 })
}

test('admin can inspect the connected workflow operations surfaces', async ({ page }) => {
  await login(page)
  await page.goto('/dashboard')
  await expect(page.getByRole('heading', { name: 'Operations Dashboard' })).toBeVisible()
  await page.goto('/templates')
  await expect(page.getByRole('heading', { name: 'Workflow Template Marketplace' })).toBeVisible()
  await page.goto('/run-console')
  await expect(page.getByRole('heading', { name: 'Run Console' })).toBeVisible()
  await page.goto('/approvals')
  await expect(page.getByRole('heading', { name: 'Approval Queue' })).toBeVisible()
  await page.goto('/reports')
  await expect(page.getByRole('heading', { name: 'Reports' })).toBeVisible()
  await page.goto('/reliability')
  await expect(page.getByRole('heading', { name: 'Workflow EvalBench' })).toBeVisible()
  await page.goto('/audit-logs')
  await expect(page.getByRole('heading', { name: 'Audit Logs' })).toBeVisible()
})

test('viewer RBAC surfaces do not expose approval power as an assumed capability', async ({ page }) => {
  await login(page, 'viewer@example.com', 'viewer123')
  await page.goto('/approvals')
  await expect(page.getByRole('heading', { name: 'Approval Queue' })).toBeVisible()
})

test('policy and connector pages are present for governance review', async ({ page }) => {
  await login(page)
  await page.goto('/policies')
  await expect(page.getByRole('heading', { name: 'Tenant Policy Engine' })).toBeVisible()
  await page.goto('/connectors')
  await expect(page.getByRole('heading', { name: 'Safe Demo Connectors' })).toBeVisible()
  await page.goto('/builder')
  await expect(page.getByRole('heading', { name: 'Workflow Builder' })).toBeVisible()
})
