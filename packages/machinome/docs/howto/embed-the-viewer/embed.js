async function start() {
  const inspector = await MachinomeViewer.mountInspector(
    '#model', 'spinner/manifest.json', {
      sidebar: 'collapsed',
      animation: 'external',
      autoplay: false,
      view: { camera: [80, -100, 85], target: [0, 0, 0] },
      role: 'img',
      ariaLabel: 'Red hub and three blue spinner blades',
    },
  );
  const slider = document.querySelector('#time');
  const position = document.querySelector('#position');
  slider.disabled = false;
  slider.addEventListener('input', () => {
    const time = Number(slider.value);
    inspector.viewer.setTime(time);
    position.value = time.toFixed(2);
  });
  document.querySelector('#status').textContent = 'Drag to orbit · scroll to zoom · open Assembly to inspect';
  window.addEventListener('pagehide', () => inspector.dispose(), { once: true });
}

start().catch(error => {
  document.querySelector('#status').textContent = `Could not load the model: ${error.message}`;
});
