import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from '@playwright/test';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const baseUrl = process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:3000';
const apiUrl = process.env.WORKFLOWOPS_API_URL || 'http://127.0.0.1:8000';
const outDir = path.resolve(__dirname, '..', '..', 'sample_outputs', 'screenshots');

async function apiLogin(email, password) {
  const response = await fetch(`${apiUrl}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) throw new Error(`API login failed for ${email}: ${await response.text()}`);
  return response.json();
}

async function apiFetch(route, token, init = {}) {
  const headers = {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
    ...(init.headers || {}),
  };
  if (init.body === undefined) delete headers['Content-Type'];
  const response = await fetch(`${apiUrl}${route}`, { ...init, headers });
  if (!response.ok) throw new Error(`${route} failed: ${await response.text()}`);
  return response.json();
}

async function ensureConnectedDemoState() {
  const admin = await apiLogin('admin@example.com', 'admin123');
  const reviewer = await apiLogin('reviewer@example.com', 'reviewer123');

  const summary = await apiFetch('/dashboard/summary', admin.access_token);
  if (summary.total_workflow_runs < 6) {
    const runs = [
      {
        template_slug: 'compliance_evidence',
        input_payload: {
          text: 'Access review evidence package for Q2 2026 SOC 2 control mapping and control owner attestations.',
        },
      },
      {
        template_slug: 'workflow_reliability',
        input_payload: {
          text: 'Run deterministic reliability sweep for the invoice approval release candidate.',
        },
      },
      {
        template_slug: 'support_escalation',
        input_payload: {
          text: 'VIP customer is threatening legal action over a refund delay and demands immediate executive review.',
        },
      },
      {
        template_slug: 'email_to_task',
        input_payload: {
          text: 'Client asks for a statement of work update, contract redlines, and pricing approval before Friday.',
        },
      },
      {
        template_slug: 'invoice_approval',
        input_payload: {
          text: 'Invoice Number: INV-2042\nVendor: Apex Industrial Supplies\nTotal: USD 9800\nDue Date: 2026-08-25',
          action_type: 'payment_export',
        },
      },
      {
        template_slug: 'rfp_response',
        input_payload: {
          text: 'Prepare a proposal compliance matrix for a public-sector automation RFP with a mandatory security questionnaire and pricing schedule.',
        },
      },
    ];
    for (const run of runs) {
      await apiFetch('/workflow-runs', admin.access_token, {
        method: 'POST',
        body: JSON.stringify(run),
      });
    }
  }

  let approvals = await apiFetch('/approvals', reviewer.access_token);
  if (!approvals.some((item) => item.status === 'approved')) {
    const pending = approvals.find((item) => item.status === 'pending');
    if (pending) {
      await apiFetch(`/approvals/${pending.id}/approve`, reviewer.access_token, {
        method: 'POST',
        body: JSON.stringify({ reason: 'Approved during live README screenshot capture.' }),
      });
    }
  }

  approvals = await apiFetch('/approvals', reviewer.access_token);
  if (!approvals.some((item) => item.status === 'changes_requested')) {
    const pending = approvals.find((item) => item.status === 'pending');
    if (pending) {
      await apiFetch(`/approvals/${pending.id}/request-changes`, reviewer.access_token, {
        method: 'POST',
        body: JSON.stringify({ reason: 'More business context required before approval.' }),
      });
    }
  }

  const reliabilityRuns = await apiFetch('/reliability-tests', admin.access_token);
  if (!reliabilityRuns.length) {
    await apiFetch('/reliability-tests/run', admin.access_token, {
      method: 'POST',
      body: JSON.stringify({ template_slug: 'invoice_approval' }),
    });
  }
}

async function loginUi(page, email = 'admin@example.com', password = 'admin123') {
  await page.goto(`${baseUrl}/login`, { waitUntil: 'networkidle' });
  await page.getByLabel('Email').fill(email);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: /login/i }).click();
  await page.waitForURL(/dashboard/, { timeout: 15000 });
}

async function capture(page, pathname, title, fileName, beforeCapture) {
  await page.goto(`${baseUrl}${pathname}`, { waitUntil: 'networkidle' });
  await page.getByText(title).waitFor({ timeout: 15000 });
  if (beforeCapture) await beforeCapture(page);
  await page.waitForTimeout(800);
  await page.screenshot({
    path: path.join(outDir, fileName),
    fullPage: false,
  });
}

async function main() {
  await fs.mkdir(outDir, { recursive: true });
  await ensureConnectedDemoState();

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1600, height: 1080 },
    colorScheme: 'light',
  });
  const page = await context.newPage();

  try {
    await loginUi(page);
    await capture(page, '/dashboard', 'Operations Dashboard', 'dashboard_live_browser.png');
    await capture(page, '/approvals', 'Approval Queue', 'approvals_live_browser.png');
    await capture(page, '/reliability', 'Workflow EvalBench', 'reliability_live_browser.png', async (nextPage) => {
      const firstRun = nextPage.locator('button', { hasText: 'invoice_approval' }).first();
      if (await firstRun.count()) await firstRun.click();
    });
    await capture(page, '/templates', 'Workflow Template Marketplace', 'templates_live_browser.png');
  } finally {
    await browser.close();
  }

  const files = await fs.readdir(outDir);
  const liveScreens = files.filter((name) => name.endsWith('_live_browser.png')).sort();
  for (const file of liveScreens) console.log(file);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
