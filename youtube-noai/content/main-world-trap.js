// main-world-trap.js
// Runs in YouTube's MAIN execution world at document_start.
// Prevents YouTube's SPA router from capturing clicks on NoAI action buttons.

(() => {
  const isNoAiAction = (e) => {
    const path = e.composedPath ? e.composedPath() : [];
    for (let i = 0; i < path.length; i++) {
      const el = path[i];
      if (el && el.classList && (
        el.classList.contains('noai-pill-block-btn') ||
        el.classList.contains('noai-unhide-btn')
      )) {
        return true;
      }
    }
    return false;
  };

  ['pointerdown', 'mousedown'].forEach(evt => {
    window.addEventListener(evt, (e) => {
      if (isNoAiAction(e)) {
        e.preventDefault();
      }
    }, true);
  });
})();
