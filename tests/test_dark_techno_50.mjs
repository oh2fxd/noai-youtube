import { spawn } from 'child_process';
import { rmSync, mkdirSync } from 'fs';

const EXTENSION_DIR = '/home/oh2fxd/toolbox/python/noai';
const PORT = 9235;
const PDIR = '/tmp/brave_test_dark_techno_' + Date.now();

try {
  rmSync(PDIR, { recursive: true, force: true });
} catch (e) {}
mkdirSync(PDIR, { recursive: true });

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

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
  console.log('Launching Brave with NoAI extension for "dark techno" search test...');
  const proc = spawn('/usr/bin/brave-browser', [
    '--headless=new',
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${PDIR}`,
    `--load-extension=${EXTENSION_DIR}`,
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-gpu',
    '--window-size=1280,1000',
    'https://www.youtube.com/results?search_query=dark+techno'
  ], { stdio: 'ignore' });

  try {
    await waitForCdp(PORT);
    const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
    const pageTarget = list.find(t => t.type === 'page' && t.url.includes('youtube'));
    if (!pageTarget) throw new Error('YouTube page target not found');

    const ws = new WebSocket(pageTarget.webSocketDebuggerUrl);
    await new Promise((res) => ws.addEventListener('open', res));
    await sendCdp(ws, 'Page.enable');
    await sendCdp(ws, 'Runtime.enable');

    console.log('Waiting for initial page load...');
    await sleep(4000);

    // Scroll down multiple times to load at least 50 video cards
    console.log('Scrolling down to load at least 50 video cards...');
    for (let scroll = 1; scroll <= 10; scroll++) {
      const cardCountRes = await sendCdp(ws, 'Runtime.evaluate', {
        expression: `document.querySelectorAll('ytd-video-renderer').length`,
        returnByValue: true
      });
      const count = cardCountRes.result?.value || 0;
      console.log(`  Scroll #${scroll}: currently ${count} cards loaded.`);
      if (count >= 55) break;

      await sendCdp(ws, 'Runtime.evaluate', {
        expression: `window.scrollBy(0, 3500);`
      });
      await sleep(2500);
    }

    // Allow extension DOM observer and debounced scan to complete
    console.log('Waiting 3s for extension DOM observer to process all cards...');
    await sleep(3000);

    const evalRes = await sendCdp(ws, 'Runtime.evaluate', {
      expression: `
        (() => {
          const cards = Array.from(document.querySelectorAll('ytd-video-renderer'));
          const results = cards.map(c => {
            const titleEl = c.querySelector('#video-title, #video-title-link, h3');
            const channelEl = c.querySelector('#channel-name, .ytd-channel-name');
            const descEl = c.querySelector('#description-text, .metadata-snippet-container');
            const isHidden = c.classList.contains('noai-hidden');
            const isBlur = c.classList.contains('noai-blur');
            const badge = c.querySelector('.noai-badge');
            
            // Check badges
            const badges = Array.from(c.querySelectorAll('ytd-badge-supported-renderer, .badge')).map(b => b.textContent.trim());

            return {
              title: titleEl ? titleEl.textContent.trim().replace(/\\s+/g, ' ') : '(no title)',
              channel: channelEl ? channelEl.textContent.trim().replace(/\\s+/g, ' ') : '(unknown channel)',
              desc: descEl ? descEl.textContent.trim().replace(/\\s+/g, ' ') : '',
              isHidden,
              isBlur,
              badgeText: badge ? badge.textContent : null,
              ytBadges: badges
            };
          }).filter(r => r.title !== '(no title)');

          return {
            totalCards: results.length,
            first50: results.slice(0, 50)
          };
        })()
      `,
      returnByValue: true
    });

    const data = evalRes.result?.value;
    if (!data) {
      console.error('Could not evaluate page cards:', evalRes);
      return;
    }

    const items = data.first50;
    const hiddenItems = items.filter(i => i.isHidden);
    const allowedItems = items.filter(i => !i.isHidden);

    console.log('\n============================================================');
    console.log(`TEST SUMMARY: "dark techno" (First ${items.length} hits)`);
    console.log(`============================================================`);
    console.log(`Total hits evaluated:       ${items.length}`);
    console.log(`Flagged & Hidden as AI:     ${hiddenItems.length} (${((hiddenItems.length / items.length) * 100).toFixed(1)}%)`);
    console.log(`Allowed (Human / Organic):  ${allowedItems.length} (${((allowedItems.length / items.length) * 100).toFixed(1)}%)`);

    if (hiddenItems.length > 0) {
      console.log('\n--- FLAGGED & HIDDEN AI CARDS ---');
      hiddenItems.forEach((item, idx) => {
        console.log(`[🚫 HIDDEN #${idx + 1}]`);
        console.log(`  Title:   ${item.title}`);
        console.log(`  Channel: ${item.channel}`);
        console.log(`  Desc:    ${item.desc.slice(0, 100)}...`);
      });
    } else {
      console.log('\n--- NO CARDS FLAGGED AS AI ---');
    }

    console.log('\n--- SAMPLE OF ALLOWED CARDS (First 15) ---');
    allowedItems.slice(0, 15).forEach((item, idx) => {
      console.log(`[✓ #${idx + 1}] "${item.title.slice(0, 70)}" by ${item.channel}`);
    });

    ws.close();
  } finally {
    proc.kill('SIGKILL');
  }
}

run();
