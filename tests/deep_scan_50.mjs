import { spawn } from 'child_process';

const PORT = 9236;
const PDIR = '/tmp/brave_dump_50_' + Date.now();

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

    for (let i = 0; i < 9; i++) {
      ws.send(JSON.stringify({ id: 2, method: 'Runtime.evaluate', params: { expression: 'window.scrollBy(0, 3500)' } }));
      await sleep(1500);
    }

    ws.addEventListener('message', e => {
      const d = JSON.parse(e.data);
      if (d.id === 100) {
        const items = d.result?.result?.value || [];
        console.log(`Examining all ${items.length} items for any AI references:`);
        items.forEach((item, idx) => {
          const combined = (item.title + ' ' + item.desc + ' ' + item.channel).toLowerCase();
          const hasAnyAIWord = /\b(ai|artificial|midjourney|suno|sora|cyber|futuristic|generated)\b/i.test(combined);
          if (hasAnyAIWord) {
            const matches = combined.match(/\b(ai|artificial|midjourney|suno|sora|cyber|futuristic|generated)\b/gi);
            console.log(`[Item #${idx + 1}] Found words [${matches.join(', ')}]:`);
            console.log(`  Title: ${item.title}`);
            console.log(`  Desc:  ${item.desc.slice(0, 120)}`);
          }
        });
        proc.kill('SIGKILL');
        process.exit(0);
      }
    });

    ws.send(JSON.stringify({
      id: 100,
      method: 'Runtime.evaluate',
      params: {
        expression: `Array.from(document.querySelectorAll('ytd-video-renderer')).slice(0, 50).map(c => ({
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
    process.exit(1);
  }
}, 2000);
