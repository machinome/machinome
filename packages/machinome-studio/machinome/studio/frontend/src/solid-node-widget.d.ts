type ViewerView = unknown;
export const SOLID_NODE_VIEWER_API_VERSION: 1;

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
  dispose(): void;
  view(): ViewerView;
};

declare global {
  interface Window {
    SolidNodeWidget: {
      apiVersion: number;
      mount(target: HTMLElement, sourceUrl: string, options: ViewerOptions): Promise<ViewerHandle>;
    };
  }
}

export { type ViewerHandle, type ViewerOptions, type ViewerView };
