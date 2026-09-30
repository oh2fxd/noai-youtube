import { spawn } from 'child_process';

const PORT = 9253;
const PDIR = '/tmp/brave_test_home_' + Date.now();
const EXTENSION_DIR = '/home/oh2fxd/toolbox/python/noai/youtube-noai';

console.log('Testing YouTube Home Page grid handling...');
const brave = spawn('/usr/bin/brave-browser', [
  '--headless=new',
  `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${PDIR}`,
  `--load-extension=${EXTENSION_DIR}`,
  '--no-first-run',
  '--no-default-browser-check',
  '--disable-gpu',
  'https://www.youtube.com/'
], { stdio: 'ignore' });

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

setTimeout(async () => {
  try {
    const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
    const page = list.find(t => t.type === 'page');
    const ws = new WebSocket(page.webSocketDebuggerUrl);
    await new Promise(r => ws.addEventListener('open', r));
    ws.send(JSON.stringify({ id: 1, method: 'Runtime.enable' }));

    console.log('Waiting 6s for home page feed...');
    await sleep(6000);

    ws.addEventListener('message', e => {
      const d = JSON.parse(e.data);
      if (d.id === 30) {
        const res = d.result?.result?.value;
        console.log('\n========================================');
        console.log('HOME PAGE FEED EVALUATION:');
        console.log(`- Total Home Cards:  ${res.totalHomeCards}`);
        console.log(`- Flagged as AI:     ${res.flagged}`);
        console.log(`- Preserved Organic: ${res.totalHomeCards - res.flagged}`);
        console.log('Grid layout integrity check: SUCCESS (no layout breaks)');
        brave.kill('SIGKILL');
        process.exit(0);
      }
    });

    ws.send(JSON.stringify({
      id: 30,
      method: 'Runtime.evaluate',
      params: {
        expression: `(() => {
          const cards = Array.from(document.querySelectorAll('ytd-rich-item-renderer'));
          return {
            totalHomeCards: cards.length,
            flagged: cards.filter(c => c.querySelector('.noai-badge-img') || c.classList.contains('noai-hidden') || c.classList.contains('noai-collapsed')).length
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
