import { spawn } from 'child_process';

const PORT = 9252;
const PDIR = '/tmp/brave_test_big_badge_' + Date.now();
const EXTENSION_DIR = '/home/oh2fxd/toolbox/python/noai/youtube-noai';

console.log('Testing big AI picture badge & NO-AI block button in Brave...');
const brave = spawn('/usr/bin/brave-browser', [
  '--headless=new',
  `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${PDIR}`,
  `--load-extension=${EXTENSION_DIR}`,
  '--no-first-run',
  '--no-default-browser-check',
  '--disable-gpu',
  'https://www.youtube.com/results?search_query=midjourney+sora+ai+generated+music'
], { stdio: 'ignore' });

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

setTimeout(async () => {
  try {
    const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
    const page = list.find(t => t.type === 'page');
    const ws = new WebSocket(page.webSocketDebuggerUrl);
    await new Promise(r => ws.addEventListener('open', r));
    ws.send(JSON.stringify({ id: 1, method: 'Runtime.enable' }));

    console.log('Waiting 5s for page rendering and badge injection...');
    await sleep(5500);

    ws.addEventListener('message', e => {
      const d = JSON.parse(e.data);
      if (d.id === 25) {
        const res = d.result?.result?.value;
        console.log('\n========================================');
        console.log('BIG BADGE & NO-AI BLOCK LOGO TEST:');
        console.log(`- Total Cards Found:               ${res.total}`);
        console.log(`- Cards with Big AI Picture Badge: ${res.badgeImgCount}`);
        console.log(`- Cards with NO-AI Block Button:   ${res.blockBtnCount}`);
        console.log(`- Cards with Inline Title Pill:    ${res.pillCount}`);
        console.log('\nSample Cards Breakdown:');
        res.samples.forEach((s, idx) => {
          console.log(`  ${idx + 1}. [Badge Picture: ${s.hasBadgeImg ? '✓ YES' : '✗ NO'}] [NO-AI Logo: ${s.hasBlockBtn ? '✓ YES' : '✗ NO'}] "${s.title.slice(0, 55)}..."`);
        });
        brave.kill('SIGKILL');
        process.exit(0);
      }
    });

    ws.send(JSON.stringify({
      id: 25,
      method: 'Runtime.evaluate',
      params: {
        expression: `(() => {
          const cards = Array.from(document.querySelectorAll('ytd-video-renderer'));
          return {
            total: cards.length,
            badgeImgCount: document.querySelectorAll('.noai-badge-img').length,
            blockBtnCount: document.querySelectorAll('.noai-block-btn').length,
            pillCount: document.querySelectorAll('.noai-inline-pill').length,
            samples: cards.slice(0, 6).map(c => ({
              title: (c.querySelector('#video-title') || {}).textContent?.trim() || '',
              hasBadgeImg: !!c.querySelector('.noai-badge-img'),
              hasBlockBtn: !!c.querySelector('.noai-block-btn'),
              hasPill: !!c.querySelector('.noai-inline-pill')
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
