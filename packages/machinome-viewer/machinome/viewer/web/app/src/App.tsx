/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

import { useEffect, useRef, useState } from 'react';
import './App.css';
import { Reloader } from './reloader';
import { ViewerShell } from './viewerShell';

const App = () => {
  const host = useRef<HTMLDivElement>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!host.current) return;
    const shell = new ViewerShell(host.current);
    shell.start().catch((reason) => setError(String(reason)));
    new Reloader(setError, () => {
      shell.reload().catch((reason) => setError(String(reason)));
    });
    return () => shell.dispose();
  }, []);

  return (
    <div className="app">
      {error ? <pre className="build-error">{error}</pre> : <div ref={host} className="model" />}
    </div>
  );
};

export default App;
