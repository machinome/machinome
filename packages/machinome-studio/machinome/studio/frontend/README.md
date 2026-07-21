# shop-floor frontend

The shop-floor browser interface is a TypeScript React application built with
Vite.

Install dependencies once:

```text
npm --prefix floor/frontend install
```

For frontend development, start the shop-floor service on its default port,
9000, and run:

```text
npm --prefix floor/frontend run dev
```

Vite proxies `/api` requests to that local service.  To produce the assets
served by the shop-floor service, run:

```text
npm --prefix floor/frontend run build
```

Use `npm --prefix floor/frontend run test` for the TypeScript check. From the repository root,
`scripts/test-e2e` builds the frontend and runs the Python Playwright browser
test; install its dependency with `python -m pip install -e '.[e2e]'`.
