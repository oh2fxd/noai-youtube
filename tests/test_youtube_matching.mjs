import { spawn } from 'child_process';
import { rmSync, mkdirSync } from 'fs';

const PROFILE_DIR = '/tmp/brave_noai_suite_' + Date.now();
const EXTENSION_DIR = '/home/oh2fxd/toolbox/python/noai';
const PORT = 9233;

try {
  rmSync(PROFILE_DIR, { recursive: true, force: true });
} catch (e) {}
mkdirSync(PROFILE_DIR, { recursive: true });

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

async function testQuery(name, url, port) {
  console.log(`\n============================================================`);
  console.log(`TEST RUN: ${name}`);
  console.log(`Navigating to: ${url}`);

  const pDir = '/tmp/brave_test_' + Math.random().toString(36).slice(2);
  const proc = spawn('/usr/bin/brave-browser', [
    '--headless=new',
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${pDir}`,
    `--load-extension=${EXTENSION_DIR}`,
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-gpu',
    '--window-size=1280,900',
    url
  ], { stdio: 'ignore' });

  try {
    await waitForCdp(port);
    const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
    const pageTarget = list.find(t => t.type === 'page' && t.url.includes('youtube'));
    if (!pageTarget) throw new Error('YouTube page target not found');

    const ws = new WebSocket(pageTarget.webSocketDebuggerUrl);
    await new Promise((res) => ws.addEventListener('open', res));
    await sendCdp(ws, 'Page.enable');
    await sendCdp(ws, 'Runtime.enable');

    console.log('Waiting 6s for YouTube rendering & NoAI extension processing...');
    await sleep(6000);

    const evalRes = await sendCdp(ws, 'Runtime.evaluate', {
      expression: `
        (() => {
          const cards = Array.from(document.querySelectorAll('ytd-video-renderer'));
          const results = cards.map(c => {
            const titleEl = c.querySelector('#video-title, #video-title-link, h3');
            const channelEl = c.querySelector('#channel-name, .ytd-channel-name');
            const isHidden = c.classList.contains('noai-hidden');
            const badge = c.querySelector('.noai-badge');
            return {
              title: titleEl ? titleEl.textContent.trim().replace(/\\s+/g, ' ') : '(no title)',
              channel: channelEl ? channelEl.textContent.trim().replace(/\\s+/g, ' ') : '(unknown channel)',
              isHidden,
              badgeText: badge ? badge.textContent : null
            };
          }).filter(r => r.title !== '(no title)');

          return {
            totalCards: results.length,
            hiddenCount: results.filter(r => r.isHidden).length,
            items: results.slice(0, 10)
          };
        })()
      `,
      returnByValue: true
    });

    const data = evalRes.result?.value;
    if (!data) {
      console.error('Failed to get page evaluation data:', evalRes);
    } else {
      const rate = data.totalCards > 0 ? ((data.hiddenCount / data.totalCards) * 100).toFixed(1) : '0';
      console.log(`\nResults for "${name}":`);
      console.log(`- Total Cards Found:    ${data.totalCards}`);
      console.log(`- Cards Hidden / AI:   ${data.hiddenCount} / ${data.totalCards} (${rate}%)`);
      console.log('\nTop 10 Video Cards Breakdown:');
      data.items.forEach((item, idx) => {
        const status = item.isHidden ? '🚫 [HIDDEN: AI Detected]' : '✓ [ALLOWED: Normal/Human]';
        console.log(`  ${idx + 1}. ${status} ${item.title.slice(0, 65)}...`);
      });
    }

    ws.close();
  } finally {
    proc.kill('SIGKILL');
  }
}

async function runAll() {
  try {
    await testQuery(
      'AI Video & Music Search',
      'https://www.youtube.com/results?search_query=midjourney+sora+ai+generated+music',
      9233
    );

    await testQuery(
      'Control Search (Acoustic Guitar Tutorials)',
      'https://www.youtube.com/results?search_query=acoustic+guitar+fingerstyle+tutorial',
      9234
    );
  } finally {
    console.log('\n============================================================');
    console.log('All tests completed.');
  }
}

runAll();
