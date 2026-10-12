document.addEventListener('DOMContentLoaded', () => {
  for (const button of document.querySelectorAll('[data-viewer-demo]')) {
    button.addEventListener('click', () => {
      const frame = document.createElement('iframe');
      frame.src = button.dataset.viewerDemo;
      frame.title = 'Interactive Machinome spinner: camera, timeline and assembly controls';
      button.closest('.viewer-demo').replaceChildren(frame);
    }, { once: true });
  }
});
