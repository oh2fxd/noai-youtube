import { spawn } from 'child_process';

const PORT = 9251;
const PDIR = '/tmp/brave_test_tag_mode_' + Date.now();
const EXTENSION_DIR = '/home/oh2fxd/toolbox/python/noai/youtube-noai';

console.log('Testing permanent tag visibility in Tag mode...');
const brave = spawn('/usr/bin/brave-browser', [
  '--headless=new',
  `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${PDIR}`,
  `--load-extension=${EXTENSION_DIR}`,
  '--no-first-run',
  '--no-default-browser-check',
  '--disable-gpu',
  'https://www.youtube.com/results?search_query=midjourney+sora+ai+music'
], { stdio: 'ignore' });

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

setTimeout(async () => {
  try {
    const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
    const page = list.find(t => t.type === 'page');
    const ws = new WebSocket(page.webSocketDebuggerUrl);
    await new Promise(r => ws.addEventListener('open', r));
    ws.send(JSON.stringify({ id: 1, method: 'Runtime.enable' }));

    // Set action to 'tag'
    await sleep(2000);
    const swTarget = list.find(t => t.type === 'service_worker');
    if (swTarget) {
      const swWs = new WebSocket(swTarget.webSocketDebuggerUrl);
      await new Promise(r => swWs.addEventListener('open', r));
      swWs.send(JSON.stringify({
        id: 99,
        method: 'Runtime.evaluate',
        params: {
          expression: `chrome.storage.sync.set({ action: 'tag' })`
        }
      }));
      await sleep(1000);
      swWs.close();
    }

    await sleep(4000);

    ws.addEventListener('message', e => {
      const d = JSON.parse(e.data);
      if (d.id === 20) {
        const res = d.result?.result?.value;
        console.log('\n--- VERIFICATION RESULT ---');
        console.log(`Total Cards: ${res.total}`);
        console.log(`Cards with permanent thumbnail badge: ${res.badgeCount}`);
        console.log(`Cards with permanent inline title pill: ${res.pillCount}`);
        console.log('Sample card details:');
        res.samples.forEach((s, idx) => {
          console.log(`  ${idx + 1}. [Badge: ${s.hasBadge ? 'YES' : 'NO'}] [Pill: ${s.hasPill ? 'YES' : 'NO'}] "${s.title.slice(0, 60)}..."`);
        });
        brave.kill('SIGKILL');
        process.exit(0);
      }
    });

    ws.send(JSON.stringify({
      id: 20,
      method: 'Runtime.evaluate',
      params: {
        expression: `(() => {
          const cards = Array.from(document.querySelectorAll('ytd-video-renderer'));
          return {
            total: cards.length,
            badgeCount: document.querySelectorAll('.noai-badge').length,
            pillCount: document.querySelectorAll('.noai-inline-pill').length,
            samples: cards.slice(0, 5).map(c => ({
              title: (c.querySelector('#video-title') || {}).textContent?.trim() || '',
              hasBadge: !!c.querySelector('.noai-badge'),
              hasPill: !!c.querySelector('.noai-inline-pill'),
              badgeStyle: c.querySelector('.noai-badge') ? window.getComputedStyle(c.querySelector('.noai-badge')).display : null
            }))
          };
        })()`,
        returnByValue: true
      }
    }));
  } catch (err) {
    console.error(err);
    brave.kill('SIGKILL');
    process.exit(1);
  }
}, 2000);
