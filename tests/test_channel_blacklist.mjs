import { spawn } from 'child_process';
import { rmSync, mkdirSync } from 'fs';

const EXTENSION_DIR = '/home/oh2fxd/toolbox/python/noai';
const PORT = 9248;
const PDIR = '/tmp/brave_channel_test_' + Date.now();

try { rmSync(PDIR, { recursive: true, force: true }); } catch (e) {}
mkdirSync(PDIR, { recursive: true });

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function waitForCdp(port, maxWaitMs = 10000) {
  const start = Date.now();
  while (Date.now() - start < maxWaitMs) {
    try {
      const res = await fetch(`http://127.0.0.1:${port}/json/version`);
      if (res.ok) return true;
    } catch (e) {}
    await sleep(200);
  }
  throw new Error('CDP port did not open in time.');
}

async function sendCdp(ws, method, params = {}) {
  const id = Math.floor(Math.random() * 1000000);
  return new Promise((resolve, reject) => {
    const handler = (evt) => {
      const msg = JSON.parse(evt.data);
      if (msg.id === id) {
        ws.removeEventListener('message', handler);
        if (msg.error) reject(msg.error);
        else resolve(msg.result);
      }
    };
    ws.addEventListener('message', handler);
    ws.send(JSON.stringify({ id, method, params }));
  });
}

async function run() {
  console.log('Testing channel blacklist on "dark techno" search results...');
  const proc = spawn('/usr/bin/brave-browser', [
    '--headless=new',
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${PDIR}`,
    `--load-extension=${EXTENSION_DIR}`,
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-gpu',
    'https://www.youtube.com/results?search_query=dark+techno'
  ], { stdio: 'ignore' });

  try {
    await waitForCdp(PORT);
    const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
    const pageTarget = list.find(t => t.type === 'page' && t.url.includes('youtube'));
    const ws = new WebSocket(pageTarget.webSocketDebuggerUrl);
    await new Promise((res) => ws.addEventListener('open', res));
    await sendCdp(ws, 'Page.enable');
    await sendCdp(ws, 'Runtime.enable');

    await sleep(3000);

    for (let i = 0; i < 7; i++) {
      await sendCdp(ws, 'Runtime.evaluate', { expression: 'window.scrollBy(0, 4000)' });
      await sleep(1500);
    }

    // Set custom channels into storage to simulate user blocking them
    await sendCdp(ws, 'Runtime.evaluate', {
      expression: `
        new Promise(resolve => {
          chrome.storage.sync.set({
            customChannels: ['Obsidian Hyper Techno', 'Hypnotic Night Sessions', 'Nocturne Echoes']
          }, resolve);
        })
      `,
      awaitPromise: true
    });

    await sleep(2000);

    const evalRes = await sendCdp(ws, 'Runtime.evaluate', {
      expression: `
        (() => {
          const cards = Array.from(document.querySelectorAll('ytd-video-renderer'));
          const hidden = cards.filter(c => c.classList.contains('noai-hidden')).map(c => ({
            title: (c.querySelector('#video-title') || {}).textContent?.trim().replace(/\\s+/g, ' ') || '',
            channel: (c.querySelector('#channel-name') || {}).textContent?.trim().replace(/\\s+/g, ' ') || ''
          }));
          return {
            total: cards.length,
            hiddenCount: hidden.length,
            hiddenItems: hidden
          };
        })()
      `,
      returnByValue: true
    });

    console.log('Channel Blacklist Evaluation Result:', JSON.stringify(evalRes.result?.value, null, 2));
    ws.close();
  } finally {
    proc.kill('SIGKILL');
  }
}

run();
