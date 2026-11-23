/*
 * Machinome - A framework for mechanical CAD projects
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// The layered machine's own app: the picture above a bar with one button
// per layer the document declares and a "Whole machine" button. A button
// shows its layer through the mount's handle; nothing is drawn by the app.

import { Viewport, useMachine, useViewer } from '@machinome/viewer/app';
import './app.css';

export default function LayersApp() {
  const { layers } = useMachine();
  const viewer = useViewer();
  return (
    <div className="layers-app">
      <Viewport className="layers-app-picture" />
      <div className="layers-app-bar">
        <button type="button" className="layers-app-button" data-layer=""
                onClick={() => viewer.show(null)}>Whole machine</button>
        {layers.map((layer) => (
          <button type="button" className="layers-app-button" key={layer.key}
                  data-layer={layer.key}
                  onClick={() => viewer.show(layer)}>{layer.label}</button>
        ))}
      </div>
    </div>
  );
}
