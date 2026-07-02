# Screenshots

`*_live_browser.png` files are real Chromium browser captures from the running FastAPI + Next.js stack.

`*_connected_demo.png` files remain lightweight data-derived preview assets for environments where Playwright browser tooling is not installed.

Generate the live browser captures with:

```bash
cd frontend
npx playwright install chromium
npm run screenshots:readme
```
