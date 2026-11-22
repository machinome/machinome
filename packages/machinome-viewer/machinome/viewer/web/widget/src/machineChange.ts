/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// The clocked machine's change notification (OpenSpec
// `show-a-models-own-app`, design Decision 6): subscribe, notify, dispose,
// on the shape of `AssemblyChangeNotifier` (`assembly.ts`, ADR-049). The
// notification carries no value: it means that what a page last read of
// the machine -- its committed bank, whether a transition is drawn -- may
// be stale, and the page reads again from the handle. `viewer.ts` decides
// WHEN to notify; this class decides nothing.

export type MachineChangeListener = () => void;

/** A listener cancelled or added while a notification is being delivered
 * is not called for that notification, and a listener that throws does
 * not stop the others or escape `notify`. */
export class MachineChangeNotifier {
  private listeners = new Set<MachineChangeListener>();

  subscribe(listener: MachineChangeListener): () => void {
    this.listeners.add(listener);
    return () => { this.listeners.delete(listener); };
  }

  notify(): void {
    for (const listener of [...this.listeners]) {
      if (!this.listeners.has(listener)) {
        // Cancelled by an earlier listener in this same dispatch.
        continue;
      }
      try {
        listener();
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('machine change listener threw', error);
      }
    }
  }

  dispose(): void {
    this.listeners.clear();
  }
}
