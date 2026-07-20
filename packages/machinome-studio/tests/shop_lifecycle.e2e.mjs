import { execFileSync } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { test, expect } from '@playwright/test';

const root = resolve('.');
const port = 8767;
const location = `http://127.0.0.1:${port}`;
const stateDirectory = mkdtempSync(join(tmpdir(), 'shop-floor-e2e-'));
const stateFile = join(stateDirectory, 'shop-floor.pid');

function askAgent(command) {
  return execFileSync('python', [
    '-m', 'shop_floor', command,
    '--port', String(port),
    '--state-file', stateFile,
  ], {
    cwd: root,
    encoding: 'utf8',
    env: { ...process.env, PYTHONPATH: join(root, 'src') },
  });
}

test.afterAll(() => {
  try {
    askAgent('close');
  } finally {
    rmSync(stateDirectory, { recursive: true, force: true });
  }
});

test('an already-open page shows closed on shutdown and open after restart', async ({ page }) => {
  askAgent('open');
  await page.goto(location);
  const status = page.locator('#shop-status');
  await expect(status).toHaveText('Shop is open');

  askAgent('close');
  await expect(status).toHaveText('Shop is closed');

  askAgent('open');
  await expect(status).toHaveText('Shop is open');
});
