/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// What the helper's public module (`index.tsx`) and its start (`start.tsx`)
// share, and an app does not import: the host the viewer hands an app, the
// context carrying it, the refusal a hook throws, and the error boundary
// around the app (OpenSpec `show-a-models-own-app`, design Decision 7).

import { Component, createContext } from 'react';
import type { ReactNode } from 'react';
import type { ViewerHandle } from '../src/viewer';

/** What the viewer's `start(host)` is given (design Decision 2). */
export interface AppHost {
  contract: 1;
  element: HTMLElement;
  viewport: HTMLElement;
  viewer: ViewerHandle;
  refuse(reason: string): void;
}

export const HostContext = createContext<AppHost | null>(null);

/** A refusal the helper states itself, passed to the viewer verbatim. */
export class AppRefusal extends Error {}

function messageOf(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

interface BoundaryProps {
  host: AppHost;
  children: ReactNode;
}

/** The error boundary around the app: an error thrown while it renders
 * refuses the app with its message, and the viewer shows the model with
 * the refusal in the app's place (design Decision 8). */
export class Boundary extends Component<BoundaryProps, { failed: boolean }> {
  state = { failed: false };

  static getDerivedStateFromError(): { failed: boolean } {
    return { failed: true };
  }

  componentDidCatch(error: unknown): void {
    this.props.host.refuse(error instanceof AppRefusal
      ? error.message : `it failed as it rendered: ${messageOf(error)}`);
  }

  render(): ReactNode {
    return this.state.failed ? null : this.props.children;
  }
}
