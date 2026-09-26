// Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
// SPDX-License-Identifier: AGPL-3.0-or-later
// Vendored from machinome-viewer 0.2.0, viewer API 11 (viewer worktree
// commit 644b504ca3431b8450ed98408d5e151cf7437ef5, branch
// viewer-navigator), declaring API 10 -- the version this studio requires
// (design D3, `adopt-the-viewer-navigator`). Only the `ViewerHandle` surface
// the studio actually uses is copied here, plus the navigator's own types;
// the driving and playback surfaces are deliberately left out. Of the run
// surface only `run.dt` is declared -- the studio sets the step a running
// model is integrated at and reads nothing back. It has been a mount option
// since viewer API 8 (`run-in-the-worker`), below the API 10 this studio
// requires, so declaring it raises nothing.
type ViewerView = unknown;
export const MACHINOME_VIEWER_API_VERSION: 20;

type AssemblyPath = readonly string[];

type AssemblyNode = {
  name: string;
  path: string[];
  color: string | null;
  model: boolean;
  children: AssemblyNode[];
};

/** The navigation state a host reads: the focused root, or `null` for the
 * published document root, and the explicitly hidden paths, each
 * root-relative. Both fields are copies: a caller holds a value, not a
 * window into the viewer. */
type AssemblyNavigationState = {
  root: string[] | null;
  hidden: string[][];
};

/** What a subscribed listener receives: the fresh assembly and navigation
 * snapshots, equal to what `assembly()` and `navigation()` return at that
 * moment. */
type AssemblyChange = {
  assembly: AssemblyNode;
  navigation: AssemblyNavigationState;
};

type AssemblyListener = (change: AssemblyChange) => void;

type ViewerOptions = {
  baseUrl: string;
  animation: "inline" | "toggle" | "none" | "external";
  view?: ViewerView;
  className?: string;
  role?: string;
  ariaLabel?: string;
  run?: {
    /** Simulated seconds per tick, fixed for the life of a mount. A
     * document publishes none; the viewer defaults to 1/240 s. */
    dt?: number;
  };
};

type ViewerHandle = {
  apiVersion: number;
  artifactChanged(path: string): Promise<void>;
  manifestChanged(): Promise<void>;
  assembly(): AssemblyNode;
  setRoot(path: AssemblyPath | null): void;
  setVisible(path: AssemblyPath, visible: boolean): void;
  /** The navigation state: the focused root and the explicitly hidden
   * paths, as a serializable snapshot the handle does not later modify. */
  navigation(): AssemblyNavigationState;
  /** Subscribe to every accepted operation that publishes a tree or moves
   * the focused root or the visibility state, and returns a function that
   * cancels the subscription. */
  onAssemblyChange(listener: AssemblyListener): () => void;
  reload(): Promise<void>;
  dispose(): void;
  view(): ViewerView;
};

type NavigatorOptions = {
  /** Accessible name of the tree; default 'Assembly'. */
  label?: string;
  /** Present the "show full assembly" affordance; default true. */
  fullAssembly?: boolean;
  /** Extra class on the navigator root, for a host's own scoping. */
  className?: string;
  /** Inject the stylesheet into the target's document; default 'inject'. */
  styles?: "inject" | "none";
};

type NavigatorHandle = {
  dispose(): void;
};

declare global {
  interface Window {
    MachinomeViewer: {
      apiVersion: number;
      mount(target: HTMLElement, sourceUrl: string, options: ViewerOptions): Promise<ViewerHandle>;
      mountNavigator(target: HTMLElement | string, viewer: ViewerHandle, options?: NavigatorOptions): NavigatorHandle;
    };
  }
}

export {
  type AssemblyChange,
  type AssemblyListener,
  type AssemblyNavigationState,
  type AssemblyNode,
  type AssemblyPath,
  type NavigatorHandle,
  type NavigatorOptions,
  type ViewerHandle,
  type ViewerOptions,
  type ViewerView,
};
