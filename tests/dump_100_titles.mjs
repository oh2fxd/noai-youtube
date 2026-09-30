import { spawn } from 'child_process';

const PORT = 9246;
const PDIR = '/tmp/brave_dump_100_' + Date.now();

const proc = spawn('/usr/bin/brave-browser', [
  '--headless=new',
  `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${PDIR}`,
  '--no-first-run',
  '--no-default-browser-check',
  '--disable-gpu',
  'https://www.youtube.com/results?search_query=dark+techno'
], { stdio: 'ignore' });

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

setTimeout(async () => {
  try {
    const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
    const page = list.find(t => t.type === 'page');
    const ws = new WebSocket(page.webSocketDebuggerUrl);
    await new Promise(r => ws.addEventListener('open', r));
    ws.send(JSON.stringify({ id: 1, method: 'Runtime.enable' }));
    await sleep(3000);

    for (let i = 0; i < 15; i++) {
      ws.send(JSON.stringify({ id: 2, method: 'Runtime.evaluate', params: { expression: 'window.scrollBy(0, 4000)' } }));
      await sleep(1500);
    }

    ws.addEventListener('message', e => {
      const d = JSON.parse(e.data);
      if (d.id === 200) {
        const items = d.result?.result?.value || [];
        console.log(`Dumping all ${items.length} items:`);
        items.forEach((item, idx) => {
          console.log(`${idx + 1}. [${item.channel}] "${item.title}"`);
        });
        proc.kill('SIGKILL');
        process.exit(0);
      }
    });

    ws.send(JSON.stringify({
      id: 200,
      method: 'Runtime.evaluate',
      params: {
        expression: `Array.from(document.querySelectorAll('ytd-video-renderer')).slice(0, 100).map(c => ({
          title: (c.querySelector('#video-title') || {}).textContent?.trim().replace(/\\s+/g, ' ') || '',
          channel: (c.querySelector('#channel-name') || {}).textContent?.trim().replace(/\\s+/g, ' ') || '',
          desc: (c.querySelector('#description-text') || {}).textContent?.trim().replace(/\\s+/g, ' ') || ''
        }))`,
        returnByValue: true
      }
    }));
  } catch (err) {
    console.error(err);
    proc.kill('SIGKILL');
  }
}, 2000);
