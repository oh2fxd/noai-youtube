import { spawn } from 'child_process';

const PORT = 9243;
const PDIR = '/tmp/brave_test_eval_' + Date.now();
const EXTENSION_DIR = '/home/oh2fxd/toolbox/python/noai';

const brave = spawn('/usr/bin/brave-browser', [
  '--headless=new',
  `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${PDIR}`,
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

    await sleep(6000);

    ws.addEventListener('message', e => {
      const d = JSON.parse(e.data);
      if (d.id === 55) {
        console.log('Results:', JSON.stringify(d.result?.result?.value, null, 2));
        brave.kill('SIGKILL');
        process.exit(0);
      }
    });

    const expr = `
      (() => {
        const regex = /((?:#|\\b)(?:ai|midjourney|suno|sora|elevenlabs)\\b)/i;
        const cards = Array.from(document.querySelectorAll('ytd-video-renderer'));
        return cards.map(c => {
          const titleEl = c.querySelector('#video-title, #video-title-link, h3, a#video-title');
          const descEl = c.querySelector('#description-text, .metadata-snippet-container');
          const text = (titleEl ? titleEl.textContent : '') + ' ' + (descEl ? descEl.textContent : '');
          const match = regex.exec(text);
          return {
            title: titleEl ? titleEl.textContent.trim().replace(/\\s+/g, ' ') : '',
            hasNoAiHidden: c.classList.contains('noai-hidden'),
            matched: match ? match[1] : null
          };
        }).slice(0, 10);
      })()
    `;

    ws.send(JSON.stringify({
      id: 55,
      method: 'Runtime.evaluate',
      params: {
        expression: expr,
        returnByValue: true
      }
    }));
  } catch (err) {
    console.error(err);
    brave.kill('SIGKILL');
  }
}, 2000);
