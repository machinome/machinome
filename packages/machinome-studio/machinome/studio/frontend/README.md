# shop-floor frontend

The shop-floor browser interface is a TypeScript React application built with
Vite.

Install dependencies once:

```text
npm install
```

For frontend development, start the shop-floor service on its default port,
9000, and run:

```text
npm run dev
```

Vite proxies `/api` requests to that local service.  To produce the assets
served by the shop-floor service, run:

```text
npm run build
```

Use `npm run test` for the TypeScript check.  From the repository root,
`scripts/test-e2e` builds the frontend and runs the Python Playwright browser
test; install its dependency with `python -m pip install -e '.[e2e]'`.
