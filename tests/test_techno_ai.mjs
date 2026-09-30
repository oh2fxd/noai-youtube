import { spawn } from 'child_process';

const PORT = 9237;
const PDIR = '/tmp/brave_ai_techno_' + Date.now();
const EXTENSION_DIR = '/home/oh2fxd/toolbox/python/noai';

const proc = spawn('/usr/bin/brave-browser', [
  '--headless=new',
  `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${PDIR}`,
  `--disable-extensions-except=${EXTENSION_DIR}`,
  `--load-extension=${EXTENSION_DIR}`,
  '--no-first-run',
  '--no-default-browser-check',
  '--disable-gpu',
  'https://www.youtube.com/results?search_query=dark+techno+ai'
], { stdio: 'ignore' });

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

setTimeout(async () => {
  try {
    const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
    const page = list.find(t => t.type === 'page');
    const ws = new WebSocket(page.webSocketDebuggerUrl);
    await new Promise(r => ws.addEventListener('open', r));

    ws.send(JSON.stringify({ id: 1, method: 'Runtime.enable' }));
    await sleep(5000);

    ws.addEventListener('message', e => {
      const d = JSON.parse(e.data);
      if (d.id === 50) {
        const res = d.result?.result?.value;
        console.log(`Query "dark techno ai": Found ${res.total} cards, Hidden: ${res.hidden}`);
        res.items.forEach((it, i) => {
          console.log(`  ${i+1}. [${it.hidden ? '🚫 HIDDEN: AI' : '✓ ALLOWED'}] ${it.title}`);
        });
        proc.kill('SIGKILL');
        process.exit(0);
      }
    });

    ws.send(JSON.stringify({
      id: 50,
      method: 'Runtime.evaluate',
      params: {
        expression: `(() => {
          const cards = Array.from(document.querySelectorAll('ytd-video-renderer'));
          return {
            total: cards.length,
            hidden: cards.filter(c => c.classList.contains('noai-hidden')).length,
            items: cards.slice(0, 10).map(c => ({
              title: (c.querySelector('#video-title') || {}).textContent?.trim().replace(/\\s+/g, ' ') || '',
              hidden: c.classList.contains('noai-hidden')
            }))
          };
        })()`,
        returnByValue: true
      }
    }));
  } catch (e) {
    console.error(e);
    proc.kill('SIGKILL');
  }
}, 2000);
