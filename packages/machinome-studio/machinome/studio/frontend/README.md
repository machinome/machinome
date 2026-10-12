# shop-floor frontend

The shop-floor browser interface is a TypeScript React application built with
Vite, the third member of the machinome repository's npm workspace
(`@machinome/studio`); it keeps no lock of its own, the root's
`package-lock.json` holding its resolutions.

Install the workspace's dependencies once, from the repository's root:

```text
npm ci
```

For frontend development, start the shop-floor service on its default port,
9000, and run, from the root:

```text
npm run dev --workspace packages/machinome-studio/machinome/studio/frontend
```

Vite proxies `/api` requests to that local service. To produce the assets
served by the shop-floor service, `static/` beside the package's modules,
run from the root:

```text
npm run build --workspace packages/machinome-studio/machinome/studio/frontend
```

`public/assets/` holds what the build copies to `static/assets/`
unchanged: the Machinome identity release under `brand/v1/`, the studio's
favicon pack under `favicon/` (built from that release's symbol by
`scripts/build-favicon`) and the two interface fonts under `fonts/`, each
directory with its own README and, for the fonts and the release, licence
notices. Both are served by the floor's `/assets` route.

`npm test --workspace packages/machinome-studio/machinome/studio/frontend`
runs the TypeScript check. `make test PKG=machinome-studio`, from the root,
checks and builds the frontend and runs the studio's tests; its browser
tests run when `MACHINOME_STUDIO_E2E=1` is set, as `scripts/test-e2e` sets
it.
