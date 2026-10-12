// The movie's palette and type, with the stage's defaults for what the
// document leaves out (docs/movie-document.md, "Top level"). Layout is never
// here: it is the set's. The defaults are the film page's former palette.
export const DEFAULT_STYLE=Object.freeze({background:'#faf7ef',foreground:'#222222',accent:'#237c86',
  fontFamily:'DejaVu Sans, sans-serif',safeInsetFraction:.08});
export const COLOR=/^#[0-9a-fA-F]{6}$/;
export const effectiveStyle=(style={})=>({...DEFAULT_STYLE,...style});
