/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// Bundle a model's own app with the viewer's toolchain (OpenSpec
// `show-a-models-own-app`, design Decision 11). `machinome/viewer/web/app.py`
// runs this with Node, writing one request as JSON on standard input,
//
//   { "entry": <the app's entry file>, "root": <the project's root>,
//     "output": <the directory the files are published into> }
//
// and reads one answer as JSON on standard output:
//
//   { "script": "app-<h>.js", "stylesheet": "app-<h>.css" | null,
//     "inputs": [<absolute paths of the project files the bundle read>] }
//   or { "refusal": "<sentence>" }, having written nothing.
//
// The app's own .tsx/.ts/.jsx/.js and .css are bundled with the viewer's own
// esbuild, its own React and React DOM and the helper
// `@machinome/viewer/app` into one minified classic script (an IIFE) and at
// most one stylesheet, each named by the first 16 hex digits of the SHA-256
// of its bytes. The script dispatches `machinome:app` on its own element as
// it runs (design Decision 2). One React: `react`, `react/jsx-runtime`,
// `react-dom`, `react-dom/client` and the helper resolve to the files the
// WIDGET resolves them to, wherever npm placed them, so the app, the helper
// and React DOM share one copy. Anything else an app imports by a bare name
// is refused naming it, and so is any file read outside the project's root.
// Nothing is installed.

import { build } from 'esbuild';
import { createHash } from 'node:crypto';
import {
  mkdtemp, readFile, realpath, rename, rm, writeFile,
} from 'node:fs/promises';
import { createRequire } from 'node:module';
import { tmpdir } from 'node:os';
import {
  dirname, isAbsolute, join, relative, resolve, sep,
} from 'node:path';
import { fileURLToPath } from 'node:url';

const WIDGET = dirname(fileURLToPath(import.meta.url));
const APP = join(WIDGET, 'app');
const widgetRequire = createRequire(join(WIDGET, 'package.json'));

/** What an app may import by a bare name, and the file each one is. */
const PROVIDED = {
  'react': widgetRequire.resolve('react'),
  'react/jsx-runtime': widgetRequire.resolve('react/jsx-runtime'),
  'react-dom': widgetRequire.resolve('react-dom'),
  'react-dom/client': widgetRequire.resolve('react-dom/client'),
  '@machinome/viewer/app': join(APP, 'index.tsx'),
};

const ALLOWED = 'an app imports its own files, react, react-dom and '
  + '@machinome/viewer/app';

const REACT_DIR = dirname(widgetRequire.resolve('react/package.json'));
const REACT_DOM_DIR = dirname(widgetRequire.resolve('react-dom/package.json'));
const SCHEDULER_DIR = dirname(createRequire(join(REACT_DOM_DIR, 'package.json'))
  .resolve('scheduler/package.json'));

class Refusal extends Error {}

const inside = (base, path) => {
  const rel = relative(base, path);
  return rel === '' || (!isAbsolute(rel) && rel !== '..'
                        && !rel.startsWith(`..${sep}`));
};

const posix = (path) => path.split(sep).join('/');

async function versionOf(directory) {
  return JSON.parse(await readFile(join(directory, 'package.json'), 'utf8')).version;
}

async function banner() {
  const viewer = await versionOf(WIDGET);
  const react = await versionOf(REACT_DIR);
  const reactDom = await versionOf(REACT_DOM_DIR);
  const reacts = react === reactDom
    ? `React and React DOM ${react}` : `React ${react} and React DOM ${reactDom}`;
  // The grant is written out, as `build.mjs` writes it: the licence test
  // reads every header of the package, this one included.
  return `/*!
 * machinome-viewer app bundle, built by machinome-viewer ${viewer}
 * Bundles ${reacts} - Copyright (c) Meta Platforms, Inc. and affiliates
 *   MIT License - https://github.com/facebook/react/blob/main/LICENSE
 * Bundles @machinome/viewer/app - Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 *   SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 *   Source: https://github.com/machinome/machinome
 */
`;
}

const nameOf = (bytes, extension) =>
  `app-${createHash('sha256').update(bytes).digest('hex').slice(0, 16)}.${extension}`;

/** Write `bytes` as `output/name` through a temporary name and a rename,
 * unless the file already holds them: an unchanged app publishes nothing. */
async function publish(output, name, bytes) {
  const target = join(output, name);
  try {
    const present = await readFile(target);
    if (present.equals(bytes)) return;
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
  }
  const staged = join(output, `.${name}.${process.pid}.tmp`);
  await writeFile(staged, bytes);
  await rename(staged, target);
}

