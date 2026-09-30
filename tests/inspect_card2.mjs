import { spawn } from 'child_process';

const brave = spawn('/usr/bin/brave-browser', [
  '--headless=new',
  '--remote-debugging-port=9227',
  '--load-extension=/home/oh2fxd/toolbox/python/noai',
  '--user-data-dir=/tmp/brave_test_card2',
  'https://www.youtube.com/results?search_query=midjourney+sora+ai+generated+music'
], { stdio: 'ignore' });

setTimeout(async () => {
  try {
    const list = await (await fetch('http://127.0.0.1:9227/json/list')).json();
    const page = list.find(t => t.type === 'page' && t.url.includes('youtube'));
    const ws = new WebSocket(page.webSocketDebuggerUrl);
    await new Promise(r => ws.addEventListener('open', r));

    ws.addEventListener('message', e => {
      const d = JSON.parse(e.data);
      if (d.id === 2) {
        console.log('Full response:', JSON.stringify(d, null, 2));
      }
    });

    ws.send(JSON.stringify({ id: 1, method: 'Runtime.enable' }));

    setTimeout(() => {
      ws.send(JSON.stringify({
        id: 2,
        method: 'Runtime.evaluate',
        params: {
          expression: `(() => {
            const cards = Array.from(document.querySelectorAll('ytd-video-renderer'));
            return {
              count: cards.length,
              titles: cards.map(c => (c.querySelector('#video-title') || {}).textContent?.trim()).filter(Boolean).slice(0, 5)
            };
          })()`,
          returnByValue: true
        }
      }));
    }, 6000);

    setTimeout(() => {
      brave.kill('SIGKILL');
      process.exit(0);
    }, 9000);
  } catch (err) {
    console.error(err);
    brave.kill('SIGKILL');
  }
}, 2000);
