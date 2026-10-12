// Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
// SPDX-License-Identifier: AGPL-3.0-or-later
type ViewerView = unknown;
export const MACHINOME_VIEWER_API_VERSION: 4;

type AssemblyPath = readonly string[];

type AssemblyNode = {
  name: string;
  path: string[];
  color: string | null;
  model: boolean;
  children: AssemblyNode[];
};

type ViewerOptions = {
  baseUrl: string;
  animation: "inline" | "toggle" | "none" | "external";
  view?: ViewerView;
  className?: string;
  role?: string;
  ariaLabel?: string;
};

type ViewerHandle = {
  apiVersion: number;
  artifactChanged(path: string): Promise<void>;
  manifestChanged(): Promise<void>;
  assembly(): AssemblyNode;
  setRoot(path: AssemblyPath | null): void;
  setVisible(path: AssemblyPath, visible: boolean): void;
  reload(): Promise<void>;
  dispose(): void;
  view(): ViewerView;
};

declare global {
  interface Window {
    MachinomeViewer: {
      apiVersion: number;
      mount(target: HTMLElement, sourceUrl: string, options: ViewerOptions): Promise<ViewerHandle>;
    };
  }
}

export { type AssemblyNode, type AssemblyPath, type ViewerHandle, type ViewerOptions, type ViewerView };
