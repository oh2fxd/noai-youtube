import { spawn } from 'child_process';
import { rmSync, mkdirSync } from 'fs';

const EXTENSION_DIR = '/home/oh2fxd/toolbox/python/noai';
const PORT = 9245;
const PDIR = '/tmp/brave_test_dt100_' + Date.now();

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
  console.log('1. Launching Brave Browser with NoAI Extension for "dark techno" (Top 100)...');
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
    if (!pageTarget) throw new Error('YouTube page not found in targets');

    const ws = new WebSocket(pageTarget.webSocketDebuggerUrl);
    await new Promise((res) => ws.addEventListener('open', res));
    await sendCdp(ws, 'Page.enable');
    await sendCdp(ws, 'Runtime.enable');

    console.log('2. Waiting for initial page render...');
    await sleep(4000);

    console.log('3. Scrolling down to accumulate at least 100 video cards...');
    for (let scroll = 1; scroll <= 25; scroll++) {
      const countRes = await sendCdp(ws, 'Runtime.evaluate', {
        expression: `document.querySelectorAll('ytd-video-renderer').length`,
        returnByValue: true
      });
      const count = countRes.result?.value || 0;
      console.log(`   [Scroll #${scroll}] Cards loaded: ${count}`);
      if (count >= 105) {
        console.log(`   ✓ Target reached: ${count} cards loaded.`);
        break;
      }

      await sendCdp(ws, 'Runtime.evaluate', {
        expression: `window.scrollBy(0, 4000);`
      });
      await sleep(1800);
    }

    console.log('4. Waiting 4s for DOM observer and keyword engine to finish scanning all cards...');
    await sleep(4000);

    const evalRes = await sendCdp(ws, 'Runtime.evaluate', {
      expression: `
        (() => {
          const cards = Array.from(document.querySelectorAll('ytd-video-renderer'));
          const results = cards.map((c, idx) => {
            const titleEl = c.querySelector('#video-title, #video-title-link, h3');
            const channelEl = c.querySelector('#channel-name, .ytd-channel-name');
            const descEl = c.querySelector('#description-text, .metadata-snippet-container');
            const isHidden = c.classList.contains('noai-hidden');
            const badge = c.querySelector('.noai-badge');
            
            return {
              rank: idx + 1,
              title: titleEl ? titleEl.textContent.trim().replace(/\\s+/g, ' ') : '(no title)',
              channel: channelEl ? channelEl.textContent.trim().replace(/\\s+/g, ' ') : '(unknown channel)',
              desc: descEl ? descEl.textContent.trim().replace(/\\s+/g, ' ') : '',
              isHidden,
              badgeText: badge ? badge.textContent : null
            };
          }).filter(r => r.title !== '(no title)');

          return {
            totalLoaded: results.length,
            top100: results.slice(0, 100)
          };
        })()
      `,
      returnByValue: true
    });

    const data = evalRes.result?.value;
    if (!data) {
      console.error('Could not evaluate cards:', evalRes);
      return;
    }

    const items = data.top100;
    const aiHits = items.filter(i => i.isHidden);
    const humanHits = items.filter(i => !i.isHidden);

    console.log('\n============================================================');
    console.log(`FINAL REPORT: "dark techno" — TOP ${items.length} HITS EVALUATED`);
    console.log(`============================================================`);
    console.log(`Total hits evaluated:       ${items.length}`);
    console.log(`Flagged & Hidden as AI:     ${aiHits.length} (${((aiHits.length / items.length) * 100).toFixed(1)}%)`);
    console.log(`Allowed (Human / Organic):  ${humanHits.length} (${((humanHits.length / items.length) * 100).toFixed(1)}%)`);

    if (aiHits.length > 0) {
      console.log('\n--- DETECTED AI CONTENT (FLAGGED & HIDDEN) ---');
      aiHits.forEach(item => {
        console.log(`[🚫 HIDDEN Rank #${item.rank}] "${item.title}"`);
        console.log(`     Channel: ${item.channel}`);
        console.log(`     Snippet: ${item.desc ? item.desc.slice(0, 90) + '...' : '(none)'}`);
      });
    } else {
      console.log('\nNo items in the first 100 hits contained detectable AI metadata/disclosures.');
    }

    console.log('\n--- SAMPLE OF PRESERVED ORGANIC HITS (Ranks 1 to 20) ---');
    humanHits.slice(0, 20).forEach(item => {
      console.log(`[✓ #${item.rank}] "${item.title.slice(0, 65)}..." by ${item.channel}`);
    });

    ws.close();
  } finally {
    proc.kill('SIGKILL');
  }
}

run();
