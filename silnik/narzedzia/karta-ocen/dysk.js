// Loaded only by the local app wrapper; the inline card has no network access.
(() => {
  'use strict';
  const boot = window.sfDiskBoot;
  let version = boot.version, pending = null, busy = false, dirty = false;
  const message = text => { document.getElementById('sf-storage').textContent = text; };
  const retry = () => document.getElementById('sf-disk-retry');
  async function flush() {
    if (busy || !pending) return;
    busy = true;
    retry().hidden = true;
    while (pending) {
      const draft = pending;
      pending = null;
      message('Zapisywanie JSON w folderze przekładu…');
      try {
        const response = await fetch(boot.endpoint, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({draft,version})});
        const result = await response.json();
        if (!response.ok) throw Error(result.error || 'Odmowa zapisu');
        version = result.version;
        dirty = Boolean(pending);
        if (!dirty) message('Zapisano automatycznie JSON w folderze przekładu · '+new Date().toLocaleTimeString('pl-PL'));
      } catch (error) {
        pending ||= draft;
        message('JSON nie został potwierdzony: '+error.message+'. Szkic pozostaje w formularzu i pamięci przeglądarki.');
        retry().hidden = false;
        break;
      }
    }
    busy = false;
  }
  window.suttaflowDisk = {
    initial: boot.initial,
    save(draft) { pending = draft; dirty = true; flush(); }
  };
  window.addEventListener('DOMContentLoaded', () => {
    const button = document.createElement('button');
    button.id = 'sf-disk-retry'; button.type = 'button'; button.hidden = true;
    button.textContent = 'Ponów zapis JSON'; button.addEventListener('click', flush);
    document.getElementById('sf-storage').after(button);
  });
  window.addEventListener('beforeunload', event => {
    if (dirty) {event.preventDefault(); event.returnValue = '';}
  });
})();
