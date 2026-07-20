import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

test('the already-open page changes closed then open as SSE reconnects', () => {
  const source = readFileSync('src/shop_floor/app.py', 'utf8');
  const script = source.match(/<script>([\s\S]*?)<\/script>/)[1];
  const status = { textContent: 'Shop is closed' };

  class FakeEventSource {
    constructor(url) {
      this.url = url;
      FakeEventSource.connection = this;
    }
  }

  vm.runInNewContext(script, {
    EventSource: FakeEventSource,
    document: { getElementById: () => status },
  });

  const connection = FakeEventSource.connection;
  assert.equal(connection.url, '/events/lifecycle');
  connection.onopen();
  assert.equal(status.textContent, 'Shop is open');
  connection.onerror();
  assert.equal(status.textContent, 'Shop is closed');
  connection.onopen();
  assert.equal(status.textContent, 'Shop is open');
});
