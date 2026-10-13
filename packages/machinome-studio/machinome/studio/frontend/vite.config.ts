// Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
// SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { dirname, join, sep } from "node:path";
import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";

/** The directory of the package a bundled module belongs to, or null for
 * a module of the frontend's own source or a virtual one. */
function packageRoot(id: string): string | null {
  if (!id.startsWith(sep)) return null;
  const parts = id.split(sep);
  const at = parts.lastIndexOf("node_modules");
  if (at < 0 || at + 1 >= parts.length) return null;
  const scoped = parts[at + 1].startsWith("@");
  const end = at + (scoped ? 3 : 2);
  if (end > parts.length) return null;
  return parts.slice(0, end).join(sep);
}

interface Notice {
  name: string;
  version: string;
  licence: string;
  source: string;
  texts: string[];
}

/** A package's notice: its name, version, licence and source as its
 * package.json states them, and the licence texts it ships. */
function notice(root: string): Notice {
  const manifest = JSON.parse(readFileSync(join(root, "package.json"), "utf8"));
  const repository = manifest.repository;
  const source =
    typeof repository === "string" ? repository
    : repository && typeof repository.url === "string" ? repository.url
    : typeof manifest.homepage === "string" ? manifest.homepage
    : "unstated";
  const texts = readdirSync(root)
    .filter((entry) => /^(licen[cs]e|copying|notice|third[-_]?party)/i.test(entry))
    .sort()
    .map((entry) => readFileSync(join(root, entry), "utf8").trim());
  return {
    name: manifest.name,
    version: manifest.version,
    licence: typeof manifest.license === "string" ? manifest.license : "unstated",
    source,
    texts,
  };
}

/** The directory of a dependency `name` as Node resolves it from `root`:
 * the nearest node_modules above `root` that holds it. */
function dependencyRoot(root: string, name: string): string | null {
  let directory = root;
  for (;;) {
    const candidate = join(directory, "node_modules", name);
    if (existsSync(join(candidate, "package.json"))) return candidate;
    const parent = dirname(directory);
    if (parent === directory) return null;
    directory = parent;
  }
}

/** Writes THIRD-PARTY-NOTICES.txt beside the built files, from the
 * packages the bundle actually holds: every package a bundled module
 * belongs to, and the runtime dependencies such a package declares and
 * ships inlined in its own files (monaco-editor carries marked and
 * DOMPurify that way, so neither is a module of the bundle). Vite's
 * minifier drops the licence comments the packages carry in their
 * sources (esbuild's legalComments is "none"), and the MIT and Apache
 * licences require their notice to accompany every copy of the code. */
function thirdPartyNotices(): Plugin {
  return {
    name: "third-party-notices",
    generateBundle(_options, bundle) {
      const roots = new Set<string>();
      for (const output of Object.values(bundle)) {
        if (output.type !== "chunk") continue;
        for (const id of output.moduleIds) {
          const root = packageRoot(id);
          if (root && existsSync(join(root, "package.json"))) roots.add(root);
        }
      }
      for (const root of [...roots]) {
        const manifest = JSON.parse(readFileSync(join(root, "package.json"), "utf8"));
        for (const name of Object.keys(manifest.dependencies ?? {})) {
          const dependency = dependencyRoot(root, name);
          if (dependency) roots.add(dependency);
        }
      }
      const notices = new Map<string, Notice>();
      for (const root of roots) {
        const entry = notice(root);
        notices.set(`${entry.name}@${entry.version}`, entry);
      }
      const rule = "-".repeat(70);
      const head = [
        "Third-party notices of the Machinome Studio browser surface",
        "",
        "The files beside this notice bundle the packages below, minified,",
        "each under its own licence. Every package keeps its licence and the",
        "notice it ships, stated here as the frontend's build read them from",
        "the installed package.",
        "",
      ].join("\n");
      const body = [...notices.values()]
        .sort((a, b) => a.name.localeCompare(b.name))
        .map((entry) =>
          [
            `${entry.name} ${entry.version}`,
            `Licence: ${entry.licence}`,
            `Source: ${entry.source}`,
            "",
            ...(entry.texts.length ? entry.texts : ["(the package ships no licence file)"]),
            "",
          ].join("\n"),
        )
        .join(`\n${rule}\n`);
      this.emitFile({
        type: "asset",
        fileName: "THIRD-PARTY-NOTICES.txt",
        source: `${head}\n${rule}\n${body}`,
      });
    },
  };
}

export default defineConfig({
  plugins: [react(), thirdPartyNotices()],
  build: {
    outDir: "../static",
    emptyOutDir: true,
  },
  server: {
    proxy: {
      "/api": "http://127.0.0.1:9000",
    },
  },
});
