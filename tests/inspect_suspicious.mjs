import { spawn } from 'child_process';

const PORT = 9247;
const PDIR = '/tmp/brave_desc_' + Date.now();

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

    for (let i = 0; i < 8; i++) {
      ws.send(JSON.stringify({ id: 2, method: 'Runtime.evaluate', params: { expression: 'window.scrollBy(0, 4000)' } }));
      await sleep(1500);
    }

    ws.addEventListener('message', e => {
      const d = JSON.parse(e.data);
      if (d.id === 300) {
        const items = d.result?.result?.value || [];
        console.log(`Inspecting suspicious channels for AI clues:`);
        items.forEach(it => {
          console.log(`\nChannel: ${it.channel}`);
          console.log(`Title:   ${it.title}`);
          console.log(`Snippet: ${it.snippet}`);
          console.log(`Aria:    ${it.ariaLabel}`);
        });
        proc.kill('SIGKILL');
        process.exit(0);
      }
    });

    ws.send(JSON.stringify({
      id: 300,
      method: 'Runtime.evaluate',
      params: {
        expression: `
          Array.from(document.querySelectorAll('ytd-video-renderer')).filter(c => {
            const ch = (c.querySelector('#channel-name') || {}).textContent || '';
            return /Obsidian|Nocturne|Hypnotic Night|Dark Noir|Techno Void|Digital Pulse/i.test(ch);
          }).slice(0, 6).map(c => ({
            channel: (c.querySelector('#channel-name') || {}).textContent?.trim().replace(/\\s+/g, ' ') || '',
            title: (c.querySelector('#video-title') || {}).textContent?.trim().replace(/\\s+/g, ' ') || '',
            snippet: (c.querySelector('#description-text') || {}).textContent?.trim().replace(/\\s+/g, ' ') || '',
            ariaLabel: (c.querySelector('#video-title') || {}).getAttribute('aria-label') || ''
          }))
        `,
        returnByValue: true
      }
    }));
  } catch (err) {
    console.error(err);
    proc.kill('SIGKILL');
  }
}, 2000);
