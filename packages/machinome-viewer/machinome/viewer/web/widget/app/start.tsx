/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// What an app bundle's generated entry calls (OpenSpec
// `show-a-models-own-app`, design Decisions 2, 7 and 11): the app's
// component rendered into the element the viewer gave it, synchronously,
// inside the host's context and an error boundary; the disposer the viewer
// keeps; and the check that the app placed the picture.

import { flushSync } from 'react-dom';
import { createRoot } from 'react-dom/client';
import type { ComponentType } from 'react';
import { Boundary, HostContext } from './host';
import type { AppHost } from './host';

export function start(App: ComponentType, host: AppHost): () => void {
  // The first refusal is the one the reader is told; a render error that
  // also leaves no picture is one failure, not two.
  let refused = false;
  const guarded: AppHost = {
    ...host,
    refuse(reason: string): void {
      if (refused) return;
      refused = true;
      host.refuse(reason);
    },
  };
  const root = createRoot(host.element);
  flushSync(() => {
    root.render(
      <HostContext value={guarded}>
        <Boundary host={guarded}>
          <App />
        </Boundary>
      </HostContext>,
    );
  });
  if (!host.element.contains(host.viewport)) {
    guarded.refuse('it places no <Viewport/>, so the model would not be seen');
  }
  return () => { root.unmount(); };
}
