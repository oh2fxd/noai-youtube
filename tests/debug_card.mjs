import { spawn } from 'child_process';

const brave = spawn('/usr/bin/brave-browser', [
  '--headless=new',
  '--remote-debugging-port=9238',
  `--user-data-dir=/tmp/brave_debug_ai_${Date.now()}`,
  '--disable-extensions-except=/home/oh2fxd/toolbox/python/noai',
  '--load-extension=/home/oh2fxd/toolbox/python/noai',
  'https://www.youtube.com/results?search_query=dark+techno+ai'
], { stdio: 'ignore' });

setTimeout(async () => {
  try {
    const list = await (await fetch('http://127.0.0.1:9238/json/list')).json();
    const page = list.find(t => t.type === 'page');
    const ws = new WebSocket(page.webSocketDebuggerUrl);
    await new Promise(r => ws.addEventListener('open', r));

    ws.send(JSON.stringify({ id: 1, method: 'Runtime.enable' }));

    setTimeout(() => {
      ws.addEventListener('message', e => {
        const d = JSON.parse(e.data);
        if (d.id === 20) {
          console.log('Eval:', JSON.stringify(d.result?.result?.value, null, 2));
          brave.kill('SIGKILL');
          process.exit(0);
        }
      });

      ws.send(JSON.stringify({
        id: 20,
        method: 'Runtime.evaluate',
        params: {
          expression: `(() => {
            const cards = Array.from(document.querySelectorAll('ytd-video-renderer'));
            const first = cards[0];
            const title = first ? (first.querySelector('#video-title') || {}).textContent?.trim() : '';
            return {
              title,
              classes: first ? first.className : '',
              hasHiddenClass: first ? first.classList.contains('noai-hidden') : false,
              allClassesInDoc: Array.from(document.querySelectorAll('[class*=noai]')).map(el => el.className)
            };
          })()`,
          returnByValue: true
        }
      }));
    }, 6000);
  } catch (err) {
    console.error(err);
    brave.kill('SIGKILL');
  }
}, 2000);