async function bundle(request) {
  let root;
  try {
    root = await realpath(request.root);
  } catch {
    throw new Refusal(`the project's root ${request.root} does not exist`);
  }
  let entry;
  try {
    entry = await realpath(request.entry);
  } catch {
    throw new Refusal(`the app's entry ${request.entry} does not exist`);
  }
  if (!inside(root, entry)) {
    throw new Refusal(`the app's entry ${entry} is outside the project at `
                      + `${root}; an app's files are the project's own`);
  }
  const named = posix(relative(root, entry));
  const own = [APP, REACT_DIR, REACT_DOM_DIR, SCHEDULER_DIR];
  const isOwn = (path) => own.some((directory) => inside(directory, path));
  const work = await mkdtemp(join(tmpdir(), 'machinome-app-'));
  try {
    // The generated entry: the app's default export started by the helper,
    // announced on the script's own element (design Decision 2).
    await writeFile(join(work, 'entry.tsx'),
      `import App from ${JSON.stringify(entry)};\n`
      + `import { start } from ${JSON.stringify(join(APP, 'start.tsx'))};\n`
      + 'document.currentScript.dispatchEvent(new CustomEvent(\'machinome:app\', '
      + '{ detail: { contract: 1, start: (host) => start(App, host) } }));\n');
    // A tsconfig of its own, so no tsconfig of the project's or of the
    // widget's changes how the app is compiled.
    await writeFile(join(work, 'tsconfig.json'), '{"compilerOptions":{}}\n');
    const imports = {
      name: 'machinome-app-imports',
      setup(builder) {
        builder.onResolve({ filter: /.*/ }, (args) => {
          if (args.kind === 'entry-point') return undefined;
          const specifier = args.path;
          if (Object.hasOwn(PROVIDED, specifier)) {
            return { path: PROVIDED[specifier] };
          }
          if (specifier.startsWith('.') || isAbsolute(specifier)) return undefined;
          // React's own packages resolve their own dependencies.
          if (isOwn(args.importer)) return undefined;
          const from = inside(root, args.importer)
            ? posix(relative(root, args.importer)) : args.importer;
          return {
            errors: [{ text: `${from}: imports '${specifier}'; ${ALLOWED}` }],
          };
        });
      },
    };
    let result;
    try {
      result = await build({
        entryPoints: [join(work, 'entry.tsx')],
        outfile: join(work, 'out', 'app.js'),
        absWorkingDir: work,
        tsconfig: join(work, 'tsconfig.json'),
        bundle: true,
        format: 'iife',
        platform: 'browser',
        target: 'es2020',
        minify: true,
        jsx: 'automatic',
        define: { 'process.env.NODE_ENV': '"production"' },
        sourcemap: false,
        metafile: true,
        write: false,
        logLevel: 'silent',
        loader: {
          '.ts': 'ts', '.tsx': 'tsx', '.js': 'js', '.jsx': 'jsx', '.css': 'css',
        },
        plugins: [imports],
      });
    } catch (failure) {
      const errors = failure.errors ?? [];
      const refused = errors.find((one) => one.pluginName === imports.name);
      if (refused !== undefined) throw new Refusal(refused.text);
      if (errors.length === 0) throw failure;
      const lines = errors.map((one) => {
        const at = one.location;
        if (!at) return one.text;
        const file = resolve(work, at.file);
        const shown = inside(root, file) ? posix(relative(root, file)) : file;
        return `${shown}:${at.line}:${at.column}: ${one.text}`;
      });
      throw new Refusal(`the app ${named} does not build:\n${lines.join('\n')}`);
    }
    // Every file the bundle read: the widget's own (the helper, React) or
    // the project's; anything else is outside the project and refused.
    const inputs = [];
    for (const key of Object.keys(result.metafile.inputs)) {
      const path = resolve(work, key);
      if (inside(work, path) || isOwn(path)) continue;
      const real = await realpath(path).catch(() => path);
      if (isOwn(real)) continue;
      if (!inside(root, real)) {
        throw new Refusal(`the app ${named} reads ${real}, which is outside `
                          + `the project at ${root}; an app's files are the `
                          + "project's own");
      }
      inputs.push(real);
    }
    inputs.sort();
    const script = result.outputFiles.find((file) => file.path.endsWith('.js'));
    const sheet = result.outputFiles.find((file) => file.path.endsWith('.css'));
    const scriptBytes = Buffer.concat([
      Buffer.from(await banner(), 'utf8'), Buffer.from(script.contents)]);
    const scriptName = nameOf(scriptBytes, 'js');
    let sheetName = null;
    let sheetBytes = null;
    if (sheet !== undefined && sheet.contents.length > 0) {
      sheetBytes = Buffer.from(sheet.contents);
      sheetName = nameOf(sheetBytes, 'css');
    }
    // Nothing is written before everything was judged.
    if (sheetName !== null) await publish(request.output, sheetName, sheetBytes);
    await publish(request.output, scriptName, scriptBytes);
    return { script: scriptName, stylesheet: sheetName, inputs };
  } finally {
    await rm(work, { recursive: true, force: true });
  }
}

async function readRequest() {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  return JSON.parse(Buffer.concat(chunks).toString('utf8'));
}

let answer;
try {
  answer = await bundle(await readRequest());
} catch (error) {
  answer = error instanceof Refusal
    ? { refusal: error.message }
    : { refusal: `the app could not be bundled: ${error?.stack ?? error}` };
}
process.stdout.write(JSON.stringify(answer));
