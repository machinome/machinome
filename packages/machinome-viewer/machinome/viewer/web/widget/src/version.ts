/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

declare const __VIEWER_API_VERSION__: number;
declare const __DOCUMENT_VERSIONS__: number[];

export const API_VERSION = __VIEWER_API_VERSION__;

/** The document schema versions this build reads, declared ONCE in
 * `package.json` as `machinomeDocumentVersions` and read from that same
 * file by `bundle.py`, so the answer a framework reads and the versions
 * the bundle actually refuses can never disagree. */
export const DOCUMENT_VERSIONS: readonly number[] = __DOCUMENT_VERSIONS__;
