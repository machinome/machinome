/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

/** One window of the register: its label and the digit it shows. */
export function Readout({ id, value }: { id: string; value: number | undefined }) {
  return (
    <span className="calculator-app-readout" data-readout={id}>
      <span className="calculator-app-label">Window</span>
      <span className="calculator-app-digit">{value}</span>
    </span>
  );
}
