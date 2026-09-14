/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// Ported from `app/src/reloader.ts` (design D12), behaviour held
// IDENTICAL: the socket URL, the 2s retry, the two-attempt grace before
// the first banner, the immediate banner on a drop from a live
// connection, the banner's id, class and text, and the `/_build_error`
// poll with its `tstamp` dedupe. The only change is the type of what a
// build error is reported through: React's `Dispatch<SetStateAction>`
// becomes a plain callback, because there is no React here to dispatch
// into. The banner's own rule moves from `App.css` into an injected
// stylesheet -- the third component in this bundle to follow the
// pattern ADR-050 set for the navigator.

export interface BuildError {
  error: string;
  tstamp: number;
}

// How long to wait between reconnect attempts once a connection attempt
// has failed (skill-repo improvements.md #12: retry indefinitely, ~2s).
const RETRY_INTERVAL_MS = 2000;

// How many consecutive failed *initial* connection attempts to tolerate
// before showing the offline banner. Avoids a red flash on ordinary page
// load, where the very first attempt just hasn't resolved yet -- only
// treated as "the backend looks dead" after a couple of retry cycles.
const INITIAL_CONNECT_GRACE_ATTEMPTS = 2;

const BANNER_ID = 'solid-node-offline-banner';
const BANNER_TEXT = 'solid develop is not running — model may be stale';

const STYLE_ID = 'solid-node-reloader-style';

// Carried over verbatim in effect from `App.css`: a fixed red strip
// across the top, `pointer-events: none` so the stale model underneath
// stays fully interactive.
const RELOADER_STYLESHEET = `
.reload-offline-banner {
  --solid-reload-bg: #c0392b;
  --solid-reload-fg: #fff;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 9999;
  background: var(--solid-reload-bg);
  color: var(--solid-reload-fg);
  text-align: center;
  font-weight: bold;
  font-family: sans-serif;
  padding: 8px 12px;
  pointer-events: none;
}
`;

function injectStylesheet(): void {
  if (typeof document === 'undefined' || document.getElementById(STYLE_ID)) {
    return;
  }
  const style = document.createElement('style');
  style.id = STYLE_ID;
  style.textContent = RELOADER_STYLESHEET;
  document.head.append(style);
}

export class Reloader {

  reloadTrigger: WebSocket | undefined;
  time: number;
  reload: () => void;

  setError: (message: string) => void;
  errorTstamp: number | null = null;

  firstCheck: boolean;

  // True once any connection attempt has ever succeeded.
  everConnected: boolean = false;

  // Consecutive failed attempts since the last successful open (only
  // meaningful before everConnected is true; see INITIAL_CONNECT_GRACE_ATTEMPTS).
  failedAttempts: number = 0;

  // Mirrors whether the offline banner is currently in the DOM, so a
  // reconnect can tell "we were down" apart from "everything was fine".
  bannerVisible: boolean = false;

  constructor(
    setError: (message: string) => void,
    reload: () => void,
  ) {
    this.setError = setError;
    this.reload = reload;

    this.time = 0;

    this.firstCheck = true;

    injectStylesheet();
    this.watch();
  }

  watch() {
    const parts = window.location.href.split('/');
    const protocol = parts[0].replace('http', 'ws');
    const domain = parts[2];

    if (this.reloadTrigger) return;

    this.reloadTrigger = new WebSocket(`${protocol}//${domain}/ws/reload`);

    this.reloadTrigger.onopen = () => {
      const isReconnect = this.bannerVisible;
      this.everConnected = true;
      this.failedAttempts = 0;

      if (isReconnect) {
        // Heal the browser with zero manual interaction: a restarted
        // `solid develop` must repopulate the tree/STLs, not just clear
        // the banner, since the model may have changed while it was down.
        this.checkBuild().finally(() => this.hideBanner());
      } else {
        this.hideBanner();
      }
    };

    this.reloadTrigger.onmessage = (event) => {
      if (event.data === "reload") {
        this.checkBuild();
      }
    };

    this.reloadTrigger.onclose = () => {
      this.reloadTrigger = undefined;

      if (this.everConnected) {
        // A connection that was genuinely up just dropped -- this is
        // exactly the case a stale-model false bug report comes from.
        // Show the banner immediately, no grace period.
        this.showBanner();
      } else {
        this.failedAttempts += 1;
        if (this.failedAttempts >= INITIAL_CONNECT_GRACE_ATTEMPTS) {
          this.showBanner();
        }
      }

      setTimeout(() => this.watch(), RETRY_INTERVAL_MS);
    };

  }

  showBanner() {
    this.bannerVisible = true;
    if (typeof document === 'undefined') return;
    if (document.getElementById(BANNER_ID)) return;

    const banner = document.createElement('div');
    banner.id = BANNER_ID;
    banner.className = 'reload-offline-banner';
    banner.textContent = BANNER_TEXT;
    document.body.appendChild(banner);
  }

  hideBanner() {
    this.bannerVisible = false;
    if (typeof document === 'undefined') return;

    const banner = document.getElementById(BANNER_ID);
    if (banner) {
      banner.remove();
    }
  }

  async checkBuild() {
    const response = await fetch('/_build_error');
    const result = await response.json() as BuildError;
    if (!result.error || result.tstamp == this.errorTstamp) {
      this.setError('');
      this.reload();
    } else {
      this.errorTstamp = result.tstamp;
      this.setError(result.error);
    }
  }

}
