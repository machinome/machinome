/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// The calculator's own app: the picture above a bar of two instruction
// buttons and the four window digits. Both buttons wait while a transition
// is drawn, and the digits read the committed bank.

import { Viewport, useMachine, usePlay } from '@machinome/viewer/app';
import { Readout } from './Readout';
import './app.css';

const WINDOWS = ['w3.digit', 'w2.digit', 'w1.digit', 'w0.digit'];

export default function CalculatorApp() {
  const { bank, drawing } = useMachine();
  const play = usePlay();
  return (
    <div className="calculator-app">
      <Viewport className="calculator-app-picture" />
      <div className="calculator-app-bar">
        <button type="button" className="calculator-app-key" data-instruction="Set four"
                disabled={drawing} onClick={() => play('Set four')}>Set four</button>
        <button type="button" className="calculator-app-key" data-instruction="Stroke"
                disabled={drawing} onClick={() => play('Stroke')}>Stroke</button>
        {WINDOWS.map((id) => <Readout key={id} id={id} value={bank[id]} />)}
      </div>
    </div>
  );
}
