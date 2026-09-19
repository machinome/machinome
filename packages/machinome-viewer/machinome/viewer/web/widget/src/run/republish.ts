/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// What a live rebuild does to a live run (OpenSpec
// `drive-the-run-on-screen`, design §3).
//
// `machinome develop` republishes while a run is standing part way through a
// movement. The workflow design's rule is the one this answers: "Live
// updates must invalidate or explicitly migrate incompatible simulation
// state, not preserve coordinates solely because strings happen to
// match." `identity` is the digest the framework publishes for exactly
// that question -- the root class, the bank's ids, the inputs'
// declarations, the spans and every edge's ends, direction and
// expression -- so an edit that moves a law changes it and an edit that
// moves a mesh does not.
//
// Pure on purpose: `viewer.ts` renders the answer and keeps or disposes
// the runtime by it, and the decision itself is tested in plain node.

/** A run, as far as a republish is concerned. */
export interface RunIdentity {
  identity: string;
  /** Simulated seconds per tick. A run state carries its step size and a
   * restore across two of them is refused by the framework's own rule,
   * so a changed step is a different run. */
  dt: number;
}

export type RepublishOutcome =
  'kept' | 'restarted' | 'started' | 'ended' | 'none';

export interface RepublishPlan {
  /** Whether the live run stands: the same bank, the same active
   * commands, the same step count and the same elapsed clock. */
  keep: boolean;
  outcome: RepublishOutcome;
  /** What to say on the panel, or null when there was no run either
   * side of the rebuild and nothing happened worth saying. */
  message: string | null;
}

export function republishPlan(current: RunIdentity | null,
                              next: RunIdentity | null): RepublishPlan {
  if (current === null && next === null) {
    return { keep: false, outcome: 'none', message: null };
  }
  if (current === null) {
    return {
      keep: false,
      outcome: 'started',
      message: 'the rebuild brought a machine: a run started at its rest '
        + 'state.',
    };
  }
  if (next === null) {
    return {
      keep: false,
      outcome: 'ended',
      message: 'the rebuild carries no machine: the run ended.',
    };
  }
  if (current.identity !== next.identity) {
    return {
      keep: false,
      outcome: 'restarted',
      message: 'the rebuild published a different mechanism: the machine '
        + 'was reset to its new rest state rather than carrying '
        + 'coordinates across two different mechanisms.',
    };
  }
  if (current.dt !== next.dt) {
    return {
      keep: false,
      outcome: 'restarted',
      message: 'the run\'s step size changed: the machine was reset rather '
        + 'than continued at a step it did not integrate.',
    };
  }
  return {
    keep: true,
    outcome: 'kept',
    message: 'the same machine was republished: the run kept where it was.',
  };
}
