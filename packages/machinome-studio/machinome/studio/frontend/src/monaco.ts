// Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
// SPDX-License-Identifier: AGPL-3.0-only
import { loader } from "@monaco-editor/react";
import * as monaco from "../node_modules/monaco-editor/esm/vs/editor/editor.api.js";
import "../node_modules/monaco-editor/esm/vs/languages/definitions/css/register.js";
import "../node_modules/monaco-editor/esm/vs/languages/definitions/html/register.js";
import "../node_modules/monaco-editor/esm/vs/languages/definitions/ini/register.js";
import "../node_modules/monaco-editor/esm/vs/languages/definitions/javascript/register.js";
import "../node_modules/monaco-editor/esm/vs/languages/definitions/markdown/register.js";
import "../node_modules/monaco-editor/esm/vs/languages/definitions/python/register.js";
import "../node_modules/monaco-editor/esm/vs/languages/definitions/typescript/register.js";
import "../node_modules/monaco-editor/esm/vs/languages/definitions/yaml/register.js";
import editorWorker from "../node_modules/monaco-editor/esm/vs/editor/editor.worker.js?worker";

type MonacoWorkerEnvironment = {
  MonacoEnvironment: {
    getWorker: (_moduleId: string, label: string) => Worker;
  };
};

(self as unknown as MonacoWorkerEnvironment).MonacoEnvironment = {
  getWorker() {
    return new editorWorker();
  },
};

loader.config({ monaco });
